import sys
import Awkward

# Witness reads in a state machine description of a file structure and programs 
# the Awkward state machine engine to parse a file with the given structure.  Since 
# the state machine description file is itself in a particular format, we can create 
# a state machine description for the state machine description files.  However, 
# this gives us a bootstrapping problem.  So we program the meta-description file
# in a much simpler format, understood by the SimpleWitness class.

WITNESS_STATEMENT = "E:/Stuff/Projects/Oblique/WITNESS.wis"

class SimpleWitness(Awkward.Awkward):

    def program(self, file):
        f = open(file, 'rt')
        try:
            line = f.readline()
            while line:
                ch = line[0]
                if ch != '\n' and ch != '#':
                    line = line.strip()
                    if line == '*':
                        curr = None
                    else:
                        curr = line.split()
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
                            chain = line.split()
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
                    self.addLabelRule(curr, regexp, code, chain)
                line = f.readline()
        finally:
            f.close()
        self.setInitialLabel('INIT')

witness0 = None

class Witness(Awkward.Awkward):
    
    def program(self, filename):
        global witness0
    
        if witness0 is None:
            witness0 = SimpleWitness()
            witness0.debug = self.debug
            witness0.program(WITNESS_STATEMENT)
    
        run0 = witness0.run()
        run0.debug = self.debug
    
        namespace = {
            'Awkward': Awkward,
            'WITNESS': self,
            'FILENAME': filename,
            'DEBUG': self.debug
        }
        
        f = open(filename, 'rt')
        try:
            run0.begin(namespace)
            buf = f.read(1024)
            while buf:
                state = run0.addText(buf)
                if state is Awkward.STOP:
                    break
                buf = f.read(1024)
            else:
                run0.end()
        finally:
            f.close()
    
    
if __name__ == '__main__':
    filename = sys.argv[1]
    witness = Witness()
    witness.debug = sys.stderr.write
    witness.program(filename)
    run = witness.run()
    run.begin()
    buf = sys.stdin.read(1024)
    while buf:
        state = run.addText(buf)
        if state is Awkward.STOP:
            break
        buf = sys.stdin.read(1024)
    else:
        run.end()

    