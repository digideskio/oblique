import sys, re
import Awkward

class Runner:
        
        def run(self):
            a = Witness.Witness(debug=self.debug_write)
            init = a.addState('init')
            x1 = a.addState('table')
            x2 = a.addState('x2')
            s1 = a.addState('s1')
            s2 = a.addState('s2')
            s3 = a.addState('s3')
            s4 = a.addState('s4')
            s5 = a.addState('s5')
            a.setState(init)
            init.addRule('<table', self.write, x1)
            init.addRule(r'[.\n]*>', self.write)
            x1.addRule('>', self.write, b4tr)
            b4tr.addRule('<tr>', None, b4acro)
            b4acro.addRule('<t([dh])>', self.b4acro, inacro)
            inacro.addRule
            
        def write(self, text, match):
            sys.stdout.write(text)
            sys.stdout.write(match.group())
            
        def b4acro(self, text, match):
            text = text.strip()
            if text:
                sys.stdout.write(text)
            
            x2.addRule(XMLTag('td'), self.doacronym, s1)
            s1.addRule(XMLTag('td'), self.doevent, s2)
            s2.addRule(XMLTag('td'), self.dolocation, s3)
            s3.addRule(XMLTag('td'), self.dodate, s4)
            s4.addRule(XMLTag('td'), self.dodeadline, s5)
            s5.addRule(re.compile(r'\W*</tr>'), self.dorow, x1)
            endgame = a.addState('end')
            x1.addRule(re.compile(r'\W*</table>'), self.write, endgame)
            endgame.addRule(re.compile(r'.+'), self.write, None)

            f = open('conf.html', 'r')
            buf = f.read(512)
            while buf:
                a.addText(buf)
                buf = f.read(512)

        def debug_write(self, text):
            sys.stderr.write(text)

        def write(self, text, match):
            sys.stdout.write(text)
            sys.stdout.write(match.group())

        def doacronym(self, match):
            self.acronym = match.all()

        def doevent(self, match):
            self.event = match.all()

        def dolocation(self, match):
            self.location = match.all()

        def dodate(self, match):
            self.date = match.all()

        def dodeadline(self, match):
            self.deadline = match.all()
            
        def dorow(self, match):
            sys.stdout.write('<tr>\n')
            sys.stdout.write(self.location)
            sys.stdout.write('\n')
            sys.stdout.write(self.date)
            sys.stdout.write('\n')
            sys.stdout.write(self.acronym)
            sys.stdout.write('\n')
            sys.stdout.write(self.event)
            sys.stdout.write('\n')
            sys.stdout.write(self.deadline)
            sys.stdout.write('\n')
            sys.stdout.write('</tr>')

r = Runner()
r.run()
