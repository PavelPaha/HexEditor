import curses

keys = [curses.KEY_CONTROL_L, curses.KEY_DOWN, curses.KEY_UP, curses.KEY_LEFT, curses.KEY_RIGHT, ord('s'), ord('z')]



class FileManager:
    def __init__(self, file_path='t.txt', width=10, height=16, notation='hex'):
        self.undo_stack = []
        self.notation = notation
        self.pointer = 0
        self.file_path = file_path
        self.offset = 0
        self.seek_pointer = 0
        self.window_width = width
        self.window_height = height
        self.window_size = self.window_width * self.window_height
        self.cursor_row = 0
        self.cursor_col = 0
        self.cursor_str_col = 0
        self.rows_offset = 0
        self.in_table = True

        with open(file_path, 'rb') as f:
            self.data = f.read(self.window_size)
        self.seek_pointer = len(self.data)
        self.lines = self.parse_data_to_lines(self.data)
        if len(self.lines) == 0:
            self.lines += [[]]
        last_line = self.lines[-1]
        while len(last_line) < self.window_width:
            last_line += ['__']
        self.lines[-1] = last_line

        # self.step_forward_window(True)
        while len(self.lines) < self.window_height:
            self.step_forward_window(False)
        self.pointer = 0
        self.buffer = self.lines

    def get_formatted_lines(self):
        result = []
        index = self.pointer + self.rows_offset + 1

        for i in range(self.pointer, self.pointer + self.window_height):
            line = self.lines[i]
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
            formatted_line = binary_number + ' ' + ' '.join(result_i1).ljust(self.window_width*3)
            formatted_line += ''.join(
                [bytes([item]).decode('utf-8', errors='replace') if ord(b'\x20') <= item <= ord(b'\x7E') else '.' for
                 item in result_i2])

            result.append(formatted_line)
        return result

    def get_actual_position(self):
        l = len(self.lines[self.cursor_row + self.pointer])
        if self.cursor_col >= len(self.lines[self.cursor_row]):
            answer = self.lines[self.get_pos_y()][self.cursor_col - l]
            if '_' in answer:
                value = ' '
            else:
                value = str(bytes([int(answer, 16)]).decode('utf-8', errors='replace'))
            return self.cursor_row + 1, self.window_width * 3 + 9 + self.cursor_col - l, value
        return self.cursor_row + 1, self.cursor_col * 3 + 9, self.lines[self.get_pos_y()][self.get_pos_x()]

    def get_window_size(self):
        return sum(len(line) for line in self.lines)

    def step_forward_window(self, last_row_contains_empty_cells=False):
        with open(self.file_path, 'rb') as f:
            f.seek(self.seek_pointer)
            right = 0
            if last_row_contains_empty_cells:
                for i in range(self.window_width):
                    cr = self.cursor_row
                    if '_' not in self.lines[self.pointer + cr + 1][i]:
                        right = i
                    else:
                        break
                data = self.parse_data_to_line(f.read(self.window_width - right - 1))
                self.shift_right_and_insert_at_index(2 * (right + 1), self.pointer + self.cursor_row + 1, ''.join(data))
            else:
                data = f.read(self.window_width)
                last_line = self.parse_data_to_line(data)
                while len(last_line) < self.window_width:
                    last_line += ['__']
                self.lines += [last_line]
                self.pointer += 1
            self.seek_pointer += len(data)

    def step_back_window(self):
        self.pointer = max(0, self.pointer - 1)
        return True

    def translate_buffer_to_bytes(self):
        byte_data = []
        for line in self.buffer:
            hex_data = ''.join(line).replace('_','')
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
            # elif key == curses.KEY_CONTROL_L and key == ord('v'):
            #     self.insert('111111')
            elif key == ord('z'):
                self.undo()
        else:
            self.change_data(key)
                # self.insert('111111')

        # if self.cursor_col >= len(self.lines[self.cursor_row]):
        #     self.cursor_row = 0
        #     self.cursor_col = 0

    def shift_cursor_right(self):
        self.cursor_col += 1
        if self.cursor_col >= 2 * self.window_width:
            if self.cursor_row + 1 <= self.window_height:
                self.shift_cursor_down()
                self.cursor_col = 0

    def shift_cursor_left(self):
        self.cursor_col -= 1
        if self.cursor_col < 0:
            self.step_back_window()
            self.cursor_row = (self.cursor_row - 1 + self.window_height) % self.window_height
            self.cursor_col = 2 * self.window_width - 1

    def shift_cursor_up(self):
        if self.cursor_row == 0:
            self.step_back_window()
        else:
            self.cursor_row -= 1

    def shift_cursor_down(self):
        if self.cursor_row + 1 < self.window_height:
            self.cursor_row += 1
            return
        if self.pointer + self.cursor_row + 1 == len(self.lines) - 1 and any(
                '_' in i for i in self.lines[self.pointer + self.cursor_row + 1]):
            self.step_forward_window(True)

            return
        self.step_forward_window(False)
        # elif self.pointer + self.cursor_row + 1 < self.window_height:
        #     self.pointer += 1
        #

    def save_file(self):
        b = self.translate_buffer_to_bytes()
        with open(self.file_path, 'rb+') as f:
            f.seek(0)
            f.write(bytes(b))

    def change_data(self, key):
        new_val = self.convert_to_number(key)
        if new_val is None:
            return
        cur_val = self.get_cur_val()
        self.undo_stack += [([self.get_pos_y(), self.get_pos_x()], cur_val)]
        if self.offset == 0:
            self.set_cur_val(new_val + cur_val[1:2])
        elif self.offset == 1:
            self.set_cur_val(cur_val[0:1] + new_val)
            self.shift_cursor_right()
            if self.cursor_col == self.window_width:
                self.shift_cursor_down()
                self.cursor_col = 0
            # self.offset = 0
        self.offset = (self.offset + 1) % 2

    def get_pos_y(self):
        return self.cursor_row + self.pointer

    def get_pos_x(self):
        return self.cursor_col % self.window_width

    def get_cur_val(self):
        return self.lines[self.get_pos_y()][self.get_pos_x()]

    def set_cur_val(self, new_val, y=None, x=None):
        if x is None and y is None:
            y = self.get_pos_y()
            x = self.get_pos_x()
        self.lines[y][x] = new_val
        for j in range(x, -1, -1):
            self.lines[y][j] = self.lines[y][j].replace('_', '0')
        for i in range(y - 1, -1, -1):
            for j in range(self.window_width - 1, -1, -1):
                self.lines[i][j] = self.lines[i][j].replace('_', '0')

    def insert(self, data):
        return
        if len(self.lines) == self.window_height:
            self.lines += [['__' for _ in range(self.window_width)]]
        for i in range(len(self.lines) - 1, self.pointer + self.cursor_row, -1):
            str = ''.join(self.lines[i - 1])
            d = str[-len(data):]
            self.shift_right_and_insert_at_index(0, i, d)
        self.shift_right_and_insert_at_index(2 * (self.cursor_col % self.window_width), self.pointer + self.cursor_row,
                                             data)

    def shift_right_and_insert_at_index(self, index, row_number, data):
        string = ''.join(self.lines[row_number])
        newstr = string[:index] + data + string[index:]
        self.lines[row_number] = [newstr[i:i + 2] for i in range(0, self.window_width * 2, 2)]

    def parse_data_to_lines(self, data):
        result = []
        for i in range(0, len(data), self.window_width):
            result_i = self.parse_data_to_line(data[i:i + self.window_width])
            result += [result_i]
        return result

    def parse_data_to_line(self, data):
        result_i = []
        for j in data:
            if self.notation == 'hex':
                item = format(j, 'x')
            elif self.notation == 'oct':
                item = oct(j)[2:]
            elif self.notation == 'bin':
                item = bin(j)[2:]
            else:
                item = str(j)
            if len(item) == 1:
                item = '0' + item
            result_i += [item]
        return result_i

    def undo(self):
        top = self.undo_stack[-1]
        self.undo_stack = self.undo_stack[:-1]
        (y, x) = top[0]
        val = top[1]
        self.set_cur_val(val, x=x, y=y)

    chars_by_notation = {
        'bin': list(range(2)),
        'oct': list(range(8)),
        'dec': list(range(10)),
        'hex': list(range(16))
    }

    def convert_to_number(self, key):
        if ord('0') <= key <= ord('9'):
            key -= ord('0')
        elif ord('a') <= key <= ord('f'):
            key = key - ord('a') + 10
        val = format(key, 'x')
        if key in self.chars_by_notation[self.notation]:
            return val
        # raise ValueError(key)


# t = FileManager('e1231.txt')
# t.process_keys(ord('s'))
# t.process_keys(curses.KEY_DOWN)
#
# t.change_data(ord('f'))
# t.process_keys(ord('z'))
# t.process_keys(ord('z'))
# # t.get_formatted_lines()
# # t.insert('caccac')
# # t.change_data(ord('4'))
# # t.shift_cursor_down()
# # t.shift_cursor_down()
# # t.shift_cursor_down()
# # #
