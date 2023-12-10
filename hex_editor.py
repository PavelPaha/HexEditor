import curses
from curses import wrapper
from file_manager import FileManager

keys = [curses.KEY_DOWN, curses.KEY_UP, curses.KEY_LEFT, curses.KEY_RIGHT, ord('s')]


def invert_hex(hex_value):
    inverted_hex = f"\033[7m{hex_value}\033[0m"
    return inverted_hex


class HexEditor:
    def __init__(self, file_path):
        self.file_manager = FileManager(file_path)
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
            if not self.begin:
                self.file_manager.change_data(self.key)
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
            # if self.key == ord('s') or self.key == ord('S'):
            #     self.display_popup(stdscr, "Save File")
            if self.key == ord('q') or self.key == ord('Q'):
                return
            self.file_manager.process_keys(self.key)

    def display_popup(self, stdscr, popup_text):
        popup_height = 10
        popup_width = len(popup_text) + 4
        screen_height, screen_width = stdscr.getmaxyx()
        popup_y = (screen_height - popup_height) // 2
        popup_x = (screen_width - popup_width) // 2
        popup_win = curses.newwin(popup_height, popup_width, popup_y, popup_x)
        popup_win.box()
        popup_win.addstr(2, 2, popup_text, curses.A_BOLD)
        popup_win.refresh()
        stdscr.timeout(2)

        del popup_win
    def run(self):
        wrapper(self.main_loop)
