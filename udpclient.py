import socket
import time
import struct
import random

SERVER_IP = '192.168.109.129'
SERVER_PORT = 12345
TIMEOUT = 0.1  # 100ms
TOTAL_REQUESTS = 12
VERSION = 2


def create_packet(seq_no):
    # 创建packet，包含 sequence number, version number以及其他填充内容
    return struct.pack('!H B 200s', seq_no, VERSION, b'a' * 200)


def parse_packet(packet):
    # 解析packet
    seq_no, ver, other_content = struct.unpack('!H B 200s', packet)
    return seq_no, ver, other_content


def parse_time(time_bytes):
    # 将服务器时间字符串解析为struct_time
    server_time_str = time_bytes.decode('ascii').strip('\x00')
    try:
        parsed_time = time.strptime(server_time_str, '%H-%M-%S')
        # 补充日期信息，假设是今天的时间
        now = time.localtime()
        full_time = (now.tm_year, now.tm_mon, now.tm_mday, parsed_time.tm_hour, parsed_time.tm_min, parsed_time.tm_sec, now.tm_wday, now.tm_yday, now.tm_isdst)
        return full_time
    except ValueError as e:
        print(f"Time parsing error: {e}")
        return None


def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(TIMEOUT)

    received_packets = 0#结接受包
    rtt_list = []
    #初始化
    start_time = None
    end_time = None

    for seq_no in range(1, TOTAL_REQUESTS + 1):
        packet = create_packet(seq_no)
        for attempt in range(3):
            try:
                start = time.time()
                client_socket.sendto(packet, (SERVER_IP, SERVER_PORT))
                response, server = client_socket.recvfrom(2048)
                end = time.time()

                server_seq_no, ver, server_time = parse_packet(response)

                if server_seq_no == seq_no:
                    received_packets += 1
                    rtt = (end - start) * 1000  # RTT in ms
                    rtt_list.append(rtt)
                    print(f"Sequence No: {seq_no}, Server IP:Port = {SERVER_IP}:{SERVER_PORT}, RTT = {rtt:.2f}ms")

                    # Update server response time
                    parsed_server_time = parse_time(server_time[:8])
                    if parsed_server_time:
                        #更新赋值
                        if not start_time:
                            start_time = parsed_server_time
                        #每次成功解析出服务器时间后，更新 end_time
                        end_time = parsed_server_time
                    break
            except socket.timeout:
                print(f"Sequence No: {seq_no}, Request Timed Out")
                continue

    # 总结信息
    #生成条件
    if received_packets > 0 and start_time and end_time:
        max_rtt = max(rtt_list)
        min_rtt = min(rtt_list)
        avg_rtt = sum(rtt_list) / received_packets
        std_dev_rtt = (sum([(x - avg_rtt) ** 2 for x in rtt_list]) / received_packets) ** 0.5
        response_time = time.mktime(end_time) - time.mktime(start_time)
    else:
        max_rtt = min_rtt = avg_rtt = std_dev_rtt = response_time = -1

    #输出，保留两位小数
    print("\nSummary")
    print(f"Received UDP Packets: {received_packets}")
    print(f"Packet Loss Rate: {(1 - received_packets / TOTAL_REQUESTS) * 100:.2f}%")
    print(f"Max RTT: {max_rtt:.2f}ms")
    print(f"Min RTT: {min_rtt:.2f}ms")
    print(f"Average RTT: {avg_rtt:.2f}ms")
    print(f"RTT Standard Deviation: {std_dev_rtt:.2f}ms")
    print(f"Server Response Time: {response_time:.2f}s")

    client_socket.close()


if __name__ == '__main__':
    main()
