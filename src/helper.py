import textwrap
import sys
import os
import re

# ---------------------
#    Helper methods
# ---------------------


# Wrap text at terminal_width - 20 and indent it an amount.
def wrap_indent(text, amount, first=' ', ch=' '):
    width = terminal_width() - 20
    width = width if width > 0 else 60
    wraptext = textwrap.fill(text, width)
    padding = first + ((amount-1) * ch)
    return ''.join(padding+line for line in wraptext.splitlines(True))


# Convert text to an int, return default on fail.
def int_parse(text, default=0):
    try:
        return int(text)
    except Exception:
        return default


# Return text if it's in selection, default otherwise.
def str_parse(text, selection, default):
    if (text in selection):
        return text
    return default


def date_parse(text):
    date_regex = r"^[\d]{4}-[\d]{2}-[\d]{2}$"
    match = re.match(date_regex, text)
    if match:
        return True
    return False


# Return the width of the terminal, defaults to 80 if an error occurs.
# To be used when wrapping text and printing horisontal lines.
def terminal_width():
    try:
        columns, _ = os.get_terminal_size()
    except OSError:
        columns = 80
    return columns


# This makes it possible to inculde the sql script when making a standalone
# executable with PyInstaller
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.environ.get("_MEIPASS2", os.path.abspath("."))
    return os.path.join(base_path, relative_path)


# Prints the menu in two columns
def print_menu(menu):
    if (len(menu) % 2 == 1):
        menu += ['']

    longest = max([len(menu[i]) for i in range(0, len(menu)//2)])

    for i in range(len(menu)//2):

        # 1: <- i  4: <- next_index
        # 2: ....  5: ...
        # 3: ....  6: ...
        # 4 = 6 // 2 + 1
        next_index = len(menu)//2 + i

        # Add spacing between the two colums so that everything is aligned
        spaces = ' '*(longest - len(menu[i])) + '\t'

        # Add the first menu item.
        line = str(i) + ': ' + menu[i] + spaces

        # Don't print the second column if the element is an empty string
        if (menu[next_index] != ''):
            # Add the second menu item
            line += str(next_index) + ': ' + menu[next_index]

        print(line)


# Execute an SQL-script
def execute_script(db, filename):
    cursor = db.cursor()
    with open(resource_path(filename), 'r') as f:
        sql_file = f.read()
        f.close()

    sql_commands = sql_file.split(';')

    for command in sql_commands:
        try:
            cursor.execute(command)
        except Exception:
            pass
