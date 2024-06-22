import socket


def server_program():
    host = "127.0.0.1"  # localhost
    port = 5000  # port to listen on

    server_socket = socket.socket()
    server_socket.bind((host, port))
    server_socket.listen(2)
    conn, address = server_socket.accept()
    print(f"Connection from: {address}")

    while True:
        data = conn.recv(1024).decode()
        if not data:
            break
        print(f"Received from client: {data}")
        data = input("Enter response: ")
        conn.send(data.encode())

    conn.close()


if __name__ == "__main__":
    server_program()
