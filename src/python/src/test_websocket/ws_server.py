import tornado.ioloop
import tornado.web
import tornado.websocket


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print("WebSocket connection opened")

    def on_message(self, message):
        print(f"Received message from client: {message}")
        self.write_message(f"You said: {message}")

    def on_close(self):
        print("WebSocket connection closed")


def make_app():
    return tornado.web.Application(
        [
            (r"/websocket", WebSocketHandler),
        ]
    )


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    print("WebSocket server is running on port 8888")
    tornado.ioloop.IOLoop.current().start()
