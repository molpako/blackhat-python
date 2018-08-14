"""
ローカルのWordPressからファイルやディレクトリ構成を参考にして
インストール用ファイルや .htaccessによって守られているディレクトリなど
その他攻撃の足がかりとなる情報を得るためのスキャナー
"""
import queue
import threading
import os
# pip install requests
import requests


threads = 10
# define your target
# target = 'http://blackhatpython.com/
# directory = '/User/justin/Downloads/joomla-3.1.1'
target = ''
directory = ''
fileters = ('.jpg', '.gif', '.png', '.css')


def test_remote(web_paths):
    """キューからパスを取り出し、ターゲットのwebパスにリクエストを送り
    ファイルの取得に成功したら出力する。失敗した場合はスルーする
    """

    while not web_paths.empty():
        path = web_paths.get()
        url = '{}/{}'.format(target, path)

        try:
            res = requests.get(url)
            code = res.status_code

            print('[{}] => {}'.format(code, path))
            res.close()

        except requests.HTTPError as err:
            print('Failed:', err)
            # pass

def main():
    os.chdir(directory)
    web_paths = queue.Queue()

    # _ is dirnames
    for dirpaths, _, filenames in os.walk('.'):
        for files in filenames:
            remote_path = '{}/{}'.format(dirpaths, files)

            if remote_path.startswith('.'):
                remote_path = remote_path[1:]

            if os.path.splitext(files)[1] not in fileters:
                web_paths.put(remote_path)

    for i in range(threads):
        print('Spawning thread: {}'.format(i))

        thread = threading.Thread(
            target=test_remote,
            args=(web_paths,),
        )

        thread.start()

if __name__ == '__main__':
    main()
