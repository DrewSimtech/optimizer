
import sys
from functools import wraps


# Function attribute to generisize this assert.
# Use this to wrap all non __builtin__ methods in root classes.
def rootClassMethod(mod_name, cls_name):
    # cls_type is nessisary for python2.6 since we dont have access to
    # an empty super() call until python3.0 so we need to pass it in.
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            cls_type = getattr(sys.modules[mod_name], cls_name)
            # Defensive programming. Force an attribute error if
            # someone has inherited wrong. This way we dont lose
            # track of our super calls.
            assert not hasattr(super(cls_type, self), func.__name__)
            return func(self, *args, **kwargs)
        return wrapper
    return decorator


# class for printing statments that we only need durring debugging.
class Debug:
    out = sys.stdout  # = None if we dont need prints
    err = sys.stderr  # = None if we dont need prints

    @staticmethod
    def toggleDebug():
        if(Debug.out):
            Debug.out = None
            Debug.err = None
        else:
            Debug.out = sys.stdout
            Debug.err = sys.stderr

    @staticmethod
    def enableDebug(enabled=True):
        if(enabled):
            Debug.out = sys.stdout
            Debug.err = sys.stderr
        else:
            Debug.out = None
            Debug.err = None

    @staticmethod
    def log(msg):
        Debug.out.write(str(msg) + '\n')
        Debug.out.flush()
