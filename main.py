from socket import *
import os, sys
import threading

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

#used in getting input/recieving messages in a thread
def clear_console():
    command = 'clear'
    if os.name in ('nt', 'dos'):  # If machine is running on Windows, use cls
        command = 'cls'
    os.system(command)

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
        self.exited_connections = []
        self.lock = threading.Lock()

    def create_server_socket(self):
        # prepare a server socket
        server_socket = socket(AF_INET, SOCK_STREAM)
        # bind socket to host (my IP?) on port 1600
        server_socket.bind((self.ip, self.port))
        server_socket.listen(self.max_requests) 
        return server_socket

    def handle_request(self, message, connection_socket, client_id):
        # this is entire connection for each client socket
        # handle intial request then continue to listen
        print(f"client id is {client_id}")

        message_type = self.message_parser.get_message_type(message)
        print(message_type["message_type"])
        if message_type["message_type"] == self.message_parser.PASSWORD:
            self.handle_password_request(message_type["payload"], connection_socket)
        elif message_type["message_type"] == self.message_parser.JOIN:
            self.handle_join_request(message_type["payload"], connection_socket)
        elif message_type["message_type"] == self.message_parser.MESSAGE:
            self.handle_message_request(message_type["payload"], connection_socket, client_id)
        elif message_type["message_type"] == self.message_parser.EXIT:
            self.handle_exit_request(message_type["payload"], connection_socket, client_id)

        while True:
            try:
                if client_id in self.exited_connections:
                    return
                message = connection_socket.recv(4096).decode()
                if len(message) > 0:
                    message_type = self.message_parser.get_message_type(message)

                    if message_type["message_type"] == self.message_parser.PASSWORD:
                        self.handle_password_request(message_type["payload"], connection_socket)
                    elif message_type["message_type"] == self.message_parser.JOIN:
                        self.handle_join_request(message_type["payload"], connection_socket)
                    elif message_type["message_type"] == self.message_parser.MESSAGE:
                        self.handle_message_request(message_type["payload"], connection_socket, client_id)
                    elif message_type["message_type"] == self.message_parser.EXIT:
                        self.handle_exit_request(message_type["payload"], connection_socket, client_id)
                    
            except KeyboardInterrupt:
                # sys.exit()
                print("\nClosing server...")
                self.close_server()
        #self.close_server()

        # switch on message_body/type NAME/PASSWORD/MESSAGE

        ### this was from browser test
        # connection_socket.send("HTTP/1.1 200 OK\r\n".encode())
        # connection_socket.send("Content-Type: text/html; charset=UTF-8\n".encode())
        # connection_socket.send("\r\n".encode())
        # connection_socket.send(f"Hello {message_body}".encode())
        # connection_socket.send("\r\n".encode())
        ###
    
    def handle_exit_request(self, payload, connection_socket, client_id):
        # self.chat_room.add_visitor(payload)
        self.exited_connections.append(client_id)
        self.established_connections[client_id].close()

        # print(self.chat_room.visitors)

    def handle_password_request(self, payload, connection_socket):
        if self.chat_room.validate_password(payload):
            connection_socket.send(self.PASSWORD_SUCCESS.encode())
        else:
            connection_socket.send(self.PASSWORD_FAILURE.encode())
    
    def handle_join_request(self, payload, connection_socket):
            self.chat_room.add_visitor(payload)
            print(self.chat_room.visitors)
    
    def handle_message_request(self, payload, connection_socket, client_id):
        sender = payload["sender"]
        message = payload["message"]
        added_message = self.chat_room.add_message(sender, message)
        for i, client_socket in enumerate(self.established_connections):
            if i not in self.exited_connections:
                client_socket.send(added_message.encode())
        # connection_socket.send(added_message.encode())
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
                    new_request = threading.Thread(target=self.handle_request, args=(message, connection_socket, self.connection_count))
                    new_request.start()
                    self.connection_count += 1 # use as an index when closing/updating 
                    # self.handle_request(message, connection_socket)
                #    message_recieved = True
            except KeyboardInterrupt:
                # sys.exit()
                print("\nClosing server...")
                self.close_server()

    def close_server(self):
        self.server_socket.close()
        for client in self.established_connections:
            client.close()

        sys.exit()

if __name__=="__main__":
    server = ChatServer()
    server.serve()

    # client = ChatClient()
    # client.run_client()
    # parser = MessageParser()
    # test = parser.get_message_type("NAME: john\n MESSAGE: hello\n")
    # print(test)