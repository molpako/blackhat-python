import socket
import sys
import paramiko
import threading

host_key = paramiko.RSAKey(filename='test_rsa.key')

class Server(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()
    
    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
    
    def check_auth_password(self, username, password):
        if username == 'root' and password == 'screencast':
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

def main():
    server = sys.argv[1]
    ssh_port = int(sys.argv[2])

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((server, ssh_port))
        sock.listen(100)
        print('[+] Listening for connection...')
        client, addr = sock.accept()

    except Exception as e:
        print('[-] Listen failed:', e)
        sys.exit(1)

    print('[+] Got a connection!')

    try:
        bhSession = paramiko.Transport(client)
        bhSession.add_server_key(host_key)
        server = Server()
        try:
            bhSession.start_server(server=server)

        except paramiko.SSHException as e:
            print('[-] SSH negotiation failed.')
 
        chan = bhSession.accept(20)
        if not chan:
            print('[!] no channel is opened before the given timeout')
            
        print('[+] Authenticated!')
        print(chan.recv(1024).decode())
        chan.send(b'Welcome to bh_ssh')

        while True:
            try:
                command = input("Enter command: ").strip('\n').encode()
                if command != b'exit':
                    chan.send(command)
                    print(chan.recv(1024).decode() + '\n')
                else:
                    chan.send(b'exit')
                    print('exiting')
                    bhSession.close()
                    raise Exception('exit')
            except KeyboardInterrupt:
                bhSession.close()
    except Exception as e:
        print('[-] Caught exception:', e)
        try:
            bhSession.close()
        except:
            pass
        sys.exit(1)
                    
if __name__ == '__main__':
    main()