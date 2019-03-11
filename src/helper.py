import textwrap
import os


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


# Return the width of the terminal, defaults to 80 if an error occurs.
def terminal_width():
    try:
        columns, _ = os.get_terminal_size()
    except OSError:
        columns = 80
    return columns
