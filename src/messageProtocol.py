from socket import socket

from messageType import *


class MessageProtocolError(Exception):
    pass


class Message:
    def __init__(self, message_type: int, data: bytes):
        self.message_type = message_type
        self.data = data

    def as_bytes(self) -> bytes:
        if self.message_type < 0:
            raise MessageProtocolError
        b = bytearray()
        b.append(0xff)
        b.append(self.message_type)
        b.extend(self.data)
        b.append(0xff)
        b.append(self.message_type + 0x80)
        return bytes(b)

    def __str__(self):
        return "[Message " + str(self.message_type) + " " + str(self.data) + "]"


class MessageProtocol:
    def __init__(self, remote: socket, name: str):
        self.name = name
        self.remote = remote
        self.buffer = bytearray()
        self.active = True
        self.disconnected = False
        self.remote_name = ''

        self.hello()

    def receive(self) -> list[Message]:
        self.read_incoming_data()
        messages = self.extract_messages()
        response = []
        for m in messages:
            if m.message_type == MESSAGE_GREETING:
                self.remote_name = m.data.decode('utf-8')
            else:
                response.append(m)
        return response

    def read_incoming_data(self) -> None:
        while True:
            try:
                response = self.remote.recv(4096, 0)
            except BlockingIOError:
                break
            if len(response) == 0:
                self.disconnect()
                break
            self.buffer.extend(response)

    def disconnect(self) -> None:
        if self.active:
            self.active = False
            self.disconnected = True
            self.remote.close()

    def extract_messages(self) -> list[Message]:
        messages = []
        while True:
            m = self.extract_message()
            if m is None:
                break
            messages.append(m)
        if self.disconnected:
            messages.append(Message(MESSAGE_DISCONNECTED, b''))
            self.disconnected = False
        return messages

    def extract_message(self) -> Message | None:
        if len(self.buffer) < 4:
            return None
        for i in range(len(self.buffer) - 1):
            if self.buffer[i] == 0xff and self.buffer[i+1] > 0x7f:
                message_end = self.buffer[i+1]
                expected_start = message_end - 0x80
                message_data = self.buffer[2:i]
                start_seq = self.buffer[0:2]
                # end_seq = self.buffer[i:i+2] # Ending sequence already validated
                self.buffer = bytearray(self.buffer[i+2:])

                message_type = expected_start

                if start_seq[0] != 0xff or start_seq[1] != expected_start:
                    message_type = MESSAGE_INVALID

                return Message(message_type, message_data)
        return None

    def send_message(self, message: Message) -> None:
        try:
            self.remote.sendall(message.as_bytes())
        except OSError:
            self.disconnect()

    def hello(self) -> None:
        self.send_message(Message(MESSAGE_GREETING, self.name.encode('utf-8')))

    def navigate(self, url: str) -> None:
        self.send_message(Message(MESSAGE_NAVIGATION, url.encode('utf-8')))

    def back(self) -> None:
        self.send_message(Message(MESSAGE_BACK, 'back'.encode('utf-8')))

    def forward(self) -> None:
        self.send_message(Message(MESSAGE_FORWARD, 'forward'.encode('utf-8')))

    def pagedata(self, data: bytes) -> None:
        self.send_message(Message(MESSAGE_PAGEDATA, data))
