from .Node import Node
import time
import threading

class Layer1Node(Node):
    def __init__(self, node_id, port, neighbors):
        # Initialize as "LAYER1"
        super().__init__(node_id, port, neighbors, layer_type="LAYER1")
        
        # Requirement 4: Nodes C1/C2 receive data every 10 seconds.
        # This responsibility falls on B2, the parent of Layer 2.
        if self.node_id == "B2":
            # Start a background thread specifically for this timer
            threading.Thread(target=self.run_layer2_timer, daemon=True).start()

    def handle_passive_sync(self, received_log):
        """
        Passive Replication (Incoming):
        Received from Parent (A2 -> B1 or A3 -> B2).
        Action: Replace local state with the authoritative parent state.
        """
        # In a simple passive model, we overwrite or extend our log
        self.data_log = received_log
        self.save_to_file()
        print(f"[{self.node_id}] Passive Sync Received. Log size: {len(self.data_log)}")

    def run_layer2_timer(self):
        """
        Requirement: "Nodes C1 and C2 receive the data every 10 seconds".
        This runs only on Node B2.
        """
        print(f"[{self.node_id}] 10-second timer started for Layer 2 propagation.")
        
        while self.running:
            # Wait for 10 seconds (Lazy Replication)
            time.sleep(10)
            
            # If we have data, propagate it to C1 and C2
            if self.data_log:
                print(f"[{self.node_id}] Timer Hit (10s). Propagating to C1 and C2...")
                
                # Identify Layer 2 children
                layer2_children = ["C1", "C2"]
                
                for child_id in layer2_children:
                    port = self.neighbors.get(child_id)
                    if port:
                        # Send the entire log (Passive Replication)
                        self.send_message(port, "SYNC_PASSIVE", self.data_log)