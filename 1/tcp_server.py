import socket
import threading


BIND_IP = "0.0.0.0"
BIND_PORT = 9999

def handle_client(client_socket):
    """クライアントからの接続を処理するスレッド"""

    # クライアントが送信してきたデータを表示
    request = client_socket.recv(1024)
    print("[*] Recerived: {}".format(request))

    # パケットの返送
    client_socket.send(b"ACK!")
    client_socket.close()


if __name__ == '__main__':
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((BIND_IP, BIND_PORT))

    # 接続キューの最大数を5として接続の待受を開始する
    server.listen(5)
    print("[*] Listening on {}:{}".format(BIND_IP, BIND_PORT))

    while True:
        # client: クライアントソケットオブジェクト
        # addr: クライアントの接続情報
        client, addr = server.accept()
        print("[*] Accept connection from: {}:{}".format(addr[0], addr[1]))

        # 受信データを処理するスレッドの起動
        client_handler = threading.Thread(target=handle_client, args=(client,))
        client_handler.start()
    