import random
import string


def generate_random_string(mark=None, *, length=16):
    tok = ''.join(random.choices(string.ascii_letters, k=length))
    if mark is None:
        return tok
    return f"<{mark}.{tok}>"
