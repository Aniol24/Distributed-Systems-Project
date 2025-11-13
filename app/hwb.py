# hwb.py
import socket
import sys

def send_to_screen(message, host="127.0.0.1", port=6000):
    """Send a debug message to the screen server."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.sendall((message + "\n").encode("utf-8"))
    finally:
        s.close()

def start_client(host='127.0.0.1', port=65432):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect((host, port))
        #send_to_screen(f"[HWB] Connected to server at {host}:{port}")

        message = "Hello from client!"
        client_socket.sendall(message.encode())
        #send_to_screen(f"[HWB] Sent: {message}")

        data = client_socket.recv(1024)
        if data:
            #send_to_screen(f"[HWB] Received: {data.decode()}")
            pass

    finally:
        client_socket.close()
        #send_to_screen("[HWB] Connection closed")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <port>")
        sys.exit(1)

    port = int(sys.argv[1])
    start_client(port=port)
