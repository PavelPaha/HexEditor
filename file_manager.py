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


def convert_to_number(key):
    if ord('0') <= key <= ord('9'):
        key -= ord('0')
    elif ord('a') <= key <= ord('f'):
        key = key - ord('a') + 10
    val = format(key, 'x')
    return val


class FileManager:
    def __init__(self, file_path='t.txt'):
        self.file_path = file_path
        self.offset = 0
        self.seek_pointer = 0
        self.window_size = 16 * 18
        with open(file_path, 'rb') as f:
            self.data = f.read(self.window_size)

        self.seek_pointer = len(self.data)

        self.lines = parse_data_to_lines(self.data)
        self.cursor_row = 0
        self.cursor_col = 0
        self.cursor_str_col = 0
        self.rows_offset = 0
        self.in_table = True

    def get_formatted_lines(self):
        result = []
        index = self.rows_offset + 1

        for line in self.lines:
            result_i1 = []
            result_i2 = b''
            binary_number = (hex(index)[2:] + '0').rjust(8, '0')

            for item in line:
                ord_value = int(item, 16)
                result_i1.append(item)
                try:
                    result_i2 += bytes([ord_value])
                except UnicodeDecodeError:
                    result_i2 += b'?'

            index += 1
            formatted_line = binary_number + ' ' + ' '.join(result_i1).ljust(48)
            formatted_line += ''.join(
                [bytes([item]).decode('utf-8', errors='replace') if ord(b'\x20') <= item <= ord(b'\x7E') else '.' for
                 item in result_i2])

            result.append(formatted_line)

        return result

    def get_actual_position(self):
        l = len(self.lines[self.cursor_row])
        if self.cursor_col >= len(self.lines[self.cursor_row]):
            answer = self.lines[self.cursor_row][self.cursor_col - l]
            ord_value = int(answer, 16)
            return self.cursor_row+1, len(self.lines[self.cursor_row]) * 3 + 9 + self.cursor_col - l, str(bytes([ord_value]).decode('utf-8', errors='replace'))
        return self.cursor_row+1, self.cursor_col * 3 + 9, self.lines[self.cursor_row][self.cursor_col]

    def get_window_size(self):
        return sum(len(line) for line in self.lines)

    def step_forward_window(self):
        with open(self.file_path, 'rb') as f:
            f.seek(self.seek_pointer)
            data = f.read(16)
            self.seek_pointer += len(data)
            if len(data) > 0:
                lines = parse_data_to_lines(data)
                self.lines = self.lines[1:] + lines
                self.rows_offset += 1
                return True
            return False

    def step_back_window(self):
        with open(self.file_path, 'rb') as f:
            sz = self.get_window_size()
            if self.seek_pointer >= sz + 16:
                self.seek_pointer -= sz + 16
                f.seek(self.seek_pointer)
                data = f.read(16)

                lines = parse_data_to_lines(data)
                self.lines = lines + self.lines[:-1]
                self.seek_pointer += self.get_window_size()
                self.rows_offset -= 1
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
                self.shift_cursor_down()
            elif key == curses.KEY_UP:
                self.shift_cursor_up()
            elif key == curses.KEY_LEFT:
                self.shift_cursor_left()
            elif key == curses.KEY_RIGHT:
                self.shift_cursor_right()
            elif key == ord('s'):
                self.save_file()

        if self.cursor_col >= 2 * len(self.lines[self.cursor_row]):
            self.cursor_row = 0
            self.cursor_col = 0

    def shift_cursor_right(self):
        self.cursor_col += 1
        if self.cursor_col >= 2 * len(self.lines[self.cursor_row]):
            if self.cursor_row + 1 < len(self.lines):
                self.cursor_row += 1
                self.cursor_col = 0

    def shift_cursor_left(self):
        self.cursor_col -= 1
        if self.cursor_col < 0:
            self.step_back_window()
            self.cursor_row = (self.cursor_row - 1 + len(self.lines)) % len(self.lines)
            self.cursor_col = len(self.lines[self.cursor_row]) - 1

    def shift_cursor_up(self):
        if self.cursor_row == 0:
            if not self.step_back_window():
                self.cursor_row = len(self.lines) - 1
        else:
            self.cursor_row -= 1

    def shift_cursor_down(self):
        if self.cursor_row + 1 >= len(self.lines):
            if not self.step_forward_window():
                self.cursor_row = 0
        else:
            self.cursor_row += 1

    def save_file(self):
        b = self.translate_lines_to_bytes()
        with open(self.file_path, 'rb+') as f:
            f.seek(self.seek_pointer - self.get_window_size())
            f.write(bytes(b))

    def change_data(self, key):
        if key not in keys:
            new_val = convert_to_number(key)
            if self.offset == 0:
                cur_val = self.get_cur_val()
                self.set_cur_val(new_val + cur_val[1:2])
            elif self.offset == 1:
                cur_val = self.get_cur_val()
                self.set_cur_val(cur_val[0:1] + new_val)
                self.set_cur_val(cur_val[0:1] + new_val)
            self.offset = (self.offset + 1) % 2

    def get_cur_val(self):
        return self.lines[self.cursor_row][self.cursor_col % len(self.lines[self.cursor_row])]

    def set_cur_val(self, new_val):
        self.lines[self.cursor_row][self.cursor_col % len(self.lines[self.cursor_row])] = new_val

# t = FileManager()
#
# t.get_formatted_lines()
# verdict = False
# while True:
#     d = input()
#     if d == 'b':
#         verdict = t.step_back_window()
#     elif d == 's':
#         t.save_file()
#     else:
#         verdict = t.step_forward_window()
