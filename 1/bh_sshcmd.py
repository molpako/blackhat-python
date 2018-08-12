"""
sshを用いて通信をトンネリングして検知を逃れるための
Paramikoを使ったリバーストンネリングスクリプト
"""
import paramiko


def ssh_command(ip, port, user, passwd, command):
    client = paramiko.SSHClient()
    #client.load_host_keys('')
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, port=port, username=user, password=passwd)
    ssh_session = client.get_transport().open_session()
    if ssh_session.active:
        ssh_session.exec_command(command)
        print(ssh_session.recv(1024).decode())
    
    return

def main():
    ssh_command('127.0.0.1', '32768', 'root', 'screencast', 'pwd')

if __name__ == '__main__':
    main()