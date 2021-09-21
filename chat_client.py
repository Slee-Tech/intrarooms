from socket import *
import os, sys # In order to terminate the program
import threading
from main import clear_console

class ChatClient:
    def __init__(self):
        self.host_ip = '127.0.0.1'
        self.host_port = 1600
        self.client_socket = self.create_client_connection()
        self.joined_room = False
        self.name = "New Chatter" # init when join successfully
        self.EXIT = False
        self.PASSWORD_SUCCESS = "SUCCESS"
        self.PASSWORD_FAILURE = "FAILURE"
        self.lock = threading.Lock()
        self.recieved_messages = []

    def run_client(self):
        # prompt until entered password or exit
        while not self.joined_room and not self.EXIT:
            # first connection scope
            self.join_room_with_password()
        
        if self.joined_room and not self.EXIT:
            # promt/display messages
            # while not self.EXIT: # probably don't need this loop actually?
                # probably want a thread for recieving input and recv messages?
            input_thread = threading.Thread(target=self.recieve_input)
            get_messages_thread = threading.Thread(target=self.get_messages)
            get_messages_thread.start()
            input_thread.start()
            return
                # don't believe join() is need on these?
        
        # self.client_socket.close()
    
    def get_messages(self):
        # cself.lient_socket = self.create_client_connection()

        while True:
            if self.EXIT:
                # self.client_socket.close()
                return
            else:
                with self.lock:
                    # self.client_socket = self.create_client_connection()
                    response = self.client_socket.recv(4096)
                full_response = ""
                if len(response) > 0:
                    clear_console()
                    self.add_recieved_message(response.decode())
                    self.print_messages()
                    # print(response.decode())
                    with open("chatlog.txt", 'a', encoding='utf-8') as f:
                        f.write(response.decode())
        return

          # maybe add to list of recieved messages?
            # print(f"full res == pass: {response.decode() == self.PASSWORD_SUCCESS}")

            # if(response):
            #     while len(response) > 0:
            #         print(f"1st decode of response: {response.decode()}")
            #         full_response += response.decode()
            #         response = self.client_socket.recv(4096)
            # print(full_response.rstrip())
            # return full_response.rstrip()
            # if self.EXIT == True:
            #     return
    
    def add_recieved_message(self, message):
        self.recieved_messages.append(message)

    def print_messages(self):
        for message in self.recieved_messages:
            print(message)
        
        # reprompt for input since it will be cleared
        print("Enter a message: ")

    def get_password_message(self):
        # client_socket = self.create_client_connection()#socket(AF_INET, SOCK_STREAM)
        response = self.client_socket.recv(4096)
        print(response.decode())
        # client_socket.close()
        return response.decode()

    def recieve_input(self):
        while not self.EXIT:
            new_message = input("Enter a message: ")

            if new_message == "EXIT":
                self.EXIT = True
                self.send_exit()
                return
            else:
                self.send_message(new_message)
    
    def create_client_connection(self):
        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket.connect((self.host_ip, int(self.host_port)))
        return client_socket

    def send_message(self, message):
        # extract name, recipient/message here
        self.client_socket = self.create_client_connection()
        self.client_socket.send(f"NAME: {self.name}\n MESSAGE: {message}\n".encode())
    
    def send_password(self, password):
        # client_socket = self.create_client_connection()
        self.client_socket.send(f"PASSWORD: {password}".encode())
        # client_socket.close()
    
    def send_name(self, name):
        # try re-establishing the connection
        client_socket = self.create_client_connection()
        client_socket.send(f"JOIN: {name}".encode())
        client_socket.close()
    
    def send_exit(self):
        client_socket = self.create_client_connection()
        client_socket.send(f"EXIT: {self.name}".encode())
        client_socket.close()
    
    def join_room_with_password(self):
        print("Please enter password to join the chatroom (or type EXIT to leave):")
        entered_password = input()

        if entered_password == "EXIT":
            self.EXIT = True
            # self.get_messages()
            self.send_exit()
            # self.client_socket.close()
            return
        
        self.send_password(entered_password)
        message = self.get_password_message()

        if message == self.PASSWORD_SUCCESS: # True check on server if password was correct in chatroom
            self.joined_room = True
            print("Please enter your name:")
            self.name = input()
            self.send_name(self.name)

if __name__=="__main__":
    # server = ChatServer()
    # server.serve()
    client = ChatClient()
    client.run_client()
    # message = input()
    # if message == "EXIT":
    #     print(True)
    # else:
    #     print(False)