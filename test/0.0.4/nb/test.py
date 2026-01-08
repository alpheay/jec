from jec_api import Core
from test2 import SimpleRoute, Test

core = Core(title="My API")

core.tinker(host="127.0.0.5", port=8000)

core.register(SimpleRoute)
core.register(Test)


