from rpid import Data, Heater, TemperatureProbe, TemperatureController

if __name__ == "__main__":
    probe = TemperatureProbe()
    output = Heater()
    data_provider = Data()

    with TemperatureController(probe=probe, output=output, data_provider=data_provider) as tc:
        tc.run()
