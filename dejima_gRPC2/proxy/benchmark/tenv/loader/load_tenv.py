import dejima
from dejima import Loader

class TENVLoader(Loader):
    def _load(self, params):
        return "commited"