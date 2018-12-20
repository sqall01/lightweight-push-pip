# written by sqall
# twitter: https://twitter.com/sqall01
# blog: https://h4des.org
# github: https://github.com/sqall01
#
# Licensed under the MIT License.

import time
import socket
import ssl
import os
import base64
import json
import hashlib
import re
from Crypto.Cipher import AES


class ErrorCodes(object):
    """
    Lightweight Push error codes.
    """
    NO_ERROR = 0
    DATABASE_ERROR = 1
    AUTH_ERROR = 2
    ILLEGAL_MSG_ERROR = 3
    GOOGLE_MSG_TOO_LARGE = 4
    GOOGLE_CONNECTION = 5
    GOOGLE_UNKNOWN = 6
    GOOGLE_AUTH = 7
    VERSION_MISSMATCH = 8
    NO_NOTIFICATION_PERMISSION = 9
    CLIENT_CONNECTION_ERROR = 0x1000
    

class Client(object):
    """
    Simple client class to connect via TCP.
    """

    def __init__(self, host, port, server_ca_file):
        self.host = host
        self.port = port
        self.server_ca_file = server_ca_file
        self.socket = None
        self.sslSocket = None

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.sslSocket = ssl.wrap_socket(self.socket,
                                         ca_certs=self.server_ca_file,
                                         cert_reqs=ssl.CERT_REQUIRED)

        self.sslSocket.connect((self.host, self.port))

    def send(self, data):
        count = self.sslSocket.send(data)

    def recv(self, buffsize, timeout=3.0):
        data = None
        self.sslSocket.settimeout(timeout)
        data = self.sslSocket.recv(buffsize)
        self.sslSocket.settimeout(None)
        return data

    def close(self):
        # closing SSLSocket will also close the underlying socket
        self.sslSocket.close()


class LightweightPush(object):

    def __init__(self, username, password, shared_secret):

        self.buffer_size = 4096
        self.host = "push.alertr.de"
        self.port = 14944
        self.ca_file = os.path.dirname(os.path.abspath(__file__)) + "/push.alertr.de.crt"

        # Create an encryption key from the secret.
        sha256 = hashlib.sha256()
        sha256.update(shared_secret.encode("utf-8"))
        self.key = sha256.digest()

        # User credentials for the push service.
        self.username = username
        self.password = password

    def _generate_prefixed_channel(self, channel):
        """
        Create the channel name linked to the username.
        NOTE: This function is not collision free but will improve collision
        resistance if multiple parties choose the same channel.

        :param channel: to send the message to.
        :return: channel with a prefix based on the user to send the message to.
        """
        sha256 = hashlib.sha256()
        sha256.update(self.username.encode("utf-8"))
        prefix = sha256.hexdigest()[0:8]
        return prefix.lower() + "_" + channel

    def _trunc_to_size(self, subject, message):
        """
        Truncates the message and subject to fit in a notification message.

        :param subject: subject of the message to send.
        :param message: message body of the message.
        :return: (subject, message) in a truncated form to fit the limitations.
        """
        len_json_sbj = len(json.dumps(subject))
        len_sbj = len(subject)
        len_json_msg = len(json.dumps(message))
        len_msg = len(message)

        # Consider json encoding (characters like \n need two characters).
        if (len_json_sbj + len_json_msg) > 1400:
            number_to_remove = (len_json_sbj + len_json_msg + 7) - 1400
            if len_msg > number_to_remove:
                message = message[0:(len_msg-number_to_remove)]
                message += "*TRUNC*"
            elif len_sbj > number_to_remove:
                subject = subject[0:(len_sbj-number_to_remove)]
                subject += "*TRUNC*"
            else:
                message = "*TRUNC*"
                number_to_remove = number_to_remove - len_msg + 7
                subject = subject[0:(len_sbj-number_to_remove)]
                subject += "*TRUNC*"

        return subject, message

    def _check_channel(self, channel):
        """
        Checks if the given channel is valid.

        :param channel: channel to check.
        :return: True if the channel is valid.
        """
        return bool(re.match(r'^[a-zA-Z0-9-_.~%]+$', channel))

    def _send_msg(self, data_frame, payload, max_retries):
        """
        Internal function to send data to the push server.

        :param data_frame: data frame to send.
        :param payload: payload of the data to send.
        :param max_retries: maximum number of retries (if -1 we try forever).
        :return: returns error code.
        """
        max_retries_ctr = max_retries
        times_sleep = 5

        # Generate random bytes for encryption.
        iv = os.urandom(16)
        internal_iv = os.urandom(4)

        while True:

            ts = int(time.time())
            payload["ts"] = ts

            # Add random bytes in the beginning of the message to increase
            # randomness.
            padded_payload = internal_iv + json.dumps(payload).encode("utf-8")
            padding = len(padded_payload) % 16
            if padding != 0:
                for i in range(16 - padding):
                    # Use whitespaces as padding since they are ignored by json.
                    padded_payload += b" "

            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            encrypted_payload = cipher.encrypt(padded_payload)

            temp = iv + encrypted_payload
            data_payload = base64.b64encode(temp)

            data_frame["data"] = data_payload.decode("utf-8")

            try:
                client = Client(self.host, self.port, self.ca_file)
                client.connect()
                client.send(json.dumps(data_frame).encode("utf-8"))
                data_recv = client.recv(self.buffer_size)
                client.close()
                error_code = json.loads(data_recv.decode("utf-8"))["Code"]
            except:
                error_code = ErrorCodes.CLIENT_CONNECTION_ERROR

            # Processing error code (decide if to stop or retry).
            if error_code is None:
                pass
            elif error_code == ErrorCodes.NO_ERROR:
                break
            elif error_code == ErrorCodes.DATABASE_ERROR:
                pass
            elif error_code == ErrorCodes.AUTH_ERROR:
                break
            elif error_code == ErrorCodes.ILLEGAL_MSG_ERROR:
                break
            elif error_code == ErrorCodes.GOOGLE_MSG_TOO_LARGE:
                break
            elif error_code == ErrorCodes.GOOGLE_CONNECTION:
                pass
            elif error_code == ErrorCodes.GOOGLE_AUTH:
                pass
            elif error_code == ErrorCodes.VERSION_MISSMATCH:
                break
            elif error_code == ErrorCodes.NO_NOTIFICATION_PERMISSION:
                break
            else:
                break

            # Process retries.
            if max_retries_ctr == 0:
                break
            elif max_retries_ctr < 0:
                pass
            else:
                max_retries_ctr -= 1

            time.sleep(times_sleep)
            times_sleep *= 2
            if times_sleep > 86400:
                times_sleep = 86400

        return error_code

    def send_msg(self, subject, message, channel, state=None, time_triggered=None, max_retries=16):
        """
        Send push notification message to the push server.

        :param subject: subject of the message to send.
        :param message: the text body of the message to send.
        :param channel: the channel the message is sent to.
        :param state: state of the message send (1 for "triggered", 0 for "normal", None for no state) (optional).
        :param time_triggered: time the alarm message was triggered (if not given the current time is used) (optional).
        :param max_retries: maximum number of retries (if -1 we try forever) (optional).
        :return: returns error code (described by class ErrorCodes).
        """

        # Truncate size to current maximum size.
        subject, message = self._trunc_to_size(subject, message)

        # Prepare channel.
        if not self._check_channel(channel):
            raise ValueError("Channel contains illegal characters.")

        # Prepare state.
        is_sa = False
        if state is not None:
            is_sa = True
            if state != 0 and state != 1:
                raise ValueError("State has to be either 0 or 1 when given.")

        # Prepare time the notification is triggered.
        if time_triggered is None:
            tt = int(time.time())
        else:
            tt = int(time_triggered)

        # Prepare base of message.
        payload = {
            "sbj": subject,
            "msg": message,
            "tt": tt,
            "is_sa": is_sa,
            }
        if is_sa:
            payload["st"] = state

        # Prepare channel
        prefixed_channel = self._generate_prefixed_channel(channel)

        # Prepare data to send.
        data_frame = {"username": self.username,
                      "password": self.password,
                      "channel": prefixed_channel,
                      "version": 0.1}

        return self._send_msg(data_frame, payload, max_retries)
