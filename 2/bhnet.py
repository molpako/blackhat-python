"""netcat tool"""
import argparse
import sys
import socket
import threading
import subprocess



DESC = """\
    Examples:
    bhnet.py -t 192.168.0.1 -p 555 -l -c
    bhnet.py -t 192.168.0.1 -p 555 -l -c c:\\target.exe
    bhnet.py -t 192.168.0.1 -p 555 -l -c "cat /etc/passwd"
    echo 'ABCDEF' | ./bhnet.py -t 192.168.0.1 -p 135
    """

def client_sender(buff, target, port):
    """標的ホストにデータを送信し、受信データがなくなるまでデータの受信を行う"""
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((target, port))

        if buff:
            client.send(buff.encode())

        while True:

            recv_len = 1
            response = b""

            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data

                if recv_len < 4096:
                    break

            print(response.decode(), end="")
            # print(response.decode())

            buff = input().encode()
            buff += b"\n"

            client.send(buff)

    except Exception as e:
        print("[*] Exception! Exiting", e)
        client.close()


def server_loop(target, port, upload_destination, execute, command):
    """サーバーのメインループ処理を行う"""
    if not target:
        target = "0.0.0.0"

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))
    server.listen(5)

    while True:
        client_socket, _ = server.accept()

        # クライアントからの新しい接続を処理するスレッドの起動
        client_thread = threading.Thread(
            target=client_handler,
            args=(client_socket, upload_destination, execute, command))
        client_thread.start()

def run_command(command):
    """コマンド実行処理とコマンドシェル処理を扱う"""
    command = command.rstrip()

    try:
        # 渡したコードをそのままローカルOSに渡して実行させる
        output = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True
        )
        output = output.stdout
    except:
        output = "Failed to execute command.\r\n"

    return output

def client_handler(client_socket, upload_destination, execute, command):

    if upload_destination:

        file_buff = ''

        # 全てのデータを受信する
        while True:
            data = client_socket.recv(4096)

            if not data:
                break
            else:
                file_buff += data

        # バイナリファイルをアップロードし、ファイルに書き込む
        try:
            with open(upload_destination, "wb") as f:
                f.write(file_buff)

            client_socket.send(b'Successfully saved file to {}\r\n'.format(upload_destination))


        except:
            client_socket.send(b'Failed to save file to {}\r\n'.format(upload_destination))

    if execute:
        print('execute block')
        output = run_command(execute)
        client_socket.send(output)

    # 送られたコマンドを実行してその結果を送り返す
    if command:
        prompt = b'<BHP:#> '
        client_socket.send(prompt)

        while True:

            cmd_buff = b''
            while b'\n' not in cmd_buff:
                cmd_buff += client_socket.recv(1024)
            response = run_command(cmd_buff)
            response += prompt

            client_socket.send(response)

def main():
    """main関数"""

    parser = argparse.ArgumentParser(description="netcat tool")
    parser.add_argument('-l', '--listen', action='store_true',
                        help="listen on [host]:[port] for incoming connections")
    parser.add_argument('-c', '--command', action='store_true',
                        help="initialize a command shell")
    parser.add_argument('-u', '--upload',
                        help="upon receiving connection upload a file and write to [destination]")
    parser.add_argument('-e', '--execute', default="",
                        help="exectute the given file upon receiving a connection")
    parser.add_argument('-t', '--target', default="", help="target host")
    parser.add_argument('-p', '--port', type=int, default=0, help='target port')

    args = parser.parse_args()

    # 標準入力からデータを受け取ってネットワーク越しに送信する処理を行う
    if not args.listen and args.target and args.port > 0:

        # コマンドラインからの入力を buff に格納する
        # 入力が来ないと処理が継続されないので
        # 標準入力にデータを送らない場合は Ctrl-D を入力すること
        buff = sys.stdin.read()

        # データ送信
        client_sender(buff, args.target, args.port)

    # 接続待機を開始
    # コマンドラインオプションに応じて、ファイルアップロード
    # コマンド実行、コマンドシェルの実行を行う
    if args.listen:
        server_loop(args.target, args.port, args.upload, args.execute, args.command)


if __name__ == '__main__':
    main()
