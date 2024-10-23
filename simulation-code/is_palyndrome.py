import time
import datetime


DELAY_SECS = 0.01  # 10ms delay


def is_palyndrom(s: str, delay=False):
    if delay:
        time.sleep(DELAY_SECS)
    if s == "" or len(s) == 1:
        return True
    while len(s) > 1 and s[0] == s[-1]:
        s = s[1 : len(s) - 1]
    if s == "" or len(s) == 1:
        return True
    return False


def is_palyndrom_mu1(s: str):
    if s == "" or len(s) == 1:
        return True
    while len(s) > 1 and s[0] == s[-1]:
        s = s[1 : len(s) - 1]
    if s == "" or len(s) == 2:  # was: len(s) == 1
        return True
    return False


def timed_is_palyndrom(s: str, delay=False):
    start = datetime.datetime.now()
    if s == "" or len(s) == 1:
        return (datetime.datetime.now() - start).total_seconds()
    while len(s) > 1 and s[0] == s[-1]:
        s = s[1 : len(s) - 1]
    if s == "" or len(s) == 1:
        return (datetime.datetime.now() - start).total_seconds()
    return (datetime.datetime.now() - start).total_seconds()
