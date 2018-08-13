"""
詳細がわからないプロトコルの調査やアプリに送信するデータを改変したり
するプロキシースクリプト
"""
import argparse
import sys
import socket
import threading


def receive_from(connection):
    buff = b''
    connection.settimeout(2)

    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buff += data
    except socket.timeout:
        pass
    except Exception as e:
        print('[!!] Error:', e)

    return buff

def request_handler(buff):
    """リモート側のホストに送る全リクエストデータの改変"""
    return buff

def response_handler(buff):
    """ローカル側のホストに送る全レスポンスデータの改変"""
    return buff

def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    """データストリームの送受信に関わる全処理を行う"""
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))

    if receive_first:
        remote_buff = receive_from(remote_socket)
        hexdump(remote_buff)

        # 受信データ処理関数にデータを渡す
        remote_buff = response_handler(remote_buff)

        if remote_buff:
            print('[<==] Sending {} bytes to localhost.'.format(len(remote_buff)))
            client_socket.send(remote_buff)

    # ローカルからのデータ受信、リモートへの送信、ローカルへの送信のループを行う
    while True:
        local_buff = receive_from(client_socket)

        if local_buff:
            print('[==>] Received {} bytes from localhost.'.format(len(local_buff)))
            hexdump(local_buff)

            local_buff = request_handler(local_buff)
            remote_socket.send(local_buff)
            print('[==>] Sent to remote.')
    
        remote_buff = receive_from(remote_socket)

        if remote_buff:
            print('[<==] Received {} bytes from remote.'.format(len(remote_buff)))
            hexdump(remote_buff)

            remote_buff = response_handler(remote_buff)

            client_socket.send(remote_buff)
            print('[<==] Sent to localhost.')
            
        if not local_buff or not remote_buff:
            break
    
    client_socket.close()
    remote_socket.close()
    print('[*] No more data. Closing connections.')

def hexdump(data, length=16):
    result = []

    for i in range(0, len(data), 16):
        binary = " ".join(["%02X" % x for x in data[i:i+16]])
        text = "".join(chr(x) if 0x20 <= x <= 0x7E else "." for x in data[i:i+16])
        result.append("[%04X] %-48s    %s" % (i, binary, text))
    print("\n".join(result))

def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    """サーバー処理"""

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server.bind((local_host, local_port))

    except Exception as e:
        print('[!!] Failed to listen on {}:{}'.format(local_host, local_port))
        print('[!!] Check for other listening sockets or correct permissions.')
        print('[!!] Error:', e)
        sys.exit(0)

    print('[*] Listening on {}:{}'.format(local_host, local_port))
    server.listen(5)

    while True:
        client_socket, addr = server.accept()
        print('[==>] Recerived incoming connection from {}:{}'.format(addr[0], addr[1]))

        proxy_thread = threading.Thread(
            target=proxy_handler,
            args=(client_socket, remote_host, remote_port, receive_first)
        )
        proxy_thread.start()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("localhost", type=str)
    parser.add_argument("localport", type=int)
    parser.add_argument("remotehost", type=str)
    parser.add_argument("remoteport", type=int)
    parser.add_argument("-r", "--receive_first", action='store_true')

    args = parser.parse_args()

    server_loop(
        args.localhost,
        args.localport,
        args.remotehost,
        args.remoteport,
        args.receive_first,
    )
    

if __name__ == '__main__':
    main()