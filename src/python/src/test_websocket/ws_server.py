import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado.ioloop import PeriodicCallback


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print("WebSocket connection opened")
        WebSocketHandler.connections.add(
            self
        )  # Add the new client to the set of connections

    def on_message(self, message):
        print(f"Received message from client: {message}")
        self.write_message(f"You said: {message}")

    def on_close(self):
        print("WebSocket connection closed")
        WebSocketHandler.connections.remove(
            self
        )  # Remove the client when they disconnect


def push_hello():
    for handler in WebSocketHandler.connections:
        handler.write_message(
            "Hello from server"
        )  # Send a message to each connected client


WebSocketHandler.connections = set()


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

    # Every second, push messages to connected clients
    callback = PeriodicCallback(push_hello, 1000)
    callback.start()

    tornado.ioloop.IOLoop.current().start()
