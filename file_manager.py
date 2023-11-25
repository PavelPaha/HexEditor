import curses

keys = [curses.KEY_DOWN, curses.KEY_UP, curses.KEY_LEFT, curses.KEY_RIGHT, ord('s'), ord('y')]


def parse_data_to_lines(data):
    result = []
    for i in range(0, len(data), 16):
        result_i = parse_data_to_line(data[i:i + 16])
        result += [result_i]
    return result


def parse_data_to_line(data):
    result_i = []
    for j in data:
        item = format(j, 'x')
        if len(item) == 1:
            item = '0' + item
        result_i += [item]
    return result_i


def convert_to_number(key):
    if ord('0') <= key <= ord('9'):
        key -= ord('0')
    elif ord('a') <= key <= ord('f'):
        key = key - ord('a') + 10
    val = format(key, 'x')
    return val


class FileManager:
    def __init__(self, file_path='t.txt'):
        self.pointer = 0

        self.file_path = file_path
        self.offset = 0
        self.seek_pointer = 0
        self.window_width = 16
        self.window_height = 10
        self.window_size = self.window_width * self.window_height
        with open(file_path, 'rb') as f:
            self.data = f.read(self.window_size)

        self.seek_pointer = len(self.data)

        self.lines = parse_data_to_lines(self.data)
        self.buffer = self.lines
        self.cursor_row = 0
        self.cursor_col = 0
        self.cursor_str_col = 0
        self.rows_offset = 0
        self.in_table = True

    def get_formatted_lines(self):
        result = []
        index = self.pointer + self.rows_offset + 1

        for i in range(self.pointer, min(self.pointer+self.window_height, len(self.lines))):
            line =  self.lines[i]
            result_i1 = []
            result_i2 = b''
            binary_number = (hex(index)[2:] + '0').rjust(8, '0')

            for item in line:
                if '_' in item:
                    result_i1.append(item)
                    continue
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
        row_number = self.pointer + self.cursor_row
        l = len(self.lines[row_number])
        if self.cursor_col >= len(self.lines[row_number]):
            answer = self.lines[row_number][self.cursor_col - l]
            if '_' in answer:
                value = ' '
            else:
                value = str(bytes([int(answer, 16)]).decode('utf-8', errors='replace'))
            return self.cursor_row+1, self.window_width * 3 + 9 + self.cursor_col - l, value
        return self.cursor_row+1, self.cursor_col * 3 + 9, self.lines[row_number][self.cursor_col]

    def get_window_size(self):
        return sum(len(line) for line in self.lines)

    def step_forward_window(self, last_row_contains_empty_cells=False):
        with open(self.file_path, 'rb') as f:
            f.seek(self.seek_pointer)
            right = 0
            if last_row_contains_empty_cells:
                for i in range(self.window_width):
                    if '_' not in self.lines[self.pointer+self.cursor_row+1][i]:
                        right = i
                    else:
                        break

                data = parse_data_to_line(f.read(self.window_width-right-1))

                self.shift_right_and_insert_at_index(2*(right+1), self.pointer+self.cursor_row+1, ''.join(data))
            else:
                data = f.read(self.window_width)
                last_line = parse_data_to_line(data)
                while len(last_line) < self.window_width:
                    last_line += ['__']
                self.lines += [last_line]
                self.pointer += 1
            self.seek_pointer += len(data)

    def step_back_window(self):
        self.pointer = max(0, self.pointer - 1)
        return True

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
            elif key == ord('y'):
                self.insert('111111')

        # if self.cursor_col >= len(self.lines[self.cursor_row]):
        #     self.cursor_row = 0
        #     self.cursor_col = 0

    def shift_cursor_right(self):
        self.cursor_col += 1
        if self.cursor_col >= 2*self.window_width:
            if self.cursor_row + 1 < self.window_height:
                self.cursor_row += 1
                self.cursor_col = 0

    def shift_cursor_left(self):
        self.cursor_col -= 1
        if self.cursor_col < 0:
            self.step_back_window()
            self.cursor_row = (self.cursor_row - 1 + self.window_height) % self.window_height
            self.cursor_col = 2*self.window_width - 1

    def shift_cursor_up(self):
        if self.cursor_row == 0:
            self.step_back_window()
        else:
            self.cursor_row -= 1

    def shift_cursor_down(self):
        if self.pointer + self.cursor_row+1 == len(self.lines) -1 and any('_' in i for i in self.lines[self.pointer + self.cursor_row+1]):
            self.step_forward_window(True)
            return
        if self.cursor_row + 1 < self.window_height:
            self.cursor_row += 1
        elif self.pointer + self.cursor_row + 1 < self.window_height:
            self.pointer += 1
        else:
            self.step_forward_window(False)
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
        return self.lines[self.cursor_row+self.pointer][self.cursor_col % self.window_width]

    def set_cur_val(self, new_val):
        self.lines[self.cursor_row+self.pointer][self.cursor_col % self.window_width] = new_val

    def insert(self, data):
        if len(self.lines) == self.window_height:
            self.lines += [['__' for _ in range(self.window_width)]]
        for i in range(len(self.lines)-1, self.pointer + self.cursor_row, -1):
            str = ''.join(self.lines[i - 1])
            d = str[-len(data):]
            self.shift_right_and_insert_at_index(0, i, d)
        self.shift_right_and_insert_at_index(2*(self.cursor_col % self.window_width), self.pointer + self.cursor_row, data)

    def shift_right_and_insert_at_index(self, index, row_number, data):
        string = ''.join(self.lines[row_number])
        newstr = string[:index] + data + string[index:]
        self.lines[row_number] = [newstr[i:i + 2] for i in range(0, self.window_width * 2, 2)]

t = FileManager()

t.get_formatted_lines()
t.insert('111111')
t.shift_cursor_down()
t.shift_cursor_down()
t.shift_cursor_down()
#
