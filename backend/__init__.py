from rpid import Data, Output, TemperatureProbe, TemperatureProgram, TemperatureController

probe = TemperatureProbe()
output = Output()
data_provider = Data()

with TemperatureController(probe=probe, output=output, data_provider=data_provider) as tc:
    tc.run()