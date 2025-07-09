import time
import datetime


NOT_A_TRIANGLE = 'NOT A TRIANGLE'
EQUILATERAL = 'EQUILATERAL'
ISOSCELES = 'ISOSCELES'
RIGHT_ANGLE = 'RIGHT ANGLE'
SCALENE = 'SCALENE'

DELAY_SECS = 0.01  # 10ms delay



def triangle_type(a, b, c, delay=False):
    if delay:
        time.sleep(DELAY_SECS)
    if a <= 0 or b <= 0 or c <= 0:
        return NOT_A_TRIANGLE
    if a + b <= c or a + c <= b or b + c <= a:
        return NOT_A_TRIANGLE
    if a == b:
        if b == c:
            return EQUILATERAL
        else:
            return ISOSCELES
    elif a == c:
        return ISOSCELES
    elif b == c:
        return ISOSCELES
    elif a*a + b*b == c*c:
        return RIGHT_ANGLE
    elif b*b + c*c == a*a:
        return RIGHT_ANGLE
    elif a*a + c*c == b*b:
        return RIGHT_ANGLE
    else:
        return SCALENE



def triangle_type_mu1(a, b, c):
    if a <= 0 or b <= 0 or c <= 0:
        return NOT_A_TRIANGLE
    if a + b <= c or a + c <= b or b + c <= a:
        return NOT_A_TRIANGLE
    if a == b:
        if b == c:
            return EQUILATERAL
        else:
            return ISOSCELES
    elif a == c:
        return ISOSCELES
    elif b == c:
        return ISOSCELES
    elif a*a + b*b == c*c:
        return RIGHT_ANGLE
    elif b*b + c*c == b*b:  # was: a*a
        return RIGHT_ANGLE
    elif a*a + c*c == b*b:
        return RIGHT_ANGLE
    else:
        return SCALENE

def timed_triangle_type(a, b, c, delay=False):
    start = datetime.datetime.now()
    type = None
    if a <= 0 or b <= 0 or c <= 0:
        type =  NOT_A_TRIANGLE
    elif a + b <= c or a + c <= b or b + c <= a:
        type =  NOT_A_TRIANGLE
    elif a == b:
        if b == c:
            type =  EQUILATERAL
        else:
            type =  ISOSCELES
    elif a == c:
        type =  ISOSCELES
    elif b == c:
        type =  ISOSCELES
    elif a*a + b*b == c*c:
        type =  RIGHT_ANGLE
    elif b*b + c*c == a*a:
        type =  RIGHT_ANGLE
    elif a*a + c*c == b*b:
        type =  RIGHT_ANGLE
    else:
        type =  SCALENE
    return (datetime.datetime.now() - start).total_seconds()
