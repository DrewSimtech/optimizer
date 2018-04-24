
import os


def getStep(fname):
    step = None
    for p in fname.split('/'):
        if('iteration' in p):
            step = int(p.partition('_')[-1])
    return step


if (__name__ == '__main__'):
    data = {}
    for root, dirs, files in os.walk('./step_map/'):
        for f in files:
            if('.OUT' in f and 'all' in f):
                fname = os.path.join(root, f)
                with open(fname, 'r') as inf:
                    data[getStep(fname)] = inf.read()
    with open('out.map', 'w') as outf:
        for d in sorted(data.keys()):
            outf.write(str(d) + '\n')
            outf.write(data[d] + '\n\n')
