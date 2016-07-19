from pywinusb import hid
from time import sleep


hids = hid.find_all_hid_devices()
with open('curr_hid.txt', 'r') as curr_hid:
    current_hid = curr_hid.readline().split(',')
curr_device = hids[int(current_hid[0])-1]

buttonmaps = {'0xbead': {'port': 0, 'lsx': 2, 'lsy': 6, 'lt': 10, 'csx': 14, 'csy': 18, 'rt': 22, 'buttons': 49, 'dpad': 50}}

#gamecube
#[port, ?, Lsx, ?, ?, ?, -Lsy, ?, ?, ?, Lt, ?, ?, ?, Cx, ?, ?, ?, -Cy, ?, ?, ?, Rt, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, buttonval, dpadval, ???...]
#[1, 130, 62, 0, 0, 255, 63, 0, 0, 97, 15, 0, 0, 3, 62, 0, 0, 1, 63, 0, 0, 99, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]


def handle(data):
    print(data)


def test_device(device):
    #test your device
    try:
        if device.is_plugged():
            print('device is detected')
            device.open()
            print('device opened successfully')
            input('press enter to start recieving input after 3 seconds.')
            sleep(3)
            device.set_raw_data_handler(handle)
            while device.is_plugged():
                #this goes on while the device is plugged in and program is running
                sleep(1)
        else:
            print('device is not detected')
    finally:
        device.close()
        print('device closed successfully')

test_device(curr_device)
