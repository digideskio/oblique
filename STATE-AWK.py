# global namespace must include
# AWKWARD: an Awkward instance
# FILENAME: the filename
# DEBUG: print debug statements

INIT
''
NEWCLAUSE NEWRULE STARTRULEP

    global lineno, getstate

    lineno = 1

    def getstate(name, AWKWARD=AWKWARD, states={}):
        if name:
            if states.has_key(name):
                state = states[name]
            else:
                state = AWKWARD.addState(name)
                states[name] = state
        else:
            state = None
        return state

$
# STARTRULEP - what follows may be a rule or nothing (initial)
# STARTRULE - what follows must be a rule
# STARTCODE - what follows must be a line of code
# STARTLINE - what follows is a rule if first character is not whitespace,
#             or code if first character is whitespace

NEWCLAUSE
''
>
    global rules, source, codestart
    rules = []
    source = None
    codestart = -1
$
SAVECLAUSE 
'' 
NEWCLAUSE
    if DEBUG:
        print 'SAVECLAUSE'
    import Awkward
    code = Awkward.codecompile(source, 
                '<code starting at %s:%d>' % (FILENAME, codestart))
    for (states, regexp, stack) in rules:
        if stack:
            stack.reverse()
        if not states:
            states = [AWKWARD]
        for state in states:
            state.addRule(regexp, code, stack)
$
NEWRULE 
'' 
>
    global states, regexp, nchain
    states = None
    regexp = None
    nchain = None
$
SAVERULE 
'' 
NEWRULE
    if DEBUG:
        print 'SAVERULE', (states, regexp, nchain)
    rules.append((states, regexp, nchain))
$
WHITESPACE 
'^[[:space:]]*(\#[^\n]*\n[[:space:]]*)*'
>
    global lineno
    lineno += _.count('\n')
$    
NEWLINE 
'^[ \t]*(\#[^\n]*)?\n' 
>
    global lineno
    lineno += 1
$
# any other pattern means extra text was present
NEWLINE
'\n' 
>
    text = _.strip()
    raise RuntimeError('%s:%d Expected newline, got %s' % 
                (FILENAME, lineno, `_`))
$
STARTRULEP STARTRULE
'^[ \t]*(\#[^\n])*\n'
*
    global lineno
    lineno += 1
$
STARTLINE
'^\#[^\n]*\n'
*
    pass
$
STARTRULEP
'^#[A-Za-z0-9_]+#[[:space:]]*=[[:space:]]*#[A-Za-z0-9_]+#' 
NEWLINE STARTRULEP
    global lineno
    oldstate = getstate(_.range(3,4))
    newstate = getstate(_.range(1,2))
    newstate.setRE(oldstate.getRE().clone())
    lineno += _.count('\n')
$
STARTLINE
'^#[A-Za-z0-9_]+#[[:space:]]*=[[:space:]]*#[A-Za-z0-9_]+#'
SAVECLAUSE NEWLINE STARTRULEP
    global lineno
    oldstate = getstate(_.range(3,4))
    newstate = getstate(_.range(1,2))
    newstate.setRE(oldstate.getRE().clone())
    lineno += _.count('\n')
$
STARTRULEP STARTRULE
'^[A-Za-z0-9_]+' 
WHITESPACE CURRSTATE
    global states
    if DEBUG:
        print 'state = ', _
    states = [getstate(_)]
$
STARTLINE
'^[A-Za-z0-9_]+'
SAVECLAUSE WHITESPACE CURRSTATE
    global states
    if DEBUG:
        print 'state = ', _
    states = [getstate(_)]
$
CURRSTATE 
'^|' 
WHITESPACE CURRSTATE1
    pass
$
CURRSTATE1 
'^[A-Za-z0-9_]+' 
WHITESPACE CURRSTATE
    if DEBUG:
        print 'state = ', _
    states.append(getstate(_))
$
STARTRULEP STARTRULE
"^'" 
REGEXP
    global states, regexp
    states = []
    regexp = ''
$
STARTLINE 
"^'" 
SAVECLAUSE REGEXP
    global states, regexp
    states = []
    regexp = ''
$
CURRSTATE 
"^'" 
REGEXP
    global regexp
    regexp = ''
$
REGEXP 
'\\\\'
*
    # ignore escaped \
    global regexp
    regexp += _
$
REGEXP 
"\\'"
*
    # backslashed ' replaced with single '
    global regexp
    regexp += _[:-2] + "'"
$
REGEXP 
"'" 
WHITESPACE NEXTSTATE0
    global regexp
    regexp += _[:-1]
    if DEBUG:
        print 'regexp =', regexp
$
STARTRULEP STARTRULE
'^>' 
WHITESPACE NEXTSTATE0
    global states, regexp
    init = getstate('[START]')
    states = [init]
    regexp = ''
    AWKWARD.setInitialState(init)
$
STARTLINE 
'^>' 
SAVERULES WHITESPACE NEXTSTATE0
    global states, regexp
    init = getstate('[START]')
    states = [init]
    regexp = ''
    AWKWARD.setInitialState(init)
$
#NEXTSTATE0 PRE:
#    assert nchain is None, `nchain`
#$
# allow concatenation of strings for REs
NEXTSTATE0
"^'"
REGEXP
    pass
$
NEXTSTATE0 
'^>' 
WHITESPACE RULETERMINATOR
    global nchain
    nchain = [AWKWARD.STOP]
$
NEXTSTATE0 
'^[A-Za-z0-9_]+' 
WHITESPACE NEXTTERM
    global nchain
    nchain = [getstate(_)]
$
NEXTSTATE0 RULETERMINATOR NEXTTERM
'^:' 
SAVERULE NEWLINE STARTCODE
    pass
$
RULETERMINATOR NEXTTERM
'^;' 
SAVERULE WHITESPACE STARTRULE
    pass
$
NEXTTERM
'^>'
WHITESPACE NEXTSTATE
    pass
$
NEXTSTATE 
'^[A-Za-z0-9_]+' 
WHITESPACE NEXTTERM
    nchain.append(getstate(_))
$
STARTRULEP 
'^[[:space:]]*(\#[^\n]*\n[[:space:]]*)*$'
>
    pass
$
STARTRULEP
'\n'
ERROR
    text = _[:-1]
$    
STARTRULEP 
'$' 
ERROR
    lines = string.split(_, '\n')
    text = lines[0]
    if len(text) > 43:
        text = text[:40] + '...'
    lineno = lineno - len(lines) + 1
    raise RuntimeError("%s:%d: unexpected text %s"
                % (FILENAME, actual, repr(text)))
$

#STARTCODE PRE:
#    assert source is None, `source`
STARTCODE 
'^([ \t][^\n]*)?\n' 
STARTLINE
    global codestart, lineno, source
    codestart = lineno
    lineno += 1
    source = _
$
STARTLINE 
'^#(#[ \t]#[^\n]*)?#\n'
*
    global lineno, source
    if DEBUG:
        print `_`, _.tags
    lineno += 1
    source += _
$
STARTCODE 
'^([ \t][^\n]*)?$' 
SAVECLAUSE
    global codestart, source
    codestart = lineno
    source = _
$
STARTLINE 
'^([ \t][^\n]*)?$' 
SAVECLAUSE
    global source
    source += _
$
*
'$'
*
    raise EOFException()
$
