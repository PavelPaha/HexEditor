import curses
from curses import wrapper
from file_manager import FileManager

keys = [curses.KEY_DOWN, curses.KEY_UP, curses.KEY_LEFT, curses.KEY_RIGHT, ord('s')]


def invert_hex(hex_value):
    inverted_hex = f"\033[7m{hex_value}\033[0m"
    return inverted_hex


class HexEditor:
    def __init__(self):
        self.file_manager = None
        self.key = None
        self.begin = True

    def main_loop(self, stdscr):
        stdscr.clear()
        self.file_manager = FileManager()
        # filepath = input("Введите путь к файлу: ")
        # try:
        #     self.file_manager = FileManager(filepath)
        # except FileNotFoundError:
        #     stdscr.addstr(0, 0, "Файл не найден")
        #     stdscr.getch()
        #     return

        while True:
            stdscr.clear()
            if not self.begin:
                self.file_manager.change_data(self.key)
            self.begin = False
            formatted_lines = self.file_manager.get_formatted_lines()
            for i in range(len(formatted_lines)):
                line = formatted_lines[i].replace('\x00', '')
                stdscr.addstr(i, 0, line)


            stdscr.addstr(*self.file_manager.get_actual_position(),
                          curses.A_REVERSE)
            stdscr.refresh()
            self.key = stdscr.getch()
            self.file_manager.process_keys(self.key)


hr = HexEditor()

wrapper(hr.main_loop)
