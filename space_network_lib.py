import time
from abc import ABC, abstractmethod
import random


class CommsError(Exception):
    """Base class for communication errors."""

    pass


class TemporalInterferenceError(CommsError):
    pass


class LinkTerminatedError(CommsError):
    pass


class DataCorruptedError(CommsError):
    pass


class OutOfRangeError(CommsError):
    pass


class BrokenConnectionError(CommsError):
    pass


class Packet:
    def __init__(self, data, sender, receiver):
        self.data = data
        self.sender = sender
        self.receiver = receiver

    def __repr__(self):
        return f"Packet(data='{self.data}', sender='{self.sender.name}', receiver='{self.receiver.name}')"


class SpaceEntity(ABC):
    def __init__(self, name, distance_from_earth):
        self.name = name
        self.distance_from_earth = distance_from_earth

    def __repr__(self):
        return f"SpaceEntity(name='{self.name}', distance_from_earth={self.distance_from_earth})"

    @abstractmethod
    def receive_signal(self, packet: Packet):
        pass


class SpaceNetwork:
    def __init__(self, level=1, noise=0.7):
        self._broken_links = set()
        self.level = level
        self.noise = noise if level >= 2 else 0.0

    def send(self, packet: Packet):
        source_entity = packet.sender
        dest_entity = packet.receiver

        # Check for broken link
        link_key = (source_entity.name, dest_entity.name)
        if link_key in self._broken_links:
            raise LinkTerminatedError("Link has been permanently terminated")

        # Check Range
        dist = abs(source_entity.distance_from_earth - dest_entity.distance_from_earth)
        if dist > 150 and self.level > 2:
            raise OutOfRangeError(f"Distance {dist} exceeds max range of 150")

        # Simulate Noise/Errors
        if random.random() < self.noise:
            # Weighted probabilities:
            # TemporalInterferenceError: 50%
            # DataCorruptedError: 60%
            # LinkTerminatedError: 20%
            error_type = random.choices(
                [TemporalInterferenceError, DataCorruptedError, LinkTerminatedError],
                weights=[50, 60, 20],
                k=1,
            )[0]

            if error_type is LinkTerminatedError and self.level > 2:
                self._broken_links.add(link_key)
                raise LinkTerminatedError("Link has been permanently terminated")
            elif error_type is TemporalInterferenceError:
                raise TemporalInterferenceError("Temporary interference, please retry")
            else:
                raise DataCorruptedError("Data corrupted during transmission")

        print(
            f"[Network] Transmitting from {source_entity.name} to {dest_entity.name}..."
        )
        dest_entity.receive_signal(packet)

class Satellite(SpaceEntity):
    def __init__(self, name, distance_from_earth):
        super().__init__(name, distance_from_earth)

    def receive_signal(self, packet: Packet):
        if isinstance(packet, RelayPacket):
            inner_packet = packet.data
            print(f"Unwrapping and forwarding to {inner_packet.receiver}")
            transmission_attempt(packet.packet_to_relay)
        else:
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

def transmission_attempt(paket: Packet):
    try:
        network_manage.send(paket)
    except TemporalInterferenceError:
        print("Interference, waiting...")
        time.sleep(2)
        transmission_attempt(paket)
    except DataCorruptedError:
        print("Data corrupted, retrying...")
        transmission_attempt(paket)
    except LinkTerminatedError:
        print("Link lost.")
        raise BrokenConnectionError("Link lost.")
    except OutOfRangeError:
        print("Target out of range.")
        raise BrokenConnectionError("Target out of range.")

network_manage = SpaceNetwork(5)

Sat1 = Satellite("satellite1", 100)
Sat2 = Satellite("satellite2", 200)
Sat3 = Satellite("satellite3", 300)
Sat4 = Satellite("satellite4", 400)
Sat5 = Satellite("satellite5", 500)
Earth = Satellite("Earth", 0)
# Satellites_list = [Sat1, Sat2, Sat3, Sat4, Sat5]

message1 = Packet("Hi there", Sat1, Sat2)
final_p = Packet("Hello from Earth", Sat1, Sat2)
p_earth_to_sat1 = RelayPacket(final_p, Earth, Sat1)
proxy1 = RelayPacket(p_earth_to_sat1, Sat1, Sat2)
proxy2 = RelayPacket(proxy1, Sat2, Sat3)
proxy3 = RelayPacket(proxy2, Sat3, Sat4)
proxy4 = RelayPacket(proxy3, Sat4, Sat5)


# try:
#     transmission_attempt(message1)
# except BrokenConnectionError:
#     print("failed Transmission")

try:
    transmission_attempt(proxy4)
except BrokenConnectionError:
    print("failed Transmission")