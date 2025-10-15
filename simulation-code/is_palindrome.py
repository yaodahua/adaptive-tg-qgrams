import time
import datetime


# 延迟时间常量（10毫秒）
DELAY_SECS = 0.01  # 10ms delay


# 回文检测函数（可选项延迟）
def is_palindrom(s: str, delay=False):
    if delay:
        time.sleep(DELAY_SECS)
    if s == "" or len(s) == 1:
        return True
    while len(s) > 1 and s[0] == s[-1]:
        s = s[1 : len(s) - 1]
    if s == "" or len(s) == 1:
        return True
    return False


# 变异版本回文检测函数（边界条件不同）
def is_palindrom_mu1(s: str):
    if s == "" or len(s) == 1:
        return True
    while len(s) > 1 and s[0] == s[-1]:
        s = s[1 : len(s) - 1]
    if s == "" or len(s) == 2:  # was: len(s) == 1
        return True
    return False


# 带时间测量的回文检测函数
def timed_is_palindrom(s: str, delay=False):
    start = datetime.datetime.now()
    if s == "" or len(s) == 1:
        return (datetime.datetime.now() - start).total_seconds()
    while len(s) > 1 and s[0] == s[-1]:
        s = s[1 : len(s) - 1]
    if s == "" or len(s) == 1:
        return (datetime.datetime.now() - start).total_seconds()
    return (datetime.datetime.now() - start).total_seconds()
