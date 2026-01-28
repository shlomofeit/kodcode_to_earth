from space_network_lib import *


class Satellite(SpaceEntity):
    def __init__(self, name, distance_from_earth):
        super().__init__(name, distance_from_earth)

    def receive_signal(self, packet: Packet):
        if isinstance(packet, RelayPacket):
            inner_packet = packet.packet_to_relay
            print(f"Unwrapping and forwarding to {inner_packet.receiver}")
            inner_packet.sender = packet.receiver
            packet_send_smart(inner_packet)

        else:
            print(f"Final destination reached: {packet.data}")
        print(f"[{self.name}] Received: {packet}")


class RelayPacket(Packet):
    def __init__(self, packet_to_relay, sender, proxy):
        super().__init__(packet_to_relay, sender, proxy)
        self.packet_to_relay: Packet = packet_to_relay
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
        if Satellites_list.index(packet.sender) < Satellites_list.index(packet.receiver):
            proxy = Satellites_list.index(packet.sender) + 1
        else:
            proxy = Satellites_list.index(packet.sender) - 1
        print("Target out of range.")
        print("XXX")
        p_earth_to_sat1 = RelayPacket(packet, packet.sender, Satellites_list[proxy])
    #     # if isinstance(final_p.data, RelayPacket):
        print(f">> From {packet.sender} To {Satellites_list[proxy]}")
        packet_send_smart(p_earth_to_sat1)


network_manage = SpaceNetwork(7)

Sat1 = Satellite("satellite1", 100)
Sat2 = Satellite("satellite2", 200)
Sat3 = Satellite("satellite3", 300)
Sat4 = Satellite("satellite4", 400)
Sat5 = Satellite("satellite5", 500)
Earth = Satellite("Earth", 0)
Satellites_list = [Earth, Sat1, Sat2, Sat3, Sat4, Sat5]

message1 = Packet("Hi there", Sat1, Sat2)
final_p = Packet("Hello from Earth", Sat1, Sat4)

try:
    packet_send_smart(final_p)
except BrokenConnectionError:
    print("failed Transmission")