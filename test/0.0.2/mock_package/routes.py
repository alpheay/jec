from jec_api import Route

class PackageRoute(Route):
    def get(self):
        return {"source": "package"}
