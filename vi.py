class State:
    
    def __init__(self):
        pat = Trespass.Pattern()
        for method in dir(self):
            if method[0] == '_':
                continue
            print method
            func = getattr(self, method)
            pat.addRegExp(func.__doc__, func)
        self._pattern = pat

class Common(State):

    def rule1(self, text):
        r'(<br>&nbsp; Flight [^<]+<br>&nbsp; <font size=1>'
        r'<i>Operated by #[^<]+#</i></font>)+'
        return WHITESPACE, FARE1

class FARE0(Common):
    
    def rule2(self, text):
        pass
        
# keep a mapping of class to singleton. When FARE0 is returned,
# if instance has not been created, create instance, and run.
# Alt, check out class methods... and have a mapping from class
# to Pattern instead

# this allows rules to return different next states depending on
# variables

