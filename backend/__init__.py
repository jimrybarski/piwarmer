from rpid import Data, Output, TemperatureProbe, TemperatureProgram, TemperatureController

probe = TemperatureProbe()
output = Output()
data_provider = Data()

tc = TemperatureController(probe=probe, output=output, data_provider=data_provider)
tc.run()