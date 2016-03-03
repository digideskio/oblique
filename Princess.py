import Trespass

ATTR_NAME = '_Princess_pattern'

class Princess:
    
    def __init__(self, state):
        self.state = state

    def getPattern(self, state):
        if hasattr(state, ATTR_NAME):
            pattern = getattr(state, ATTR_NAME)
        else:
            pattern = Trespass.Pattern()
            for rulename in dir(state):
                if rulename[0] == '_':
                    continue
                method = getattr(state, rulename)
                regexp = method.__doc__
                pattern.addRegExp(regexp, method)
            setattr(state, ATTR_NAME, pattern)
        return pattern
                
    def begin(self, namespace=None):
        if namespace is None:
            self.namespace = {}
        else:
            self.namespace = namespace
        self.buffer = ''
        self.stack = []
        self.matcher = Trespass.Matcher(self.getPattern(self.state))
        if self.debug:
            self.matcher.debug = self.debug

    def addText(self, text):
        assert hasattr(self, 'state'), 'method begin not called'
        if self.debug:
            self.debug('Princess.addText(%r)\n' % text)
        if text:
            self.check(text)
        if self.debug:
            self.debug('- Wait for more text\n')
        return self.state

    def end(self):
        assert hasattr(self, 'state'), 'method begin not called'
        if self.debug:
            self.debug('Princess.end()\n')
        self.check('')
        if self.debug:
            self.debug('- Text fully parsed\n')
        return self.state

    def check(self, text):
        state = self.state
        buffer = self.buffer + text
        matcher = self.matcher
        if self.debug:
            if hasattr(state, 'im_class'):
                name = state.im_class.__name__
            else:
                name = state.__name__
            self.debug('- State: %s\n' % name)
        # from the previous check() we have searched up to 
        # end of buffer, so here we search the new text only
        if text:
            match = matcher.addChunk(text)
        else:
            match = matcher.addFinal(text)
        while match:
            tags, rule = match
            start = tags[0]
            end = tags[-1]
            if self.debug:
                self.debug('- Found match at %d: %r\n' % 
                            (start, buffer[start:end]))
            if rule.im_self is None:
                rule = getattr(rule.im_class(), rule.__name__)
            try:
                execute(rule, buffer[:end], tags, self.namespace)
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
