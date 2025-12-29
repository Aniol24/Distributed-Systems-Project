# screen_server.py
import socket

def run_screen_server(port=6000):
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", port))
    srv.listen(10)
    print("[SCREEN] Server started")
    while True:
        conn, _ = srv.accept()
        line = conn.makefile("rb").readline()
        print(line.decode("utf-8").strip())
        conn.close()

if __name__ == "__main__":
    run_screen_server()
