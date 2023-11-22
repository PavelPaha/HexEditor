import curses
from curses import wrapper
from file_manager import FileManager

keys = [curses.KEY_DOWN, curses.KEY_UP, curses.KEY_LEFT, curses.KEY_RIGHT, ord('s')]


# def invert_hex(hex_value):
#     inverted_hex = f"\033[7m{hex_value}\033[0m"
#     return inverted_hex


class HexEditor:
    def __init__(self):
        self.file_manager = FileManager()
        self.seek_pointer = 0
        self.window_size = 16 * 5
        self.offset = 0
        with open('t.txt', 'rb') as f:
            self.data = f.read(self.window_size)

        self.seek_pointer = len(self.data)

        self.lines = self.parse_data_to_lines(self.data)
        self.cursor_row = 0
        self.cursor_col = 0

        self.key = None
        self.begin = True

    def parse_data_to_lines(self, data):
        return [[format(j, 'x') for j in data[i:i + 16]] for i in range(0, len(data), 16)]

    def step_forward_window(self):
        with open('t.txt', 'rb') as f:
            f.seek(self.seek_pointer)
            data = f.read(16)
            self.seek_pointer += len(data)
            if len(data) > 0:
                lines = self.parse_data_to_lines(data)
                self.lines = self.lines[1:] + lines
                return True
            return False

    def step_back_window(self):
        with open('t.txt', 'rb') as f:
            sm = sum(len(line) for line in self.lines)
            if self.seek_pointer >= sm + 16:
                self.seek_pointer -= sm + 16
                f.seek(self.seek_pointer)
                data = f.read(16)

                lines = self.parse_data_to_lines(data)
                self.lines = lines + self.lines[:-1]
                self.seek_pointer += sum(len(line) for line in self.lines)
                return True
            return False

    def main_loop(self, stdscr):
        stdscr.clear()
        while True:
            stdscr.clear()
            self.change_data()
            self.begin = False
            for i, line in enumerate(self.lines):
                formatted_line = ' '.join(str(line[i]) for i in range(0, len(line)))
                stdscr.addstr(i, 0, formatted_line)
            # print(self.lines[self.cursor_row][self.cursor_col * 2])
            # print(len(self.lines), self.cursor_row)
            if self.cursor_col >= len(self.lines[self.cursor_row]):
                self.cursor_row = 0
                self.cursor_col = 0
            stdscr.addstr(self.cursor_row, self.cursor_col * 3, self.lines[self.cursor_row][self.cursor_col],
                          curses.A_REVERSE)

            stdscr.refresh()
            self.key = stdscr.getch()
            print(self.key, self.key)
            self.process_keys()

    def change_data(self):
        if self.key not in keys and not self.begin:
            if ord('0') <= self.key <= ord('9'):
                self.key -= ord('0')
            elif ord('a') <= self.key <= ord('f'):
                self.key = self.key - ord('a') + 10
            val = format(self.key, 'x')
            print(val)
            # raise EOFError
            if self.offset == 0:
                new_value = self.lines[self.cursor_row][self.cursor_col]
                self.lines[self.cursor_row][self.cursor_col] = val + new_value[1:2]
            elif self.offset == 1:
                new_value = self.lines[self.cursor_row][self.cursor_col]
                self.lines[self.cursor_row][self.cursor_col] = new_value[0:1] + val
                # print(new_value[0:1] + val)
                # raise EOFError
                self.lines[self.cursor_row][self.cursor_col] = new_value[0:1] + val

            self.offset = (self.offset + 1) % 2

    def process_keys(self):
        if self.key in keys:
            self.offset = 0
            if self.key == curses.KEY_DOWN:
                if self.cursor_row + 1 >= len(self.lines):
                    if not self.step_forward_window():
                        self.cursor_row = 0
                else:
                    self.cursor_row += 1
            elif self.key == curses.KEY_UP:
                if self.cursor_row == 0:
                    if not self.step_back_window():
                        self.cursor_row = len(self.lines) - 1
                else:
                    self.cursor_row -= 1
            elif self.key == curses.KEY_LEFT:
                self.cursor_col -= 1
                if self.cursor_col < 0:
                    self.step_back_window()
                    self.cursor_row = (self.cursor_row - 1 + len(self.lines)) % len(self.lines)
                    self.cursor_col = len(self.lines[self.cursor_row]) - 1
            elif self.key == curses.KEY_RIGHT:
                self.cursor_col += 1
                if self.cursor_col >= len(self.lines[self.cursor_row]):
                    if self.cursor_row + 1 < len(self.lines):
                        self.cursor_row += 1
                        self.cursor_col = 0
            elif self.key == ord('s'):
                b = self.translate_lines_to_bytes()
                with open('t.txt', 'wb') as f:
                    f.seek(self.seek_pointer)
                    f.write(bytes(b))

    def translate_lines_to_bytes(self):
        byte_data = []
        for line in self.lines:
            hex_data = ''.join(line)
            byte_data += bytes.fromhex(hex_data)
        return byte_data

hr = HexEditor()

wrapper(hr.main_loop)

