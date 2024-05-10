import random
import string
from datetime import datetime

def generate(length):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(length))

def generate_with_date(length, include_microsec=False):
    now = datetime.now()
    if include_microsec:
        datestr = now.strftime("%y%m%d%H%M%S%f")
    else:
        datestr = now.strftime("%y%m%d%H%M%S")
    letters = string.ascii_letters
    return datestr + ''.join(random.choice(letters) for _ in range(length))

if __name__ == "__main__":
    now = datetime.now()
    datestr = now.strftime("%y%m%d%H%M%S")
    letters = string.ascii_letters
    print(datestr)