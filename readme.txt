Witness is a state machine-driven analyser of data streams.

For each stream, there is a current state, and for each state, there
are several patterns for which Witness will watch. Witness scans the patterns
looking for one that matches the current text. It then executes the code
associated with that pattern, and resumes searching from the end of the
pattern.

Need to tokenize into lines (or similar) to avoid problem where 31 does not
trigger 3124 pattern, but does trigger 3.+ pattern, then next characters read
are 24.

A Witness configuration file:

import witness

w = witness.Witness()

def func(match):
    print match

w.rule_add(re.compile("http://([a-zA-Z0-9_]+\.)+/[^\s]"), func)

s1 = w.state_add('STATE1')

s1.rule_add(re.compile('hello'), func, s2)

w.rule_add(None, unknown)

w.read(f)

By default, state == ''
