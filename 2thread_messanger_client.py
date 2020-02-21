"""
To create client side of the application I had to use multithreading module since input() function can't be used
effectively in asyncio, since asyncio loop is blocked until we input data and press Enter key. Client file is much
easier than server file, we create additional thread to listen to incoming messages from server. The main thread is
used to write messages to other clients.

To use client just run the file. To have several clients run this file in separate console windows.

When the script starts run short name - it will be name of the client. Then to write message to another client write:
another_client_name##your long message here.

To close connection print quit then press Enter key or just stop the file.
"""


import socket
import threading
import sys
import time


def listen_server_words(s: socket.socket):
    """
    This function is used to listen to incoming messages from other clients (actually from server).
    The function is used in the second thread.
    :param s: this is socket instance
    :return:
    """
    while True:
        try:
            s.connect(('127.0.0.1', 8888))
        except ConnectionRefusedError:
            print("Trying co connect to the remote server {} {} ...".format('127.0.0.1', 8888))
            time.sleep(2)
        else:
            print("Connection with {} {} was established".format('127.0.0.1', 8888))
            break

    # this is the main part of the function which listens to incomming messages
    while True:
        try:
            data = s.recv(1024)
            if data:
                data = data.decode('utf-8')
                income_data = data.split("|")
                income_data.pop()  # remove empty part
                for m in income_data:
                    from_whom, message = m.split("##")
                    print(f"{from_whom} says: {message}")
        except ConnectionResetError:
            print("Session was finished by the remote server")
            break


def represent_yourself(s_: socket.socket):
    """
    This is support function which is used in main thread, it is used to define client name
    :param s_: this is socket instance
    :return:
    """
    while True:
        name = input("What is your name?\n>>")
        if len(name) < 2:
            print("Name can't be less than 2 chars")
        else:
            try:
                s_.send(name.encode('utf8'))
                time.sleep(1)
            except Exception as ex:
                print(f"Failed to connect to the remote server: {ex}")
            else:
                print("To break connection with the remote server print: quit")
                break


if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # IPv4 TCP
    # start another thread 'th' to listen to incoming messages
    th = threading.Thread(target=listen_server_words, args=(s,), daemon=True)
    th.start()
    time.sleep(1)
    represent_yourself(s)

    # the main part of the main thread, which is used to write messages to other clients (actually to server)
    while True:
        word = input(">>")
        try:
            s.sendall(word.encode('utf-8'))
            if word == "quit":
                try:
                    s.close()
                except ConnectionAbortedError:
                    pass
                finally:
                    print("Session was finished by us")
                    sys.exit()
        except ConnectionResetError:
            print("The server stopped connection earlier")
            print("Please close the program")
        except OSError:
            pass
