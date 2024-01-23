class Loader:
    # check parameters
    def param_check(self, params, param_keys):
        for key in param_keys:
            if not key in params.keys():
                raise Exception("Invalid parameters")

    # load for specific data
    def _load(self, params):
        # -- inherit this class and override this method --
        raise Exception("set _load")

    # parent load (call self._load)
    def load(self, params):
        print("load start")

        try:
            result = self._load(params)
        except Exception as e:
            return {"result": e}

        print("load finish")
        return {"result": result}
