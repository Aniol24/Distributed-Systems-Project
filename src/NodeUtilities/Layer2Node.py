from .Node import Node

class Layer2Node(Node):
    def __init__(self, node_id, port, neighbors):
        # Initialize as "LAYER2"
        # Neighbors are likely empty or irrelevant for propagation, but kept for structure
        super().__init__(node_id, port, neighbors, layer_type="LAYER2")

    def handle_passive_sync(self, received_log):
        """
        Passive Replication (Incoming):
        Received from Parent (B2 -> C1 or B2 -> C2).
        Triggered by B2's 10-second timer.
        """
        # Overwrite local log with the update received from B2
        self.data_log = received_log
        self.save_to_file()
        print(f"[{self.node_id}] Passive Sync Received from Layer 1. Current Version Count: {len(self.data_log)}")

    def handle_client_update(self, data, client_socket):
        """
        Layer 2 nodes are read-heavy and hold the oldest versions[cite: 14].
        They cannot process writes/updates directly.
        """
        # Reject write requests
        client_socket.send(b"ERROR: Layer 2 is Read-Only for updates. Connect to Core.")