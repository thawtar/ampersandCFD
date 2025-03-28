# Function to recursively convert tuples to lists (or any other conversion)
from typing import Sequence
import yaml




@staticmethod
def crlf_to_LF(file_path):
    WINDOWS_LINE_ENDING = b'\r\n'
    UNIX_LINE_ENDING = b'\n'
    with open(file_path, 'rb') as f:
        content = f.read()
    content = content.replace(WINDOWS_LINE_ENDING, UNIX_LINE_ENDING)
    with open(file_path, 'wb') as f:
        f.write(content)

