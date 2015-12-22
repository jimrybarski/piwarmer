from device.pid import PID, Driver

class CycleData(object):
    pass


cd = CycleData()

cd.desired_temperature = 72
cd.current_temperature = 25
cd.accumulated_error = 0

driver = Driver("test", 10.0, 1.0, 3.0, 10, -10)
pid = PID(driver)

temperatures = [25.0, 32.0, 37.0, 45.0, 53.0, 65.0, 68.0, 68.0, 68.0, 68.0, 68.0, 68.0, 68.0, 68.0, 71.0, 73.0, 78.0, 79.0, 83.0, 78.0, 74.0, 71.0, 70.0, 72.0, 78.0, 65.0]

for temp in temperatures:
    cd.current_temperature = temp
    duty_cycle, cd.accumulated_error = pid.update(cd)
    print(cd.current_temperature, duty_cycle)
