import time, math, bno055, os, machine
from ustruct import pack, unpack
from machine import I2C, Pin

# try:
#     os.remove('bno055_config.dat')
# except:
#     pass
#
BNO055_SAMPLERATE_DELAY_MS = .1

i2c = I2C(-1, Pin(5), Pin(4), freq=400000, timeout=10000)


print("Starting I2C scan")

while True:
    devices = i2c.scan()
    print("Found devices: %s" % (repr(devices)))
    if 41 in devices:
        break

sensor = bno055.BNO055(i2c, address=41)
sensor.operation_mode(bno055.NDOF_MODE)

def display_sensor_offset():
    acc = "x=%d y=%d z=%d" % sensor.accel_offset()
    mag = "x=%d y=%d z=%d" % sensor.mag_offset()
    gyr = "x=%d y=%d z=%d" % sensor.gyro_offset()
    print("cal acc=(%s) mag=(%s) gyr=(%s) acc_r=%d mag_r=%d" % (acc, mag, gyr, sensor.acc_radius(), sensor.mag_radius()))

def display_cal_status():
    mag_status, accel_status, gyro_status, sys_status = sensor.get_calibration()
    print("mag_status=%d accel_status=%d gyro_status=%d sys_status=%d" % (mag_status, accel_status, gyro_status, sys_status))

def display_sensor_status():
    st_result = sensor.st_result()
    sys_error = sensor.sys_error()
    sys_status = sensor.sys_status()
    print("result=%d err=%d status=%d" % (st_result, sys_error, sys_status))


# Configure mode
found_calib = False
try:
    file = open('bno055_config.dat', 'rb')
    accel_offset_x, accel_offset_y, accel_offset_z, mag_offset_x, mag_offset_y, mag_offset_z, gyro_offset_x, gyro_offset_y, gyro_offset_z, acc_radius, mag_radius = unpack('hhhhhhhhhhh', file.read())
    print("Previous BNO055 calibration data found.")
    sensor.set_sensor_offsets(
        pack('<hhh', accel_offset_x, accel_offset_y, accel_offset_z),
        pack('<hhh', mag_offset_x, mag_offset_y, mag_offset_z),
        pack('<hhh', gyro_offset_x, gyro_offset_y, gyro_offset_z),
        acc_radius,
        mag_radius
    )
    found_calib = True
    file.close()
except:
    print("No previous BNO055 calibration data found.")

if found_calib:
    print("Move sensor slightly to calibrate magnetometers:")
else:
    print("Please calibrate sensor:")

display_cal_status()
# display_sensor_offset()

while not sensor.is_fully_calibrated():
    display_cal_status()
    time.sleep(BNO055_SAMPLERATE_DELAY_MS)
display_cal_status()
print("Fully calibrated!")
print("--------------------------------")

print("Calibration Results: ")
print("Storing calibration data")
display_sensor_status()
accel_offset, mag_offset, gyro_offset, acc_radius, mag_radius = sensor.get_sensor_offsets()
display_sensor_status()
acc = "x=%d y=%d z=%d" % accel_offset
mag = "x=%d y=%d z=%d" % mag_offset
gyr = "x=%d y=%d z=%d" % gyro_offset
print("cal acc=(%s) mag=(%s) gyr=(%s) acc_r=%d mag_r=%d" % (acc, mag, gyr, acc_radius, mag_radius))
sensor.set_sensor_offsets(accel_offset, mag_offset, gyro_offset, acc_radius, mag_radius)
display_sensor_status()
accel_offset_x, accel_offset_y, accel_offset_z = accel_offset
mag_offset_x, mag_offset_y, mag_offset_z = mag_offset
gyro_offset_x, gyro_offset_y, gyro_offset_z = gyro_offset

new_calib = pack('hhhhhhhhhhh',
     accel_offset_x,
     accel_offset_y,
     accel_offset_z,
     mag_offset_x,
     mag_offset_y,
     mag_offset_z,
     gyro_offset_x,
     gyro_offset_y,
     gyro_offset_z,
     acc_radius,
     mag_radius)
file = open('bno055_config.dat', 'wb')
file.write(new_calib)
file.close()


sensor.use_external_crystal(True) #Crystal must be configured AFTER loading calibration data into BNO055.

# Main code
while True:
    try:
        ex, ey, ez = sensor.euler()
        w, x, y, z = sensor.quaternion()

        ysqr = y * y
        t3 = +2.0 * (w * z + x * y)
        t4 = +1.0 - 2.0 * (ysqr + z * z)
        yaw = math.degrees(math.atan2(t3, t4))

        st_result = sensor.st_result()
        sys_error = sensor.sys_error()
        sys_status = sensor.sys_status()

        print("% 4.2f % 4.2f result=%d err=%d status=%d" % (ex, yaw, st_result, sys_error, sys_status))

        display_cal_status()

        #sensor.operation_mode(bno055.CONFIG_MODE)

        #print("cal acc=(%s) mag=(%s) gyr=(%s) acc_r=%d mag_r=%d" % (acc, mag, gyr, sensor.acc_radius(), sensor.mag_radius()))

        #file.write("%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (str(ex), str(yaw), str(st_result), str(sys_error), str(sys_status), str(mag_status), str(acc_status), str(gyr_status), str(sys_status)))
        # file.write(str(ex))

        #sensor._system_trigger(1) # Run a self test.
        #sensor.operation_mode(bno055.NDOF_MODE)
        #print("% 4.2f % 4.2f % 4.2f  % -50s %d %s %s" % (x, y, z, sensor.quaternion(), sensor.temperature(), bin(sensor.calib_stat()[0]), bin(sensor.calib_stat()[1])))

    except OSError as e:
        print(dir(e))

    time.sleep(BNO055_SAMPLERATE_DELAY_MS)




