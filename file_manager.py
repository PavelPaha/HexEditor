import curses

keys = [curses.KEY_DOWN, curses.KEY_UP, curses.KEY_LEFT, curses.KEY_RIGHT, ord('s')]


def parse_data_to_lines(data):
    result = []
    for i in range(0, len(data), 16):
        result_i = []
        for j in data[i:i + 16]:
            item = format(j, 'x')
            if len(item) == 1:
                item = '0' + item
            result_i += [item]
        result += [result_i]
    return result


class FileManager:
    def __init__(self):
        self.offset = 0
        self.seek_pointer = 0
        self.window_size = 16 * 5
        with open('t.txt', 'rb') as f:
            self.data = f.read(self.window_size)

        self.seek_pointer = len(self.data)

        self.lines = parse_data_to_lines(self.data)
        self.cursor_row = 0
        self.cursor_col = 0

    def get_formatted_lines(self):
        return [' '.join(str(line[i]) for i in range(0, len(line))) for line in self.lines]

    def get_actual_position(self):
        return self.cursor_row, self.cursor_col * 3, self.lines[self.cursor_row][self.cursor_col]

    def get_window_size(self):
        return sum(len(line) for line in self.lines)

    def step_forward_window(self):
        with open('t.txt', 'rb') as f:
            f.seek(self.seek_pointer)
            data = f.read(16)
            self.seek_pointer += len(data)
            if len(data) > 0:
                lines = parse_data_to_lines(data)
                self.lines = self.lines[1:] + lines
                return True
            return False

    def step_back_window(self):
        with open('t.txt', 'rb') as f:
            sz = self.get_window_size()
            if self.seek_pointer >= sz + 16:
                self.seek_pointer -= sz + 16
                f.seek(self.seek_pointer)
                data = f.read(16)

                lines = parse_data_to_lines(data)
                self.lines = lines + self.lines[:-1]
                self.seek_pointer += self.get_window_size()
                return True
            return False

    def translate_lines_to_bytes(self):
        byte_data = []
        for line in self.lines:
            hex_data = ''.join(line)
            byte_data += bytes.fromhex(hex_data)
        return byte_data

    def process_keys(self, key):
        if key in keys:
            self.offset = 0
            if key == curses.KEY_DOWN:
                if self.cursor_row + 1 >= len(self.lines):
                    if not self.step_forward_window():
                        self.cursor_row = 0
                else:
                    self.cursor_row += 1
            elif key == curses.KEY_UP:
                if self.cursor_row == 0:
                    if not self.step_back_window():
                        self.cursor_row = len(self.lines) - 1
                else:
                    self.cursor_row -= 1
            elif key == curses.KEY_LEFT:
                self.cursor_col -= 1
                if self.cursor_col < 0:
                    self.step_back_window()
                    self.cursor_row = (self.cursor_row - 1 + len(self.lines)) % len(self.lines)
                    self.cursor_col = len(self.lines[self.cursor_row]) - 1
            elif key == curses.KEY_RIGHT:
                self.cursor_col += 1
                if self.cursor_col >= len(self.lines[self.cursor_row]):
                    if self.cursor_row + 1 < len(self.lines):
                        self.cursor_row += 1
                        self.cursor_col = 0
            elif key == ord('s'):
                self.save_file()

    def save_file(self):
        b = self.translate_lines_to_bytes()
        with open('t.txt', 'rb+') as f:
            bb = bytes(b)
            f.seek(self.seek_pointer - self.get_window_size())
            f.write(bytes(b))

    def change_data(self, key):
        if key not in keys:
            if ord('0') <= key <= ord('9'):
                key -= ord('0')
            elif ord('a') <= key <= ord('f'):
                key = key - ord('a') + 10
            val = format(key, 'x')
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

# t = FileManager()
#
# verdict = False
# while True:
#     d = input()
#     if d == 'b':
#         verdict = t.step_back_window()
#     elif d == 's':
#         t.save_file()
#     else:
#         verdict = t.step_forward_window()
