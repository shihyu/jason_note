import socket


def server_program():
    host = "127.0.0.1"  # localhost
    port = 5000  # port to listen on

    server_socket = socket.socket()
    server_socket.bind((host, port))
    server_socket.listen(1)
    server_socket.settimeout(10)  # set a timeout of 10 seconds for accept()

    print(f"Server listening on {host}:{port}")

    while True:
        try:
            conn, address = server_socket.accept()
            print(f"Connection from: {address}")

            conn.settimeout(
                10
            )  # set a timeout for receive operations on this connection

            while True:
                try:
                    data = conn.recv(1024).decode()
                    if not data:
                        print(f"Connection closed by client: {address}")
                        break
                    print(f"Received from client: {data}")
                except socket.timeout:
                    print("hello")
                    continue

            conn.close()
            print("Waiting for new connection...")

        except socket.timeout:
            print("No incoming connections in the last 10 seconds.")


if __name__ == "__main__":
    server_program()
