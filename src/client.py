import socket
import json
import time
import sys

class Client:
    def __init__(self):
        # [cite_start]Maps Layer IDs to target node ports [cite: 32, 40]
        # Layer 0 (Core) = A1, A2, A3
        # Layer 1 = B1, B2
        # Layer 2 = C1, C2
        self.layer_map = {
            0: [5001, 5002, 5003],
            1: [6001, 6002],
            2: [7001, 7002]
        }

    def send_transaction(self, transaction_line):
        """
        Parses a transaction line and sends it to the correct node.
        Format examples:
        - Write: "12 49.53 2" (Float value = Write -> Always Core)
        - Read:  "30 49 1"    (Integer value = Read  -> Specific Layer)
        """
        parts = transaction_line.strip().split()
        if len(parts) < 3:
            print(f"[Client] Invalid format: {transaction_line}")
            return

        try:
            # Parse components
            val_str = parts[1]
            layer_id_requested = int(parts[2])
            
            # Determine if Write (Not read-only) or Read
            # [cite_start]Heuristic: The exercise implies floats are updates (49.53) [cite: 41]
            is_write = '.' in val_str 
            
            command = "CLIENT_UPDATE" if is_write else "READ_REQUEST"
            payload = transaction_line
            
            # Routing Rule: 
            # [cite_start]Writes ALWAYS go to Core (Layer 0), regardless of the requested layer [cite: 41-43].
            # [cite_start]Reads go to the specified layer [cite: 38-39].
            target_layer = 0 if is_write else layer_id_requested
            
            self.connect_and_send(target_layer, command, payload)
            
        except ValueError:
            print(f"[Client] Error parsing numbers in: {transaction_line}")

    def connect_and_send(self, layer_id, command, payload):
        """
        Attempts to connect to nodes in the target layer until one succeeds.
        """
        possible_ports = self.layer_map.get(layer_id, [])
        
        for port in possible_ports:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(2) # Prevent hanging if node is down
                s.connect(('localhost', port))
                
                msg = {"command": command, "payload": payload}
                s.send(json.dumps(msg).encode())
                
                response = s.recv(1024).decode()
                print(f"[{'WRITE' if command == 'CLIENT_UPDATE' else 'READ'}] Sent to Port {port} | Response: {response}")
                s.close()
                return # Success
            except (ConnectionRefusedError, socket.timeout):
                continue # Try next node in the list
        
        print(f"[Client] Failed to connect to any node in Layer {layer_id}")

    def run_interactive(self):
        print("\n--- Distributed System Client ---")
        print("Enter transaction (e.g. '12 49.53 2' for write, '30 49 1' for read)")
        print("Type 'file <filename>' to load a batch. Type 'exit' to quit.\n")
        
        while True:
            user_input = input(">> ").strip()
            if user_input.lower() == 'exit':
                break
            elif user_input.lower().startswith('file '):
                filename = user_input.split()[1]
                self.process_file(filename)
            else:
                self.send_transaction(user_input)

    def process_file(self, filename):
        try:
            with open(filename, 'r') as f:
                print(f"[Client] Processing batch file: {filename}")
                for line in f:
                    if line.strip():
                        print(f"Processing: {line.strip()}")
                        self.send_transaction(line)
                        time.sleep(0.5) # Small delay for readability
        except FileNotFoundError:
            print("[Client] File not found.")

if __name__ == "__main__":
    client = Client()
    client.run_interactive()