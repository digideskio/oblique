
class COMMON:

    def zrule1(self, text):
        '$'
        raise EOFError()
    
class NAVITAIRE(COMMON):

    def rule1(self, text):
        'Navitaire Inc'
        global names, routes, dates
        names = {}
        routes = {}
        dates = {}
        return SKYLIGHTS

class SKYLIGHTS(COMMON):

    def rule1(self, text):
        r'Skylights v6\.0\.4'
        return PORTS

# get airports served

class PORTS(COMMON):
    
    def rule1(self, text):
        'var Dests = new Array \([[:space:]]*'
        return PORT

class PORT(COMMON):

    def rule1(self, text):
        '^"XXX[A-Z]",[[:space:]]*'
        pass
    
    def rule2(self, text):
        '^"#[A-Z]{3}#",[[:space:]]*'
        port = text.range(1, 2)
        routes[port] = None
        names[port] = None

    def rule3(self, text):
        '^0[[:space:]]*\);'
        return NAMES

# get name of airport

class NAMES(COMMON):
    
    def rule1(self, text):
        '^[[:space:]]*var sXXX[A-Z] = "--- #[A-Z]+( [A-Z]+)*# ---";'
        global country
        country = text.range(1, 2).title()
        return MORENAMES


class MORENAMES(NAMES):

    def rule2(self, text):
        '^[[:space:]]*var s#[A-Z]{3}# = "#[^"]+#";'
        port = text.range(1,2)
        name = text.range(3,4)
        names[port] = '%s, %s' % (name, country)

    def rule3(self, text):
        '[[:space:]]*var aXXX[A-Z] = new Array\([[:space:]]*0[[:space:]]*\);'
        return ROUTES

# routes

class ROUTES(COMMON):
    
    def rule1(self, text):
        '^[[:space:]]*var aXXX[A-Z] = new Array\([[:space:]]*0[[:space:]]*\);'
        pass

    def rule2(self, text):
        '^[[:space:]]*var a#[A-Z]{3}# = new Array\('
        global origin
        origin = _.range(1,2)
        assert routes[origin] is None
        routes[origin] = []
        return ROUTE

    def rule3(self, text):
        r'^[[:space:]]*}'
        return DATEFIND

class ROUTE(COMMON):

    def rule1(self, text):
        '^[[:space:]]*"XXX[A-Z]",'
        pass

    def rule2(self, text):
        r'^[[:space:]]*"#[A-Z]{3}#",'
        dest = _.range(1,2)
        routes[origin].append(dest)

    def rule3(self, text):
        r'^[[:space:]]*0[[:space:]]*\);'
        return ROUTES

class DATEFIND(COMMON):

    def rule1(self):
        r'<select name=\'sector_1_m\' [^>]*>[[:space:]]*'
        return DATE

class DATE(COMMON):
    def rule1(self, text):
        '^<OPTION VALUE=#[0-9]{2}#[0-9]{4}#( SELECTED)?>[[:alpha:]]{3} '
        '#[0-9]{4}#[[:space:]]*'
        m = int(_.range(1,2))
        y = int(_.range(2,3))
        z = int(_.range(4,5))
        assert y == z, `y, z`
        dates[(y, m)] = True

    def rule2(self, text):
        '^</select>'
        return Witness.STOP


Machine = Witness.Program(NAVITAIRE)
