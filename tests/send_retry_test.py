import unittest
from cloudfiles        import Connection
from cloudfiles.authentication import MockAuthentication as Auth
from fakehttp          import TrackerSocket, CustomHTTPConnection
from misc              import printdoc


class FailableTrackerSocket(TrackerSocket):
    """
    Raises an socket error when gets the specific word "spain" and is
    configured to fail (may_fail is True).
    """
    def __init__(self, may_fail=False):
        super(FailableTrackerSocket, self).__init__()
        self.may_fail = may_fail

    def send(self, data, flags=0):
        if self.may_fail and data == 'spain':
            raise IOError, 'socket error simulation'
        return super(FailableTrackerSocket, self).send(data, flags)
    sendall = send


class FailOnceHTTPConnection(CustomHTTPConnection):
    """
    Http Connection that uses the FailableTrackerSocket to emulate a connection
    instability. He starts configured to not fail unless the set by the
    let_fail method. After that, he will fail only once.
    """
    def let_fail(self):
        self.can_fail = True

    def connect(self):
        if not hasattr(self, 'can_fail'):
            self.sock = FailableTrackerSocket()
        else:
            if not hasattr(self, 'may_fail'):
                self.may_fail = True
            self.sock = FailableTrackerSocket(self.may_fail)
            self.may_fail = False


class ObjectTest(unittest.TestCase):
    """
    Freerange Object class tests.
    """

    @printdoc
    def test_send_retry(self):
        """Simulates an inactivity timeout between two send requests."""
        gener = (part for part in ('the ', 'rain ', 'in ', 'spain', ' ...'))
        self.storage_object.size = 21
        self.storage_object.content_type = "text/plain"
        self.container.conn.connection.let_fail()
        self.storage_object.send(gener)

    def setUp(self):
        self.auth = Auth('jsmith', 'qwerty')
        self.conn = Connection(auth=self.auth)
        self.conn.conn_class = FailOnceHTTPConnection
        self.conn.http_connect()
        self.container = self.conn.get_container('container1')
        self.storage_object = self.container.get_object('object1')

    def tearDown(self):
        del self.storage_object
        del self.container
        del self.conn
        del self.auth


# vim:set ai sw=4 ts=4 tw=0 expandtab:
