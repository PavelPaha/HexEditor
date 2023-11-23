import argparse
from hex_editor import HexEditor


def parse_arguments():
    parser = argparse.ArgumentParser(description='Hex Editor')
    parser.add_argument('file', type=str, help='Path to the file')
    args = parser.parse_args()
    return args


def main():
    args = parse_arguments()
    file_path = args.file

    hr = HexEditor(file_path)
    hr.run()


if __name__ == '__main__':
    main()
