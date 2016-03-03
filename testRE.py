import sys, traceback
import Trespass

def test(line):
    print '#%d' % i
    status, regexp, text = line.split(':')
    try:
        pattern = Trespass.Pattern()
        #pattern.debug = sys.stderr.write
        pattern.addRegExp(regexp)
    except:
        if status != '2':
            print 'expected', status, 'got 2'
            traceback.print_exc()
    else:
        result = pattern.match(text)
        if result:
            if status != '0':
                print 'expected', status, 'got 0'
        else:
            if status != '1':
                print 'expected', status, 'got 1'

f = open('TESTS', 'rt')
try:
    if len(sys.argv) > 1:
        limit = int(sys.argv[1])
    else:
        limit = 999999
    line = f.readline()
    i = 1
    while line and i <= limit:
        test(line.strip())
        line = f.readline()
        i += 1
finally:
    f.close()
