from rpid import model, service

hot_relay = model.Relay("hot")
cold_relay = model.Relay("cold")

thermometer = service.TempSensor()
toggler = service.RelayToggler()
toggler.on(hot_relay)