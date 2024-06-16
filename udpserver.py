import socket
import struct
import random
import time

SERVER_IP = '0.0.0.0'
SERVER_PORT = 12345
LOSS_RATE = 0.2


def create_response_packet(seq_no):
    server_time = time.strftime('%H-%M-%S').encode('ascii')
    return struct.pack('!H B 200s', seq_no, 2, server_time + b'\x00' * 192)


def parse_packet(packet):
    # 解析packet
    seq_no, ver, other_content = struct.unpack('!H B 200s', packet)
    return seq_no, ver, other_content


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))

    print(f"Server listening on {SERVER_IP}:{SERVER_PORT}")

    while True:
        try:
            packet, client_addr = server_socket.recvfrom(2048)
            seq_no, ver, other_content = parse_packet(packet)
            print(f"Received packet: Seq No {seq_no} from {client_addr}")

            if random.random() > LOSS_RATE:
                response_packet = create_response_packet(seq_no)
                server_socket.sendto(response_packet, client_addr)
                print(f"Sent response for Seq No {seq_no} to {client_addr}")
            else:
                print(f"Simulating packet loss for Seq No {seq_no}")
        except Exception as e:
            print(e)
            break

    server_socket.close()


if __name__ == '__main__':
    main()