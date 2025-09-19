import socket
import struct
import zlib
import threading

ADDRESS = "localhost"
PORT = 12345

client_id = 0
counter = 0
clients_counter = {} # clientID, counter
is_client_running = False

def receive_messages(sock):
    print("start client receive message.")
    global is_client_running, clients_counter
    while True:
        try:
            data = sock.recv(7)
            if  not data:
                break
            
            sender_id, packet_counter, packet_length, sender_message_len = struct.unpack(">bbbi", data)
            if packet_length == len(data):
                data_crc = sock.recv(4)
                crc = struct.unpack(">I", data_crc)[0]
                data_packet = struct.pack(">bbbi", client_id, packet_counter, packet_length, sender_message_len)
                computed_crc = zlib.crc32(data_packet)
                if computed_crc == crc or True:
                    clients_counter[sender_id] = packet_counter
                    data_message = sock.recv(sender_message_len)
                    sender_message = data_message.decode("utf-8")
                    print(f"\n[CLIENT_{sender_id}]: {sender_message}")
        except Exception as ex:
            print("Error handling client: {0}:{1}".format(client_id, ex))
            break

    is_client_running = False
    sock.close()

def run_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect((ADDRESS, PORT))
    except:
        print("Error: unable to connect to the server")
        return

    print("Connected to server at: {0}:{1}".format(ADDRESS, PORT))
    global client_id, counter
    data = client_socket.recv(4)
    client_id = struct.unpack(">b", data)[0]

    threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()

    global is_client_running
    is_client_running = True

    while is_client_running:
        message = input()
        if message.lower() == "exit":
            break

        packet = create_packet(message.encode("utf-8"))   
        client_socket.sendall(packet)

    client_socket.close()

def create_packet(message):
        global counter
        message_len = len(message)
        packet_lenght = 7
        data_packet = struct.pack(">bbbi", client_id, counter, packet_lenght, message_len) 
        counter += 1
        if counter > 255:
            counter = -1

        crc = zlib.crc32(data_packet)
        packet = data_packet + message + struct.pack(">I", crc)
        return packet


if __name__ == "__main__":
    run_client()
