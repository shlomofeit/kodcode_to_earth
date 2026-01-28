from space_network_lib import *


class Satellite(SpaceEntity):
    def __init__(self, name, distance_from_earth):
        super().__init__(name, distance_from_earth)

    def receive_signal(self, packet: Packet):
        # if isinstance(packet, RelayPacket):
        #     # print(f">>>{packet} is RelayPacket")
        #     inner_packet = packet.data
        #     print(f"Unwrapping and forwarding to {inner_packet.receiver}")
        #     transmission_attempt(packet.packet_to_relay)
        # else:
        print(f"Final destination reached: {packet.data}")
        print(f"[{self.name}] Received: {packet}")


class RelayPacket(Packet):
    def __init__(self, packet_to_relay, sender, proxy):
        super().__init__(packet_to_relay, sender, proxy)
        self.packet_to_relay = packet_to_relay
        self.sender = sender
        self.proxy = proxy

    def __repr__(self):
        return f"RelayPacket(Relaying [{self.data}] to {self.receiver} from {self.sender})"


def transmission_attempt(packet: Packet):
    try:
        network_manage.send(packet)
    except TemporalInterferenceError:
        print("Interference, waiting...")
        time.sleep(0.3)
        transmission_attempt(packet)
    except DataCorruptedError:
        print("Data corrupted, retrying...")
        transmission_attempt(packet)
    except LinkTerminatedError:
        print("Link lost.")
        raise BrokenConnectionError("Link lost.")
    # except OutOfRangeError:
    #     print("Target out of range.")
    #     raise BrokenConnectionError("Target out of range.")


def packet_send_smart(packet: Packet):
    try:
        if isinstance(packet, RelayPacket):
            packet_send_smart(packet.packet_to_relay)
        else:
            transmission_attempt(packet)
    except OutOfRangeError:
        print("XXX")
        proxy = Satellites_list.index(packet.sender)
        p_earth_to_sat1 = RelayPacket(packet, packet.sender, Satellites_list[proxy + 1])
        # if isinstance(final_p.data, RelayPacket):
        print(f">>>{packet} is RelayPacket")
        inner_packet1 = packet
        print(f"Unwrapping and forwarding to {inner_packet1.receiver}")
        # transmission_attempt(p_earth_to_sat1.packet_to_relay)
        packet_send_smart(p_earth_to_sat1)


network_manage = SpaceNetwork(6)

Sat1 = Satellite("satellite1", 100)
Sat2 = Satellite("satellite2", 200)
Sat3 = Satellite("satellite3", 300)
Sat4 = Satellite("satellite4", 400)
Sat5 = Satellite("satellite5", 500)
Earth = Satellite("Earth", 0)
Satellites_list = [Earth, Sat1, Sat2, Sat3, Sat4, Sat5]

message1 = Packet("Hi there", Sat1, Sat2)
final_p = Packet("Hello from Earth", Sat1, Sat3)
# p_earth_to_sat1 = RelayPacket(final_p, Earth, Sat1)
# proxy1 = RelayPacket(p_earth_to_sat1, Sat1, Sat2)
# proxy2 = RelayPacket(proxy1, Sat2, Sat3)
# proxy3 = RelayPacket(proxy2, Sat3, Sat4)
# proxy4 = RelayPacket(proxy3, Sat4, Sat5)


# try:
#     transmission_attempt(message1)
# except BrokenConnectionError:
#     print("failed Transmission")

# try:
#     transmission_attempt(proxy4)
# except BrokenConnectionError:
#     print("failed Transmission")

try:
    packet_send_smart(final_p)
# except OutOfRangeError:
#     print("XXX")
#     proxy = Satellites_list.index(final_p.sender)
#     p_earth_to_sat1 = RelayPacket(final_p, final_p.sender, Satellites_list[proxy + 1])
#     # if isinstance(final_p.data, RelayPacket):
#     print(f">>>{final_p} is RelayPacket")
#     inner_packet1 = final_p
#     print(f"Unwrapping and forwarding to {inner_packet1.receiver}")
#     # transmission_attempt(p_earth_to_sat1.packet_to_relay)
#     packet_send_smart(p_earth_to_sat1)
except BrokenConnectionError:
    print("failed Transmission")