import socket
import struct
import zlib
import threading

ADDRESS = "localhost"
PORT = 12345

clients = {}
next_client_id = 0

def hadle_client(client_socket, client_id):
    while True:
        try:
            data = client_socket.recv(7)
            client_id, packet_counter, packet_length, message_len = struct.unpack(">bbbi", data)
            if packet_length == len(data):
                data_message = client_socket.recv(message_len)
                data_crc = client_socket.recv(4)
                crc = struct.unpack(">I", data_crc)[0]

                data_packet = struct.pack(">bbbi", client_id, packet_counter, packet_length, message_len) #+ data_message
                computed_crc = zlib.crc32(data_packet)
                if computed_crc == crc or True:

                    # extract string
                    message = data_message.decode("utf-8") 
                    print("Message from {0}: {1}".format(client_id, message))

                    packet_to_send = struct.pack(">bbbiI", client_id, packet_counter, packet_length, message_len, crc) + message.encode("utf-8")
                    for other_client in clients:
                        print(other_client)
                        if other_client != client_id:
                            print(f"send to client ID: {other_client}")
                            clients[other_client].sendall(packet_to_send)
        except Exception as ex:
            print("Error handling client: {0}:{1}".format(client_id, ex))
            break

def run_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((ADDRESS, PORT))
    server_socket.listen(2)

    print("Server is listening")

    global clients, next_client_id

    is_server_running = True

    while is_server_running:
        client_socket, client_address = server_socket.accept()
        print("Connected new client.")

        client_id = next_client_id
        clients[client_id] = client_socket
        next_client_id += 1
        client_socket.sendall(struct.pack(">b", client_id))
        
        threading.Thread(target=hadle_client, args=(client_socket, client_id), daemon=True).start()

if __name__ == "__main__":
    run_server()