import curses
from curses import wrapper
from file_manager import FileManager

keys = [curses.KEY_DOWN, curses.KEY_UP, curses.KEY_LEFT, curses.KEY_RIGHT, ord('s')]


def invert_hex(hex_value):
    inverted_hex = f"\033[7m{hex_value}\033[0m"
    return inverted_hex


class HexEditor:
    def __init__(self):
        self.file_manager = FileManager()
        self.seek_pointer = 0
        self.window_size = 16 * 5
        self.offset = 0
        with open('t.txt', 'rb') as f:
            self.data = f.read(self.window_size)

        self.seek_pointer = len(self.data)

        self.key = None
        self.begin = True

    def main_loop(self, stdscr):
        stdscr.clear()
        while True:
            stdscr.clear()
            if not self.begin:
                self.file_manager.change_data(self.key)
            self.begin = False
            formatted_lines = self.file_manager.get_formatted_lines()
            for i in range(len(formatted_lines)):
                stdscr.addstr(i, 0, formatted_lines[i])
            # print(self.lines[self.cursor_row][self.cursor_col * 2])
            # print(len(self.lines), self.cursor_row)

            # if self.cursor_col >= len(self.lines[self.cursor_row]):
            #     self.cursor_row = 0
            #     self.cursor_col = 0
            stdscr.addstr(*self.file_manager.get_actual_position(),
                          curses.A_REVERSE)
            stdscr.refresh()
            self.key = stdscr.getch()
            self.file_manager.process_keys(self.key)


hr = HexEditor()

wrapper(hr.main_loop)
