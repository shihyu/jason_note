import socket


def client_program():
    host = "127.0.0.1"  # localhost
    port = 5000  # port to connect to

    client_socket = socket.socket()
    client_socket.connect((host, port))

    message = input("Enter message to send: ")

    while message.lower().strip() != "bye":
        client_socket.send(message.encode())
        data = client_socket.recv(1024).decode()
        print(f"Received from server: {data}")
        message = input("Enter message to send: ")

    client_socket.close()


if __name__ == "__main__":
    client_program()
