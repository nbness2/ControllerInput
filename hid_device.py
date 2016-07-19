from pywinusb import hid
from time import sleep


hids = hid.find_all_hid_devices()
with open('curr_hid.txt', 'r') as curr_hid:
    current_hid = curr_hid.readline().split(',')
curr_device = hids[int(current_hid[0])-1]

buttonmaps = {'0xbead': {'port': 0, 'lsx': 2, 'lsy': 6, 'lt': 10, 'csx': 14, 'csy': 18, 'rt': 22, 'buttons': (49, True), 'dpad': (50, True)}}


def handle(rawdata, xargs=(None, None)):
    data = rawdata
    product_id = hex(xargs[0])
    buttons = xargs[1]
    del xargs
    if not buttons:
        print(data)
    else:
        s = ''
        for button in buttons:
            s += button+', '
            buttondata = buttonmaps[product_id][button]
            if type(buttondata) == int:
                s += str(data[buttondata])+' -- '
            else:
                s += bin(data[buttondata[0]])[2:]+' -- '
        print(s)


def test_device(device, buttons=None):
    try:
        if device.is_plugged():
            print('device is detected')
            device.open()
            print('device opened successfully')
            input('press enter to start recieving input after 3 seconds.')
            sleep(3)
            device.set_raw_data_handler(handle, (device.product_id, buttons))
            while device.is_plugged():
                sleep(1)
        else:
            print('device is not detected')
    finally:
        device.close()
        print('device closed successfully')

test_device(curr_device, ('dpad',))
