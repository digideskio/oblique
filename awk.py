import sys
import Awkward

class PrimitiveAwkward(Awkward.Awkward):
    
    def __init__(self):
        Awkward.Awkward.__init__(self)
        self.__states = {}

    def getstate(self, name):
        if not self.__states.has_key(name):
            self.__states[name] = self.addState(name)
        return self.__states[name]

    def init(self):
        f = open('STATE-AWK.py', 'rt')
        try:
            line = f.readline()
            while line:
                ch = line[0]
                if ch != '\n' and ch != '#':
                    if ch == '*':
                        curr = [self]
                    else:
                        curr = [self.getstate(x)
                                    for x in line.strip().split()]
                    if self.debug:
                        self.debug('states = %s\n' % curr)
                    line = f.readline().strip()
                    if (
                        line[0] == "'" and line[-1] == "'" or
                        line[0] == '"' and line[-1] == '"'
                    ):
                        regexp = line[1:-1]
                        if self.debug:
                            self.debug('regexp = %s\n' % `regexp`)
                        line = f.readline().strip()
                        if line[0] == '*':
                            chain = None
                        elif line[0] == '>':
                            chain = [Awkward.STOP]
                        else:
                            chain = [self.getstate(x) for x in 
                                        line.split()]
                            chain.reverse()
                        if self.debug:
                            self.debug('stack = %s\n' % chain)
                        code = ''
                        line = f.readline()
                        while line[0] != '$':
                            code = code + line
                            line = f.readline()
                        if self.debug:
                            self.debug('code =\n%s' % code)
                    else:
                        raise RuntimeError(`line`)
                    for state in curr:
                        state.addRule(regexp, code, chain)
                line = f.readline()
        finally:
            f.close()
        self.setInitialState(self.__states['INIT'])

pa = None

def awk(filename):
    global pa

    if pa is None:
        pa = PrimitiveAwkward()
        #pa.debug = sys.stderr.write
        pa.init()

    pr = pa.run()
    #pr.debug = sys.stderr.write

    a = Awkward.Awkward()
    a.debug = sys.stderr.write

    namespace = {
        'AWKWARD': a,
        'FILENAME': filename,
        'DEBUG': 1
    }
    
    pr.begin(namespace)

    f = open(filename, 'rt')
    try:
        buf = f.read(1024)
        while buf:
            pr.addText(buf)
            buf = f.read(1024)
    finally:
        f.close()

    pr.end()

    return a

if __name__ == '__main__':
    a = awk(sys.argv[1])
    run = a.run()
    run.begin()
    buf = sys.stdin.read(1024)
    while buf:
        state = run.addText(buf)
        if state is Awkward.STOP:
            break
        buf = sys.stdin.read(1024)
    else:
        run.end()

    