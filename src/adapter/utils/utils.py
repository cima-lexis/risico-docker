from hashlib import sha1
from time import time
import numpy as np



class DotDict(dict):
    """
        dot.notation access to dictionary attributes
    """
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __getattr__(*args):
        val = dict.get(*args)
        return DotDict(val) if type(val) is dict else val

    # methods for pickling
    def __getstate__(self):
        return self

    def __setstate__(self, state):
        self.update(state)
        self.__dict__ = self


def timeit(method):
    def timed(*args, **kw):
        ts = time()
        result = method(*args, **kw)
        te = time()

        print('%r (%r, %r) %2.2f sec' % \
              (method.__name__, args, kw, te-ts))
        return result

    return timed


def get_dt(date, prev_date, clip_values=(1.0, 72.0)):
    dt_seconds = (date - prev_date).total_seconds()
    if clip_values:
        dt = np.clip(dt_seconds / 3600.0, clip_values[0], clip_values[1])
    else:
        dt = dt_seconds / 3600.0

    return dt


def get_hash(a):
    return sha1(a.astype('double', order='C')).hexdigest()


def wrap_in_array(*args):
    nargs = len(args)
    if nargs == 0:
        return
    elif nargs == 1:
        return np.array([args[0]])
    else:
        return (np.array([v]) for v in args)