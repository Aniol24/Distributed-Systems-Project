from .Node import Node
import threading

class CoreNode(Node):
    def __init__(self, node_id, port, neighbors):
        # Initialize base node with "CORE" type
        super().__init__(node_id, port, neighbors, layer_type="CORE")
        self.lock = threading.Lock() # Required for Eager replication consistency

    def handle_client_update(self, data, client_socket):
        """
        Requirements: Update Everywhere, Active, Eager.
        1. Receive update.
        2. Broadcast to all other Core nodes (Active).
        3. Wait for ACKs from all of them (Eager).
        4. Commit only if all ACK.
        """
        print(f"[{self.node_id}] Coordinating Write: {data}")
        
        # Identify peer Core nodes (A1, A2, A3)
        core_peers = [nid for nid in self.neighbors if nid.startswith("A")]
        acks_received = 0
        
        # Critical Section: Lock to ensure atomic transaction processing
        with self.lock:
            # Step 1: Active Replication - Broadcast to peers
            success_count = 0
            for peer_id in core_peers:
                peer_port = self.neighbors[peer_id]
                # Send message and wait for "ACK" response (Eager)
                if self.send_message(peer_port, "REPLICATE_ACTIVE", data, wait_for_ack=True):
                    success_count += 1
            
            # Step 2: Check Eager Condition
            # We only commit if ALL peers acknowledged
            if success_count == len(core_peers):
                self.commit_data(data)
                client_socket.send(b"SUCCESS")
                print(f"[{self.node_id}] Write Successful. Committed.")
            else:
                # In a real system, you would rollback here.
                client_socket.send(b"ERROR: Eager Replication Failed")
                print(f"[{self.node_id}] Write Failed. Peer missing.")

    def handle_active_replication(self, data, client_socket):
        """
        Handle incoming broadcast from another Core node.
        Requirement: Commit immediately and ACK.
        """
        with self.lock:
            self.commit_data(data)
            client_socket.send(b"ACK")

    def commit_data(self, data):
        """
        Overrides/Extends base commit to include Layer 1 triggers.
        """
        # 1. Save to local log and file
        self.data_log.append(data)
        self.save_to_file()
        
        # 2. Check Layer 1 Propagation Trigger (Lazy - Every 10 Updates)
        # Only A2 and A3 have children in Layer 1
        if self.node_id in ["A2", "A3"]:
            self.check_layer1_threshold()

    def check_layer1_threshold(self):
        """
        Requirement: Nodes B1 and B2 receive data every 10 updates.
        A2 -> B1
        A3 -> B2
        """
        self.update_counter += 1
        
        if self.update_counter % 10 == 0:
            target_node = "B1" if self.node_id == "A2" else "B2"
            target_port = self.neighbors.get(target_node)
            
            if target_port:
                print(f"[{self.node_id}] Trigger: 10th Update. Propagating to {target_node}...")
                # Passive Replication: Send the whole state (self.data_log)
                self.send_message(target_port, "SYNC_PASSIVE", self.data_log)