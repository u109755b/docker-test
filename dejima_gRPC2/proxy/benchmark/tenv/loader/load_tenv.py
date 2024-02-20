from dejima import status
from dejima import Loader

class TENVLoader(Loader):
    def _load(self, params):
        return status.COMMITTED
