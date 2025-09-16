#include <stdio.h>
#include <stdlib.h>
#include <dlfcn.h>
#include <dirent.h>
#include <string.h>
#include <limits.h>
#include "plugin_interface.h"

typedef struct plugin_node {
    void *handle;
    plugin_info_t *info;
    struct plugin_node *next;
} plugin_node_t;

plugin_node_t *plugins = NULL;

void load_plugin(const char *path) {
    void *handle = dlopen(path, RTLD_LAZY);
    if (!handle) {
        fprintf(stderr, "Cannot load plugin %s: %s\n", path, dlerror());
        return;
    }

    plugin_info_t *info = dlsym(handle, "plugin_info");
    if (!info) {
        fprintf(stderr, "Plugin %s has no plugin_info: %s\n", path, dlerror());
        dlclose(handle);
        return;
    }

    // 初始化插件
    if (info->initialize && info->initialize() != 0) {
        fprintf(stderr, "Plugin %s initialization failed\n", path);
        dlclose(handle);
        return;
    }

    // 添加到插件列表
    plugin_node_t *node = malloc(sizeof(plugin_node_t));
    node->handle = handle;
    node->info = info;
    node->next = plugins;
    plugins = node;

    printf("Loaded plugin: %s (version %s)\n", info->name, info->version);
}

void load_all_plugins(const char *dir) {
    DIR *d = opendir(dir);
    if (!d) {
        printf("Cannot open plugin directory: %s\n", dir);
        return;
    }

    struct dirent *entry;
    while ((entry = readdir(d)) != NULL) {
        if (strstr(entry->d_name, ".so")) {
            char path[PATH_MAX];
            snprintf(path, sizeof(path), "%s/%s", dir, entry->d_name);
            load_plugin(path);
        }
    }
    closedir(d);
}

void execute_all_plugins(const char *args) {
    plugin_node_t *node = plugins;
    while (node) {
        if (node->info->execute) {
            node->info->execute(args);
        }
        node = node->next;
    }
}

void unload_all_plugins() {
    plugin_node_t *node = plugins;
    while (node) {
        plugin_node_t *next = node->next;
        if (node->info->cleanup) {
            node->info->cleanup();
        }
        dlclose(node->handle);
        free(node);
        node = next;
    }
    plugins = NULL;
}

int main() {
    printf("=== Plugin System Demo ===\n");

    // 載入所有插件
    load_all_plugins("./plugins");

    // 執行插件
    execute_all_plugins("test arguments");

    // 卸載插件
    unload_all_plugins();

    return 0;
}