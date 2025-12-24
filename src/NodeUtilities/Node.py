import socket
import threading
import json
import time

class Node:
    """
    Base Node class that handles all networking and storage.
    """
    def __init__(self, node_id, port, neighbors, layer_type):
        self.node_id = node_id
        self.port = port
        self.neighbors = neighbors
        self.layer_type = layer_type
        
        # State
        self.data_log = []
        self.update_counter = 0
        self.running = True
        
        # File Persistence
        self.log_filename = f"{self.node_id}_log.txt"
        open(self.log_filename, 'w').close() # Clear on startup

        # START THE SERVER
        # We run this in a daemon thread so it doesn't block the main program
        threading.Thread(target=self.start_server, daemon=True).start()

    # ---------------------------------------------------------
    # NETWORKING (This was missing!)
    # ---------------------------------------------------------
    def start_server(self):
        """Initializes TCP socket and listens for connections."""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Allow reusing the port immediately if we restart quickly
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('localhost', self.port))
            self.server_socket.listen(5)
            print(f"[{self.node_id}] Server listening on port {self.port}...")
            
            while self.running:
                client, addr = self.server_socket.accept()
                threading.Thread(target=self.handle_message, args=(client,)).start()
                
        except Exception as e:
            print(f"[{self.node_id}] Server Error: {e}")

    def handle_message(self, client_socket):
        """Routes incoming JSON messages to the correct handler."""
        try:
            raw_data = client_socket.recv(4096).decode()
            if not raw_data: return
            
            msg = json.loads(raw_data)
            command = msg.get('command')
            payload = msg.get('payload')

            if command == 'CLIENT_UPDATE':
                # Core Layer Write
                self.handle_client_update(payload, client_socket)
            elif command == 'REPLICATE_ACTIVE':
                # Core-to-Core replication
                self.handle_active_replication(payload, client_socket)
            elif command == 'SYNC_PASSIVE':
                # Layer 1/2 Sync
                self.handle_passive_sync(payload)
                client_socket.close() # No response needed for passive sync
            elif command == 'READ_REQUEST':
                # Simple read handling
                response = json.dumps(self.data_log)
                client_socket.send(response.encode())
                client_socket.close()

        except Exception as e:
            print(f"[{self.node_id}] Message Error: {e}")
            client_socket.close()

    def send_message(self, target_port, command, payload, wait_for_ack=False):
        """Helper to send JSON to another node."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(('localhost', target_port))
            
            msg = json.dumps({"command": command, "payload": payload})
            s.send(msg.encode())
            
            if wait_for_ack:
                # Wait for response (used by Eager Replication)
                response = s.recv(1024).decode()
                s.close()
                return response == "ACK" or response == "SUCCESS"
            
            s.close()
            return True
        except ConnectionRefusedError:
            # This is expected if a node is down or busy
            # print(f"[{self.node_id}] Connection refused to port {target_port}")
            return False
        except Exception as e:
            print(f"[{self.node_id}] Send Error: {e}")
            return False

    # ---------------------------------------------------------
    # DEFAULT HANDLERS (Overridden by Subclasses)
    # ---------------------------------------------------------
    def handle_client_update(self, data, client_socket):
        client_socket.send(b"ERROR: This node cannot accept updates.")
        client_socket.close()

    def handle_active_replication(self, data, client_socket):
        client_socket.close()

    def handle_passive_sync(self, received_log):
        self.data_log = received_log
        self.save_to_file()
    
    def save_to_file(self):
        with open(self.log_filename, 'w') as f:
            for line in self.data_log:
                f.write(f"{line}\n")
    
    # Empty hooks for subclasses
    def check_layer1_threshold(self): pass
    def run_layer2_timer(self): pass