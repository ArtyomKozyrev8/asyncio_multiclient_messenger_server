"""
To create client side of the application I had to use multithreading module since input() function
can't be used effectively in asyncio, since asyncio loop is blocked until we input data and press Enter key.
"""


import socket
import threading
import sys
import time


def listen_server_words(s):
    while True:
        try:
            s.connect(('127.0.0.1', 8888))
        except ConnectionRefusedError:
            print("Trying co connect to the remote server {} {} ...".format('127.0.0.1', 8888))
            time.sleep(2)
        else:
            print("Connection with {} {} was established".format('127.0.0.1', 8888))
            break
    print("To break connection with the remote server print: quit")
    while True:
        try:
            data = s.recv(1024)
            if data:
                data = data.decode('utf-8')
                income_data = data.split("|")
                income_data.pop()  # remove empty part
                for m in income_data:
                    from_whom, message = m.split("***")
                    print(f"{from_whom} says: {message}")
        except ConnectionResetError:
            print("Session was finished by the remote server")
            break


def represent_yourself(s_: socket.socket):
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
                break


if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    th = threading.Thread(target=listen_server_words, args=(s,), daemon=True)
    th.start()
    time.sleep(1)
    represent_yourself(s)
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
                    sys.exit(100)
        except ConnectionResetError:
            print("The server stopped connection earlier")
            print("Please close the program")
        except OSError:
            pass
