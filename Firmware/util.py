import time

def timed_function(f, *args, **kwargs):
    try:
        myname = str(f).split(' ')[1]
    except IndexError:
        myname = str(f)
    def new_func(*args, **kwargs):
        t = time.monotonic_ns()
        result = f(*args, **kwargs)
        delta = time.monotonic_ns() - t
        print('Function {} Time = {:6.3f}ms'.format(myname, delta/1000000))
        return result
    return new_func