import socket
import time


def client_program():
    host = "127.0.0.1"  # server's hostname or IP address
    port = 5000  # port to connect to

    client_socket = socket.socket()
    client_socket.connect((host, port))

    try:
        while True:
            message = "Hello, Server!"
            client_socket.send(message.encode())
            print(f"Sent to server: {message}")
            time.sleep(5)  # wait for 5 seconds before sending the next message
    except KeyboardInterrupt:
        print("Client stopped.")
    finally:
        client_socket.close()


if __name__ == "__main__":
    client_program()
