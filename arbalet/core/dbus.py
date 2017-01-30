"""
    Arbalet - ARduino-BAsed LEd Table
    Arbalet Data Bus

    Central bus based on ZMQ for inter-process communication

    Copyright 2017 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""
from json import dumps, loads
from .config import ConfigReader
import zmq

__all__ = ['DBusClient']

class Channel(object):
    def __init__(self, channel_name, context, host, port_pub, port_sub, publisher, subscriber, conflate):
        if publisher:
            connect_to = "tcp://{}:{}".format(host, port_pub)
            self._publisher = context.socket(zmq.PUB)
            if conflate:
                self._publisher.setsockopt(zmq.CONFLATE, 1)
            print("Connecting publisher to {} on channel {}".format(connect_to, channel_name))
            self._publisher.connect(connect_to)
        if subscriber:
            connect_to = "tcp://{}:{}".format(host, port_sub)
            self._subscriber = context.socket(zmq.SUB)
            if conflate:
                self._subscriber.setsockopt(zmq.CONFLATE, 1)
            self._subscriber.setsockopt(zmq.SUBSCRIBE, channel_name)
            print("Connecting subscriber to {} on channel {}".format(connect_to, channel_name))
            self._subscriber.connect(connect_to)
        self.is_publisher = publisher
        self.is_subscriber = subscriber
        self.channel = channel_name

    def publish(self, data):
        """
        Send a message to this channel
        :param data: List or Map to send
        """
        if self.is_publisher:
            self._publisher.send(self.channel + ' ' + dumps(data))
        else:
            print("[Arbalet D-Bus] Cannot publish data, channel '{}' is not a publisher".format(self.channel))

    def recv(self, blocking=True):
        """
        Receive a message from this channel
        :param blocking: Must block until a message is received
        :return: returns None if no message has been received in blocking mode, the decoded list or map otherwise
        """
        if self.is_subscriber:
            flags = 0 if blocking else zmq.NOBLOCK
            try:
                data = self._subscriber.recv(flags=flags)
            except zmq.error.ZMQError as e:
                if blocking:
                    raise
            else:
                return loads(data[len(self.channel)+1:])
        else:
            print("[Arbalet D-Bus] Cannot receive data, channel '{}' is not a subscriber".format(self.channel))
            return None

    def close(self):
        if self.is_subscriber:
            self._subscriber.close()
        if self.is_publisher:
            self._publisher.close()


class DBusClient(object):
    """
    Reading/writing data bus interface
    Only 1 D-Bus interface must be declared by process
    """
    def __init__(self, host="127.0.0.1", event_publisher=False, event_subscriber=False, display_publisher=False, display_subscriber=False):
        config_reader = ConfigReader()
        dbus_config = config_reader.dbus
        port_pub = dbus_config['xpub_port']
        port_sub = dbus_config['xsub_port']
        self._context = zmq.Context()
        self.events = Channel('events', self._context, host, port_pub, port_sub, event_publisher, event_subscriber, False)
        self.display = Channel('display', self._context, host, port_pub, port_sub, display_publisher, display_subscriber, True)

    def close(self):
        self.events.close()
        self.display.close()
