import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-l', '--listen', action='store_true')
args = parser.parse_args()

print(args.l)


