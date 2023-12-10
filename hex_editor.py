import curses
import time
from curses import wrapper
from file_manager import FileManager

keys = [curses.KEY_DOWN, curses.KEY_UP, curses.KEY_LEFT, curses.KEY_RIGHT, ord('s')]


def invert_hex(hex_value):
    inverted_hex = f"\033[7m{hex_value}\033[0m"
    return inverted_hex


class HexEditor:
    def __init__(self, file_path, width, height, notation):
        self.width = width
        self.height = height
        self.file_manager = FileManager(file_path, width, height, notation)
        self.key = None
        self.begin = True


    def main_loop(self, stdscr):
        stdscr.clear()
        # filepath = input("Введите путь к файлу: ")
        # try:
        #     self.file_manager = FileManager(filepath)
        # except FileNotFoundError:
        #     stdscr.addstr(0, 0, "Файл не найден")
        #     stdscr.getch()
        #     return

        while True:
            stdscr.clear()
            # if not self.begin and self.key != ord('s'):
            #     self.file_manager.change_data(self.key)
            self.begin = False
            formatted_lines = self.file_manager.get_formatted_lines()
            for i in range(len(formatted_lines)):
                line = formatted_lines[i].replace('\x00', '')
                stdscr.addstr(i+1, 0, line)

            try:
                stdscr.addstr(*self.file_manager.get_actual_position(),
                              curses.A_REVERSE)
            except:
                args = self.file_manager.get_actual_position()
                stdscr.addstr(args[0], args[1], ' ', curses.A_REVERSE)

            navigation_bar = "[S] Save File  [Q] Quit"
            stdscr.addstr(0, 0, navigation_bar, curses.A_BOLD)

            stdscr.refresh()
            self.key = stdscr.getch()
            if self.key == ord('q') or self.key == ord('Q'):
                return

            if self.key == ord('s'):
                curses.curs_set(False)
                curses.start_color()
                curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
                message = "Файл сохранён"
                height, width = 5, len(message) + 4
                y, x = self.height // 3, (self.width * 3)//2

                win = curses.newwin(height, width, y, x)

                win.bkgd(' ', curses.color_pair(1))
                win.box()
                win.addstr(height // 2, (width - len(message)) // 2, message)
                win.refresh()

                time.sleep(2)

                win.clear()
                curses.curs_set(True)
                curses.endwin()
                del win
            self.file_manager.process_keys(self.key)


    def run(self):
        wrapper(self.main_loop)
