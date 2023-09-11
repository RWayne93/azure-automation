from argparse import ArgumentParser
from azure.bootstraps.utils import ConfigParser

def main(filepath):
    configs = ConfigParser(filepath)
    for c in configs:
        print(c.resource_group)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-c", required = True, help = "filepath to config file")
    args = parser.parse_args()
    main(args.c)  