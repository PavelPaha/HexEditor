import argparse
import os.path

from hex_editor import HexEditor


def parse_arguments():
    parser = argparse.ArgumentParser(description='Hex Editor')
    parser.add_argument('--notation', '-n', type=str, default='hex', choices=['bin', 'oct', 'dec', 'hex'], help='Notation')
    parser.add_argument('--width', '-w', type=int, default=10, help='Window width')
    parser.add_argument('--height', type=int, default=10, help='Window height')
    parser.add_argument('file', type=str, default='t.txt', help='Path to the file')
    args = parser.parse_args()
    return args


def main():
    args = parse_arguments()
    file_path = args.file
    notation = args.notation
    width = args.width
    height = args.height

    if not os.path.exists(file_path):
        open(file_path, 'w')
    hr = HexEditor(file_path, width, height, notation)
    hr.run()


if __name__ == '__main__':
    main()
