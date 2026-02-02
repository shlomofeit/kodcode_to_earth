from space_network_lib import *
from EncryptedPacket import EncryptedPacket

class SecurityBreachError(Exception):
    pass

class Satellite(SpaceEntity):
    Satellites_list = []
    def __init__(self, name, distance_from_earth):
        super().__init__(name, distance_from_earth)
        self.key = "".join(chr(random.randint(65, 90)) for n in range(10))
        Satellite.Satellites_list.append(self)

    def receive_signal(self, packet: Packet):
        if isinstance(packet, RelayPacket):
            inner_packet = packet.packet_to_relay
            print(f"Unwrapping and forwarding to {inner_packet.receiver}")
            inner_packet.sender = packet.receiver
            packet_send_smart(inner_packet)

        else:
            encrypted = EncryptedPacket.decrypt_key(self, packet.data, self.key).decode()
            if encrypted.startswith("RRR"):
                print(f"Final destination reached: {encrypted[3:]}")
            else:
                raise SecurityBreachError("")
        print(f"[{self.name}] Received: {packet}")


class RelayPacket(Packet):
    def __init__(self, packet_to_relay, sender, proxy):
        super().__init__(packet_to_relay, sender, proxy)
        self.packet_to_relay: EncryptedPacket = packet_to_relay
        self.sender = sender
        self.proxy = proxy

    def __repr__(self):
        return f"RelayPacket(Relaying [{self.data}] to {self.receiver} from {self.sender})"


def packet_send_smart(packet: Packet):
    try:
        network_manage.send(packet)
    except TemporalInterferenceError:
        print("Interference, waiting...")
        time.sleep(0.3)
        packet_send_smart(packet)
    except DataCorruptedError:
        print("Data corrupted, retrying...")
        packet_send_smart(packet)
    except LinkTerminatedError:
        print("Link lost.")
        raise BrokenConnectionError("Link lost.")
    except OutOfRangeError:
        if Satellite.Satellites_list.index(packet.sender) < Satellite.Satellites_list.index(packet.receiver):
            proxy = Satellite.Satellites_list.index(packet.sender) + 1
        else:
            proxy = Satellite.Satellites_list.index(packet.sender) - 1
        print("Target out of range.")
        print("XXX")
        p_earth_to_sat1 = RelayPacket(packet, packet.sender, Satellite.Satellites_list[proxy])
    #     # if isinstance(final_p.data, RelayPacket):
        print(f">> From {packet.sender} To {Satellite.Satellites_list[proxy]}")
        packet_send_smart(p_earth_to_sat1)


network_manage = SpaceNetwork(7)
Sat1 = Satellite("satellite1", 100)
Sat2 = Satellite("satellite2", 200)
Sat3 = Satellite("satellite3", 300)
Sat4 = Satellite("satellite4", 400)
Sat5 = Satellite("satellite5", 500)
Earth = Satellite("Earth", 0)

message1 = EncryptedPacket("Hi there", Sat1, Sat2, Sat4.key)
final_p = EncryptedPacket("Hello from Earth", Sat1, Sat4, Sat4.key)

try:
    packet_send_smart(final_p)
except BrokenConnectionError:
    print("failed Transmission")