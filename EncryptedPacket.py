from space_network_lib import Packet


class EncryptedPacket(Packet):
    def __init__(self, data, sender, receiver, key):
        self.key = key.encode() if isinstance(key, str) else key
        b_data = data.encode() if isinstance(data, str) else data
        self.data = self.decrypt_key(b"RRR" + b_data, self.key)
        super().__init__(self.data, sender, receiver)

    def  decrypt_key(self, n_data, n_key):
        self.n_data = n_data.encode() if isinstance(n_data, str) else n_data
        self.n_key = n_key.encode() if isinstance(n_key, str) else n_key
        if len(self.n_key) < len(self.n_data):
            self.n_key = self.n_key * (len(self.n_data) // len(self.n_key) + 1)
            self.n_key = self.n_key[:len(self.n_data)]

        return bytes([x ^ y for x, y in zip(self.n_data, self.n_key)])