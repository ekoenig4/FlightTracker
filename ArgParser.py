from argparse import ArgumentParser

parser = ArgumentParser()

def parse_args():
    parser.args = ArgumentParser.parse_args(parser)
    return parser.args
parser.parse_args = parse_args
