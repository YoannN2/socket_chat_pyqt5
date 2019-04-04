from PyQt5 import QtCore, QtGui, QtWidgets, QtNetwork
from PyQt5.uic import loadUi
import socket
import errno
import sys
import argparse


HEADER_LENGTH = 10
IP = socket.gethostname()
PORT = 1234

class Chat(QtWidgets.QWidget):
    def __init__(self, username):
        super(Chat, self).__init__()
        self.ui = loadUi("ui/chat_window.ui", self)
        self.ui.username_label.setText(username)
        self.username = username

        self.connect_to_server()

        self.ui.chat.append("Starting the chat...")

        self.ui.message.returnPressed.connect(self.send_msg)
        self.ui.send_btn.clicked.connect(self.send_msg)


        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_chat)
        self.timer.start(500)

    def update_chat(self):
        try:
            username_header = self.client_socket.recv(HEADER_LENGTH)
            if not len(username_header):
                print("Connection closed by the server")
                sys.exit()

            username_length = int(username_header.decode("utf-8").strip())
            username = self.client_socket.recv(username_length).decode("utf-8")

            message_header = self.client_socket.recv(HEADER_LENGTH)
            message_length = int(message_header.decode("utf-8").strip())
            message = self.client_socket.recv(message_length).decode("utf-8")

            self.ui.chat.append(f"{username}: {message}")

        except IOError as e:
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print("Reading error", str(e))
                sys.exit()
            pass

        except Exception as e:
            print("General error", str(e))
            sys.exit()


    def connect_to_server(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((IP, PORT))
        self.client_socket.setblocking(False)

        username = self.username.encode("utf-8")
        username_header = f"{len(username):<{HEADER_LENGTH}}".encode("utf-8")
        self.client_socket.send(username_header + username)

    def send_msg(self):
        # get the msg
        msg = self.ui.message.text()

        # send msg to server
        if msg:
            message = msg.encode("utf-8")
            message_header = f"{len(message):<{HEADER_LENGTH}}".encode("utf-8")

            self.client_socket.send(message_header + message)

        # clear msg
        self.ui.message.setText("")


    def recv_msgs(self, msg):
        """
        I GOT NO IDEA >.<
        """
        print(type(msg), msg)
        # IDK how to get the msgs from the server




if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    parser = argparse.ArgumentParser()
    parser.add_argument("--username", default="anonymous", help="Choose a username, defaults to 'default' if left blank")

    args = parser.parse_args()
    username = args.username

    chat = Chat(username)
    chat.show()

    sys.exit(app.exec_())
