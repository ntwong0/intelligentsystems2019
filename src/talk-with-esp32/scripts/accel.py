#!/usr/bin/env python

import requests
import time
import numpy as np

# dictToSend = {'question':'what is the answer?'}
# res = requests.post('http://localhost:5000/task1', json=dictToSend)
# print 'response from server:',res.text
# dictFromServer = res.json()

ip_addr = '192.168.0.193'
# ip_addr = '192.168.0.128'

def str_to_int16(str):
    return np.int16(int(str, 16))

def str_to_float64(str):
    return np.float64(int(str, 16))

def aY_to_x(aY):
    return np.float32(aY) / np.float32(0x4000)

def aX_to_y(aX):
    return -aY_to_x(aX)

# for arctan(y,x), use np.arctan2()

def radians_to_degrees(radVal):
    if radVal < 0:
        return np.uint16(180.0*(radVal/np.pi + 2))
    else:
        return np.uint16(180.0*radVal/np.pi)

def accelHex_to_degrees(aX, aY):
    return radians_to_degrees(
            np.arctan2(aX_to_y(str_to_int16(aX)),
                       aY_to_x(str_to_int16(aY))))

def linAcc_to_degrees(aX, aY):
    return radians_to_degrees(
            np.arctan2(aX_to_y(str_to_int16(aX)),
                       aY_to_x(str_to_int16(aY))))

def normalize_degree_for_servo(degree):
    if degree > 270:
        return 0
    elif degree > 180:
        return 180
    else:
        return degree

def get_accel():
    res = requests.post('http://' + ip_addr + ':80/accel')
    my_list = res.text.split(",")
    #<debug>
    # print res.text
    #</debug>
    return my_list

def set_servo(deg_val):
    res = requests.post('http://' + ip_addr + ':80/servo?deg_val=' + str(deg_val))
    #<debug>
    print res.text
    #</debug>

def accel_to_servo_demo():
    while True:
        my_list = get_accel()
        deg_val = normalize_degree_for_servo(
            accelHex_to_degrees(my_list[0], my_list[1])
        )
        print deg_val
        set_servo(deg_val)
        time.sleep(0.1)

import rospy
from std_msgs.msg import String, Header
from sensor_msgs.msg import Imu

pkt = Imu()
seq = 0

def packetize_imu(my_list):
    global pkt, seq
    pkt.header.seq = seq
    seq = seq + 1
    pkt.header.stamp = rospy.Time.now()
    pkt.header.frame_id = "imu"
    pkt.linear_acceleration.x = 9.8 * str_to_int16(my_list[0]) / 16384.0
    pkt.linear_acceleration.y = 9.8 * str_to_int16(my_list[1]) / 16384.0
    pkt.linear_acceleration.z = 9.8 * str_to_int16(my_list[2]) / 16384.0

def accel_talker():
    pub = rospy.Publisher('imu/raw', Imu, queue_size=1)
    rospy.init_node('accel', anonymous=True)
    rate = rospy.Rate(10) # 10hz
    while not rospy.is_shutdown():
        # hello_str = "hello world %s" % rospy.get_time()
        packetize_imu(get_accel())
        rospy.logdebug(pkt)
        pub.publish(pkt)
        rate.sleep()

if __name__ == '__main__':
    try:
        accel_talker()
    except rospy.ROSInterruptException:
        pass