import sys
# inspect, interject, erect

conn, addr = sock.accept()
socketin = ServerSocketIn(conn)
socketout = ServerSocketOut(conn)
# echo server
socketin.setEject(socketout.inject)
socketin.setError(socketout.reject)

class ServerSocketIn:
    
    def __init__(self, conn):
        self.conn = conn
        self.eject = None
        self.error = None

    def setEject(self, eject):
        self.eject = eject
        eventloop.onReadable(self.conn, self.ready)

    def setError(self, error):
        self.error = error

    def ready(self):
        try:
            buffer = self.conn.read(2048)
            if buffer:
                eventloop.onReadable(self.conn, self.ready)
            else:
                self.conn.shutdown(0)
                self.conn = None
            self.eject(buffer)
        except:
            if self.error is None:
                raise
            else:
                self.error(sys.exc_info())
                self.error = None
                self.eject(None)
                self.eject = None

class ServerSocketOut:

    def __init__(self, conn):
        self.conn = conn
        self.close = 0

    def inject(self, text):
        if self.conn is None:
            raise RuntimeError('connection closed')
        if not text:
            if self.buffer:
                self.close = 1
            else:
                self.conn.close()
                self.conn = None
        else:
            if not self.buffer:
                eventloop.onWritable(self.conn, self.ready)
        self.buffer += text

    def reject(self, exc):
        import traceback
        sys.stderr.write('[Caught Exception]\n')
        traceback.print_exception(*exc)
        if self.conn is not None:
            self.conn.close()
            self.conn = None

    def ready(self):
        nbytes = self.conn.write(self.buffer)
        self.buffer = self.buffer[nbytes:]
        if self.buffer:
            eventloop.onWritable(self.conn, self.ready)
        elif self.close:
            self.conn.close()
            self.conn = None
        
# for echo server
socketin.eject = socketout.inject
socketin.error = socketout.reject

