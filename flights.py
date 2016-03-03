import sys
import JetStar, VirginBlue

jetstar = JetStar.Airline()
jetstar.config()
virginb = VirginBlue.VirginBlue()
virginb.config()

dict = {}
for date in [1, 2, 3]:
    for origin in ('OOL', 'BNE', 'BNK'):
        sys.stderr.write('%d %s\n' % (date, origin))
        for airline in (jetstar, virginb):
            flights = airline.fetch(origin, 'PER', date, 3, 2005)
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
    if price > lastprice * 1.05:
        sys.stdout.write('\n')
    lastprice = price
    flights = [(flight[0][0][5], flight) for flight in dict[price]]
    flights.sort()
    for _, flight in flights:
        sys.stdout.write('$%4d.%02d' % divmod(price, 100))
        sys.stdout.write(' %s %s' % (flight[3], flight[2]))
        taxes = {}
        for currency, value in flight[5]:
            if taxes.has_key(currency):
                taxes[currency] += value
            else:
                taxes[currency] = value
        if taxes:
            taxlist = ['$%d.%02d %s' % (divmod(value, 100) + (currency,))
                        for currency, value in taxes.items()]
            sys.stdout.write(' (including taxes of %s)\n' % 
                        ' + '.join(taxlist))
        else:
            sys.stdout.write('\n')
        sectors = flight[0]
        for sector in sectors:
            sys.stdout.write('  %s %02d/%02d %02d:%02d - %02d:%02d %s'
                        ' %s Flight %s %s\n' %
                        (sector[3], sector[5][2], sector[5][1], 
                        sector[5][3], sector[5][4], sector[6][3], sector[6][4],
                        sector[4], sector[0], sector[1], sector[2]))
