import argparse

class CliParser:
    def __init__(self, prog:str):
        self.parser = argparse.ArgumentParser(prog=prog)
        self.parser.add_argument('--cfg', help='path to config of the %(prog)s program')

    def __call__(self, cli_mock:str = None):
        cli_args = self.parser.parse_args(cli_mock)
        return cli_args
