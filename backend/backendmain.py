from rpid import Data, Output, TemperatureProbe, TemperatureController
import time

if __name__ == "__main__":
    time.sleep(300)
    probe = TemperatureProbe()
    output = Output()
    data_provider = Data()

    with TemperatureController(probe=probe, output=output, data_provider=data_provider) as tc:
        tc.run()
