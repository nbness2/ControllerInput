from pywinusb import hid
from time import sleep


hids = hid.find_all_hid_devices()
with open('curr_hid.txt', 'r') as curr_hid:
    current_hid = curr_hid.readline().split(',')
curr_device = hids[int(current_hid[0])-1]

buttonmaps = {'0xbead': {'port': 0, 'lsx': 2, 'lsy': 6, 'lt': 10, 'csx': 14, 'csy': 18, 'rt': 22, 'buttons': (49, True), 'dpad': (50, True)}}


class Axis:

    def __init__(self, rdidx, dead_low, dead_high, digital=False, low_value='low', high_value='high', neutral_value='n/a'):
        self.rdidx = rdidx
        self.digital = digital
        if self.digital:
            self.dead_low = dead_low
            self.dead_high = dead_high
            self.low_value = low_value
            self.high_value = high_value
            self.neutral_value = neutral_value

    def update(self, value):
        if self.digital:
        #updates the value and then returns a value based on the update
            if value >= self.dead_high:
                return self.high_value
            elif value <= self.dead_low:
                return self.low_value
            else:
                return self.neutral_value
        else:
            return value


class Buttons:

    def __init__(self, rdidx, button_values):
        self.rdidx = rdidx
        self.button_values = button_values
        #should be tuple\list with button_count entries. little -> big ordered

    def update(self, value):
        try:
            pressed = []
            for idx, button in enumerate(value[::-1]):
                if int(button):
                    pressed.append(self.button_values[idx])
            if not len(pressed):
                return ['n/a']
            elif len(pressed) == 1:
                return pressed[0]
            else:
                return pressed
        except IndexError:
            raise IOError('Extra button(s) detected.')


buttonmaps = {'0xbead': {'lsx': Axis(2, 58, 68), 'lsy': Axis(6, 58, 67), 'lt': Axis(10, 10, 105), 'rt': Axis(22, 10, 105),
                         'csx': Axis(14, 59, 67), 'csy': Axis(18, 59, 68), 'buttons': Buttons(49, 'abxyzrl'), 'dpad': Buttons(50, 'udlr')}}


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
            component = buttonmaps[product_id][button]
            idx = component.rdidx
            if type(component) == Buttons:
                s += 'buttons: '+''.join(b for b in component.update(bin(data[idx])[2:]))
            elif type(component) == Axis:
                s += str(component.update(data[idx]))
            s += ' -- '
            del idx
        print(s[:-4])


def device_test(device, buttons=None, delay=1):
    try:
        if device.is_plugged():
            print('device is detected')
            device.open()
            print('device opened successfully')
            device.set_raw_data_handler(handle, (device.product_id, buttons))
            while device.is_plugged():
                sleep(1)
        else:
            print('device is not detected')
    finally:
        device.close()
        print('device closed successfully')

device_test(curr_device, gcbuttons)
