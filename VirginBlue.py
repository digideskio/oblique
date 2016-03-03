import httplib, os, sys, tempfile
import Witness, Awkward

bookwit = None
flt1wit = None
flt2wit = None

class VirginBlue:

    def __init__(self):
        self.names = None
        self.routes = None
        self.dates = None

    def getroot(self):
        self.conn.request("GET", "/")
        f = open('VirginBlue-root.txt', 'wt')
        res = self.conn.getresponse()
        if res.status != 200:
            raise RuntimeError((res.status, res.reason))
        buf = res.read(1024)
        try:
            while buf:
                f.write(buf)
                buf = res.read(1024)
        finally:
            f.close()

    def config(self):
        global bookwit

        conn = httplib.HTTPConnection("www.virginblue.com.au")
        try:
            conn.request("GET", "/sky_book.html")
    
            if bookwit is None:
                bookwit = Witness.Witness()
                bookwit.program('VIRBLU-CONF.wit')
            run = bookwit.run()
            namespace = {}
            run.begin(namespace)
            #run.debug = sys.stderr.write
    
            res = conn.getresponse()
            if res.status != 200:
                raise RuntimeError((res.status, res.reason))
    
            f = open('VirginBlue-book.txt', 'wt')
            try:
                buf = res.read(512)
                while buf:
                    f.write(buf)
                    if run:
                        state = run.addText(buf)
                        if state is Awkward.STOP:
                            run = None
                    buf = res.read(512)
                if run:
                    run.end()
            finally:
                f.close()
        finally:
            conn.close()

        self.names = namespace['names']
        self.routes = namespace['routes']
        self.dates = namespace['dates']

        #for key, dests in self.routes.items():
        #    print self.names[key], '->', ', '.join([self.names[x] for x in dests])
        #for date in self.dates.keys():
        #    print date

    def fetch(self, origin, dest, day, month, year):
        global flt1wit, flt2wit

        conn = httplib.HTTPConnection("bookings.virginblue.com.au")
        try:

            if (
                not self.routes.has_key(origin) or
                dest not in self.routes[origin] or
                not self.dates.has_key((year, month))
            ):
                return None
    
            inputs = (
                'travel_type=on',
                'sector1_o=a%s' % origin,
                'sector1_d=%s' % dest,
                'sector_1_d=%02d' % day,
                'sector_1_m=%02d%04d' % (month, year),
                'sector_2_d=00',
                'sector_2_m=000000',
                'ADULT=01',
                'CHILD=00',
                'INFANT=00',
                'm2=', # set in submit_SB_form if return
                'tc=1',
                'page=SELECT',
                'language=EN',
                'pM=0',
                'oP=',
                'm1DO=0',
                'm1DP=0',
                'module=SB',
                'pT=00CHILD01ADULT', # changed in setPassengerTypes
                'rP=',
                'm2DO=0',
                'mode=0',
                'm2DP=0',
                'nom=1', # changed in submit_SB_Form 1=oneway, 2=return
                'm1=%04d%02d%02d%s%s' % (year, month, day, origin, dest)
                # changed in submit_SB_Form
            )
            body = '&'.join(inputs)
    
            conn.request('POST', '/skylights/cgi-bin/skylights.cgi', body)
    
            if flt1wit is None:
                flt1wit = Witness.Witness()
                #flt1wit.debug = sys.stderr.write
                flt1wit.program('VIRBLU-FLT1.wit')
            run = flt1wit.run()
            namespace = {}
            run.begin(namespace)
            #run.debug = sys.stderr.write
    
            res = conn.getresponse()
            if res.status != 200:
                raise RuntimeError((res.status, res.reason))
    
            fd, filename = tempfile.mkstemp('.html', 'VB-flt1-', 'E:\\tmp')
            try:
                buf = res.read(1024)
                while buf:
                    os.write(fd, buf)
                    if run:
                        state = run.addText(buf)
                        if state is Awkward.STOP:
                            run = None
                    buf = res.read(1024)
                if run:
                    run.end()
            finally:
                os.close(fd)

            if run is not None:
                os.rename(filename, '%s.err' % filename)


            fares = namespace['fares']
        
            flights = []

            for label, inputs in fares.items():
                conn.close()
                conn = httplib.HTTPConnection("bookings.virginblue.com.au")

                body = '&'.join(inputs)
        
                conn.request('POST', '/skylights/cgi-bin/skylights.cgi',
                            body)
        
                if flt2wit is None:
                    flt2wit = Witness.Witness()
                    #flt2wit.debug = sys.stderr.write
                    flt2wit.program('VIRBLU-FLT2.wit')
                run = flt2wit.run()
                namespace = {'label': label}
                run.begin(namespace)
                #run.debug = sys.stderr.write
        
                res = conn.getresponse()
                if res.status != 200:
                    raise RuntimeError((res.status, res.reason))
        
                fd, filename = tempfile.mkstemp('.html', 'VB-flt2-', 'E:/tmp')
                try:
                    buf = res.read(1024)
                    while buf:
                        os.write(fd, buf)
                        if run:
                            state = run.addText(buf)
                            if state is Awkward.STOP:
                                run = None
                        buf = res.read(1024)
                    if run:
                        run.end()
                finally:
                    os.close(fd)

                if run is not None:
                    os.rename(filename, '%s.err' % filename)

                flights.append(namespace['flight'])
        finally:
            conn.close()

        return flights

if __name__ == '__main__':
    
    v = VirginBlue()
    v.config()
    #flights = v.fetch('SYD', 'OOL', 7, 2, 2005)
    dict = {}
    for date in 24,25,26:
      for origin in ('OOL', 'BNE', 'BNK'):
        flights = v.fetch(origin, 'SYD', date, 2, 2005)
        if flights is not None:
            for flight in flights:
                price = flight[4]
                f = dict.get(price)
                if f is None:
                    dict[price] = f = []
                f.append(flight)
    prices = dict.keys()
    prices.sort()
    lastprice = prices[0]
    for price in prices:
        if price > lastprice * 1.1:
            sys.stdout.write('\n')
        sys.stdout.write('$%4d.%02d\n' % divmod(price, 100))
        for flight in dict[price]:
            sys.stdout.write('%s\n' % flight[2])
            sectors = flight[0]
            for sector in sectors:
                sys.stdout.write(' %s %02d/%02d %02d:%02d - %02d:%02d %s'
                            ' %s Flight %s %s\n' %
                            (sector[3], sector[5][2], sector[5][1], sector[5][3],
                            sector[5][4], sector[6][3], sector[6][4],
                            sector[4], sector[0], sector[1], sector[2]))
            
