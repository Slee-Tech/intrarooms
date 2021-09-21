from socket import *
import os, sys # In order to terminate the program
import threading

# could be used in getting input/recieving messages in a thread
# may not be needed
def clear_console():
    command = 'clear'
    if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
        command = 'cls'
    os.system(command)

class ChatRoom:
    def __init__(self):
        self.visitors = []
        self.messages = []
        self.password = "p"
    
    def add_visitor(self, name):
        self.visitors.append(name)
    
    def validate_password(self, password):
        if password == self.password:
            return True
        else:
            return False
    
    def add_message(self, sender, message, recipient="ALL"):
        new_message = "\n"
        new_message = f"\nFROM: {sender} TO: {recipient}\n"
        new_message += message
        new_message += "\n"
        self.messages.append(new_message)
        return new_message

    def get_messages(self):
        return self.messages
    
    # for initial join of new users
    def get_messages(self):
        return self.messages

    def get_most_recent_message(self):
        if len(self.messages > 0):
            return self.messages[-1]

class ChatClient:
    def __init__(self):
        self.host_ip = '127.0.0.1'
        self.host_port = 1600
        self.client_socket = self.create_client_connection()
        self.joined_room = False
        self.name = "New Chatter" # init when join successfully
        self.EXIT = False

    def run_client(self):
        # prompt until entered password or exit
        while not self.joined_room or self.EXIT:
            self.join_room_with_password()
        
        if self.joined_room and not self.EXIT:
            # promt/display messages
            while not self.EXIT: # probably don't need this loop actually?
                return
                # probably want a thread for recieving input and recv messages?
                input_thread = threading.Thread(target=self.recieve_input)
                get_messages_thread = threading.Thread(target=self.get_messages)
                input_thread.start()
                get_messages_thread.start()
                # don't believe join() is need on these?
        
        self.client_socket.close()
    
    def get_messages(self):
        response = client_socket.recv(4096)

        if(response):
            while len(response) > 0:
                print(response.decode())
                response = client_socket.recv(4096)

    def recieve_input(self):
        new_message = input("Enter a message: ")
        self.send_message(new_message)
    
    def create_client_connection(self):
        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket.connect((self.host_ip, int(self.host_port)))
        return client_socket

    def send_message(self, message):
        # extract name, recipient/message here
        self.client_socket.send(f"Name: {self.name}\n Message: {message}\n".encode())
    
    def send_password(self, password):
        self.client_socket.send(f"PASSWORD: {password}".encode())
    
    def send_name(self, name):
        self.client_socket.send(f"JOIN: {name}".encode())
    
    def join_room_with_password(self):
        print("Please enter password to join the chatroom (or type EXIT to leave) :\n")
        entered_password = input()
        message = self.send_message(entered_password)
        if message == "EXIT":
            self.EXIT = True
            return
        elif message: # True check on server if password was correct in chatroom
            self.joined_room = True
            print("Please enter your name:\n")
            self.name = input()

class MessageParser:
    EXIT = "EXIT:"
    PASSWORD = "PASSWORD:"
    JOIN = "JOIN:"
    ERROR = "ERROR:"
    MESSAGE = "NAME:"
    
    def get_message_type(self, message):
        message_body = message.split(" ")
        print(message_body)

        # return dict with message type, and payload
        if message_body[0] == self.PASSWORD:
            return {
                "message_type": self.PASSWORD,
                "payload": message_body[1]
            }
        elif message_body[0] == self.EXIT:
            return {
                "message_type":self.EXIT,
                "payload": message_body[1]
            }
        elif message_body[0] == self.JOIN:
            return {
                "message_type":self.JOIN,
                "payload": message_body[1]
            }
        elif message_body[0] == self.MESSAGE:
            # in this case, name will be first then
            # find message body
            message_to_send = message.split("MESSAGE:")[1][1:-1]
            print(f"TO send: {message_to_send}") # handle space
            return {
                "message_type":self.MESSAGE,
                "payload": {
                    "sender": message_body[1][:-1],
                    "message": message_to_send
                }
            }
        else:
            return self.ERROR

class ChatServer:
    def __init__(self):
        self.chat_room = ChatRoom()
        self.ip = '127.0.0.1'
        self.port = 1600
        self.max_requests = 5
        self.server_socket = self.create_server_socket()
        self.message_parser = MessageParser()
        self.PASSWORD_SUCCESS = "SUCCESS"
        self.PASSWORD_FAILURE = "FAILURE"
        self.established_connections = []
        self.connection_count = 0

    def create_server_socket(self):
        # prepare a server socket
        server_socket = socket(AF_INET, SOCK_STREAM)
        # bind socket to host (my IP?) on port 1600
        server_socket.bind((self.ip, self.port))
        server_socket.listen(self.max_requests) 
        return server_socket

    def handle_request(self, message, connection_socket):
        # maybe extract to function
        # message_body = message.split()[1][1:]
        # print(f"message is: {message}")
        # print(message_body)
        # this is entire connection for each socket client
        while True:
            message = connection_socket.recv(4096).decode()

        message_type = self.message_parser.get_message_type(message)
        print(message_type["message_type"])
        if message_type["message_type"] == self.message_parser.PASSWORD:
            self.handle_password_request(message_type["payload"], connection_socket)
        elif message_type["message_type"] == self.message_parser.JOIN:
            self.handle_join_request(message_type["payload"], connection_socket)
        elif message_type["message_type"] == self.message_parser.MESSAGE:
            self.handle_message_request(message_type["payload"], connection_socket)
        elif message_type["message_type"] == self.message_parser.EXIT:
            # self.handle_password_request(message_type["payload"], connection_socket)
            connection_socket.close()
        #self.close_server()

         # switch on message_body/type NAME/PASSWORD/MESSAGE

        ### this was from browser test
        # connection_socket.send("HTTP/1.1 200 OK\r\n".encode())
        # connection_socket.send("Content-Type: text/html; charset=UTF-8\n".encode())
        # connection_socket.send("\r\n".encode())
        # connection_socket.send(f"Hello {message_body}".encode())
        # connection_socket.send("\r\n".encode())
        ###

    def handle_password_request(self, payload, connection_socket):
        if self.chat_room.validate_password(payload):
            connection_socket.send(self.PASSWORD_SUCCESS.encode())
        else:
            connection_socket.send(self.PASSWORD_FAILURE.encode())
    
    def handle_join_request(self, payload, connection_socket):
            self.chat_room.add_visitor(payload)
            print(self.chat_room.visitors)
    
    def handle_message_request(self, payload, connection_socket):
        sender = payload["sender"]
        message = payload["message"]
        added_message = self.chat_room.add_message(sender, message)
        connection_socket.send(added_message.encode())
        print(added_message)

    def serve(self):
        message_recieved = False
        while True:
            try:
                print('Ready to serve...')
                #establish the connection
                connection_socket, addr = self.server_socket.accept()
                message = connection_socket.recv(4096).decode()
                print(f"Message recieved: {message}")

                if len(message) > 0:
                    self.established_connections.append(connection_socket)
                    self.connection_count += 1 # use as an index when closing/updating 
                    new_request = threading.Thread(target=self.handle_request, args=(message, connectionSocket))
                    new_request.start()
                    # self.handle_request(message, connection_socket)
                #    message_recieved = True
            except KeyboardInterrupt:
                # sys.exit()
                print("\nClosing server...")
                self.close_server()

    def close_server(self):
        self.server_socket.close()
        sys.exit()

if __name__=="__main__":
    server = ChatServer()
    server.serve()
    # client = ChatClient()
    # client.run_client()
    # parser = MessageParser()
    # test = parser.get_message_type("NAME: johnthony\n MESSAGE: you are a fucker\n")
    # print(test)