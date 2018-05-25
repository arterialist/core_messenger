import time


def full_strip(string):
    while 1:
        if len(string):
            if string[0] in [' ', '\n'] or string[-1] in [' ', '\n']:
                string = string.strip('\n')
                string = string.strip(' ')
            else:
                break
        else:
            break
    return string


def current_time():
    return int(round(time.time() * 1000))
