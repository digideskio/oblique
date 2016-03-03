import Trespass

class Text(str):

    def __new__(cls, text, *args):
        return str.__new__(cls, text)

    def __init__(self, text, tags):
        self.tags = tags

    def range(self, tag0, tag1):
        return self[self.tags[tag0]:self.tags[tag1]]

def codecompile(code, label='<string>'):
    if isinstance(code, str):
        if code[-1] != '\n':
            code = code.rstrip() + '\n'
        while code[0] == '\n':
            code = code[1:]
        if code[0] in ' \t':
            code = 'if 1:\n' + code
        code = compile(code, label, 'exec')
    elif hasattr(code, 'func_code'):
        code = code.func_code
    return code

def execute(code, text, tags, namespace):
    locals = {'_': Text(text, tags)}
    exec code in namespace, locals

class Run:
    
    def __init__(self, state):
        self.state = state
        self.debug = None

    def begin(self, namespace=None):
        if namespace is None:
            self.namespace = {}
        else:
            self.namespace = namespace
        self.buffer = ''
        self.stack = []
        self.matcher = self.state.matcher()
        assert isinstance(self.matcher, Trespass.Matcher), `self.matcher`
        if self.debug:
            self.matcher.debug = self.debug

    def addText(self, text):
        assert hasattr(self, 'state'), 'method begin not called'
        if self.debug:
            self.debug('Awkward.addText(%r)\n' % text)
        if text:
            self.check(text)
        if self.debug:
            self.debug('- Wait for more text\n')
        return self.state

    def end(self):
        assert hasattr(self, 'state'), 'method begin not called'
        if self.debug:
            self.debug('Awkward.end()\n')
        self.check('')
        if self.debug:
            self.debug('- Text fully parsed\n')
        return self.state

    def check(self, text):
        state = self.state
        buffer = self.buffer + text
        matcher = self.matcher
        if self.debug:
            self.debug('- State: %s\n' % state.name)
        # from the previous check() we have searched up to 
        # end of buffer, so here we search the new text only
        if text:
            match = matcher.addChunk(text)
        else:
            match = matcher.addFinal(text)
        while match:
	    #tags, (code, stack) = match
            start = match.start()
	    end = match.end()
	    tags = match.tags()
	    (code, stack) = match.value()
	    # start = tags[0]
            #end = tags[-1]
            if self.debug:
                self.debug('- Found match at %d: %r\n' % 
                            (start, buffer[start:end]))
            try:
                execute(code, buffer[:end], tags, self.namespace)
            except:
                self.state = state
                self.buffer = buffer
                self.matcher = matcher
                raise
            if stack:
                self.stack.extend(stack)
                state = self.stack.pop()
                while state is STOP:
                    if self.debug:
                        self.debug('- Reached STOP state '
                                    '[%d items on stack]\n'
                                    % len(self.stack))
                    if self.stack:
                        state = self.stack.pop()
                    else:
                        break
            if state is STOP:
                break
            if self.debug:
                self.debug('- State: %s\n' % state.name)
            buffer = buffer[end:]
            if self.debug:
                s = '- buffer = %s' % `buffer`
                if len(s) > 75:
                    s = s[:75] + '...'
                self.debug('%s\n' % s)
            matcher = state.matcher()
            if self.debug:
                matcher.debug = self.debug
            # we have created a new search so we pass in the full
            # remaining buffer
            if text:
                match = matcher.addChunk(buffer)
            else:
                match = matcher.addFinal(buffer)
        else:
            if self.debug:
                self.debug('- No match\n')
        self.state = state
        self.buffer = buffer
        self.matcher = matcher

class State:

    def __init__(self, name):
        self.name = name
        self.pattern = None

    def __repr__(self):
        return 'Awkward.State(%s)' % repr(self.name)

    def setPattern(self, pattern):
        self.pattern = pattern

    def getPattern(self):
        return self.pattern

    def addRule(self, regexp, code, stack=None):
        self.pattern.addRegExp(regexp, (codecompile(code), stack))

    def matcher(self):
        return Trespass.Matcher(self.pattern)

STOP = State('[STOP]') # a state with no rules

class Awkward:

    def __init__(self):
        self.debug = None
        self.default = State('[DEFAULT]')
        self.default.setPattern(Trespass.Pattern())
        self.states = [self.default]
        self.labels = {}
        self.initstate = self.default

    def run(self):
        return Run(self.initstate)

    # methods using states instances
    
    def addRule(self, regexp, code, stack=None):
        next = (codecompile(code), stack)
        for state in self.states:
            state.pattern.addRegExp(regexp, next)

    def addState(self, name, base=None):
        if base is None:
            base = self.default
        state = State(name)
        state.setPattern(base.getPattern().clone())
        self.states.append(state)
        self.labels[name] = state
        return state

    def setInitialState(self, state):
        self.initstate = state

    # methods using names

    def getState(self, name):
        if isinstance(name, State):
            state = name
        else:
            state = self.labels.get(name)
            if state is None:
                state = self.addState(name)
        return state

    def addLabelRule(self, labels, regexp, code, stack=None):
        if stack is not None:
            stack = [self.getState(name) for name in stack]
        if labels is None:
            self.addRule(regexp, code, stack)
        else:
            states = [self.getState(name) for name in labels]
            for state in states:
                state.addRule(regexp, code, stack)

    def addLabel(self, label, base=None):
        if base is not None:
            base = self.getState(base)
        self.addState(label, base)

    def setInitialLabel(self, label):
        self.initstate = self.getState(label)

if __name__ == '__main__':

    import sys

    a = Awkward()
    write = """import sys\nsys.stdout.write(_)"""
    a.addRule('l+', write)
    a.addRule('$', write, [STOP])
    r = a.run()
    r.debug = sys.stderr.write
    r.begin()
    r.addText('*hello, ')
    r.addText('world!')
    r.end()



