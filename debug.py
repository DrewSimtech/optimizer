
import sys


class Debug:
    out = sys.stdout
    err = sys.stderr

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
        Debug.out.write(msg)
        Debug.out.flush()
