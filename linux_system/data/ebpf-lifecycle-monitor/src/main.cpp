#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <unistd.h>
#include <time.h>
#include <vector>
#include <string>
#include <iostream>
#include <memory>
#include <functional>
#include <algorithm>

#include <bpf/libbpf.h>
#include "monitor.h"
#include "monitor.skel.h"
#include "mongoose.h"

// 全域停止標誌
static volatile bool stop = false;

void sig_handler(int sig) {
    stop = true;
}

// 簡單的 JSON 轉義函數
std::string escape_json_string(const char* input) {
    std::string output;
    for (int i = 0; input[i] != '\0'; i++) {
        switch (input[i]) {
            case '"': output += "\\\""; break;
            case '\\': output += "\\\\"; break;
            case '\b': output += "\\b"; break;
            case '\f': output += "\\f"; break;
            case '\n': output += "\\n"; break;
            case '\r': output += "\\r"; break;
            case '\t': output += "\\t"; break;
            default: output += input[i];
        }
    }
    return output;
}

// --- WebSocket Server ---
class WebServer {
public:
    WebServer(const char* listening_address) {
        mg_mgr_init(&mgr);
        if (mg_http_listen(&mgr, listening_address, event_handler, this) == NULL) {
            throw std::runtime_error("Failed to listen on address: " + std::string(listening_address));
        }
    }

    ~WebServer() {
        mg_mgr_free(&mgr);
    }

    void poll(int timeout_ms) {
        mg_mgr_poll(&mgr, timeout_ms);
    }

    void broadcast(const std::string& message) {
        for (struct mg_connection* c : clients) {
            mg_ws_send(c, message.c_str(), message.length(), WEBSOCKET_OP_TEXT);
        }
    }

private:
    struct mg_mgr mgr;
    std::vector<struct mg_connection*> clients;

    static void event_handler(struct mg_connection* c, int ev, void* ev_data) {
        WebServer* server = static_cast<WebServer*>(c->fn_data);
        if (ev == MG_EV_WS_OPEN) {
            printf("New WS connection\n");
            server->clients.push_back(c);
        } else if (ev == MG_EV_CLOSE) {
            auto& clients = server->clients;
            clients.erase(std::remove(clients.begin(), clients.end(), c), clients.end());
        } else if (ev == MG_EV_HTTP_MSG) {
            struct mg_http_message* hm = (struct mg_http_message*)ev_data;
            if (mg_match(hm->uri, mg_str("/ws"), NULL)) {
                mg_ws_upgrade(c, hm, NULL);
            } else {
                mg_http_reply(c, 200, "", "eBPF Lifecycle Monitor is Running\n");
            }
        }
    }
};

// --- BPF Manager ---
class BPFManager {
public:
    using EventHandler = std::function<void(const struct event*)>;

    BPFManager(EventHandler handler) : handler_(handler) {
        // 設定錯誤輸出
        libbpf_set_print([](enum libbpf_print_level level, const char* format, va_list args) {
            return vfprintf(stderr, format, args);
        });

        // 1. Open
        skel_ = monitor_bpf__open();
        if (!skel_) throw std::runtime_error("Failed to open BPF skeleton");

        // 2. Load
        if (monitor_bpf__load(skel_)) {
            monitor_bpf__destroy(skel_);
            throw std::runtime_error("Failed to load BPF skeleton");
        }

        // 3. Attach
        if (monitor_bpf__attach(skel_)) {
            monitor_bpf__destroy(skel_);
            throw std::runtime_error("Failed to attach BPF skeleton");
        }

        // 4. Ring Buffer
        rb_ = ring_buffer__new(bpf_map__fd(skel_->maps.events), ring_buffer_callback, this, NULL);
        if (!rb_) {
            monitor_bpf__destroy(skel_);
            throw std::runtime_error("Failed to create ring buffer");
        }
    }

    ~BPFManager() {
        if (rb_) ring_buffer__free(rb_);
        if (skel_) monitor_bpf__destroy(skel_);
    }

    void poll(int timeout_ms) {
        ring_buffer__poll(rb_, timeout_ms);
    }

private:
    struct monitor_bpf* skel_ = nullptr;
    struct ring_buffer* rb_ = nullptr;
    EventHandler handler_;

    static int ring_buffer_callback(void* ctx, void* data, size_t data_sz) {
        BPFManager* manager = static_cast<BPFManager*>(ctx);
        const struct event* e = (const struct event*)data;
        if (manager->handler_) {
            manager->handler_(e);
        }
        return 0;
    }
};

// --- Main ---

int main(int argc, char** argv) {
    signal(SIGINT, sig_handler);
    signal(SIGTERM, sig_handler);

    try {
        WebServer web_server("http://0.0.0.0:8080");
        printf("Web Server started at http://localhost:8080/ws\n");

        BPFManager bpf_manager([&web_server](const struct event* e) {
            std::string type_str = "UNKNOWN";
            if (e->type == EVENT_PROCESS_EXEC) type_str = "EXEC";
            else if (e->type == EVENT_PROCESS_EXIT) type_str = "EXIT";
            else if (e->type == EVENT_OOM_KILL) type_str = "OOM";

            char buffer[512];
            snprintf(buffer, sizeof(buffer),
                     "{\"timestamp\": %llu, \"pid\": %d, \"ppid\": %d, \"comm\": \"%s\", \"type\": \"%s\", \"exit_code\": %d, \"target_pid\": %d}",
                     e->timestamp, e->pid, e->ppid, escape_json_string(e->comm).c_str(), type_str.c_str(), e->exit_code, e->target_pid);

            std::string json(buffer);
            printf("%s\n", json.c_str());
            web_server.broadcast(json);
        });

        printf("eBPF Monitoring started...\n");

        while (!stop) {
            bpf_manager.poll(10); // Poll BPF events
            web_server.poll(0);   // Poll Web events
        }

    } catch (const std::exception& e) {
        fprintf(stderr, "Error: %s\n", e.what());
        return 1;
    }

    printf("Exiting...\n");
    return 0;
}