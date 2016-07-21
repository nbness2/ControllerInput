from pywinusb import hid
from pyautogui import press, hotkey
from time import sleep


hids = hid.find_all_hid_devices()
with open('curr_hid.txt', 'r') as curr_hid:
    current_hid = curr_hid.readline().split(',')
curr_device = hids[int(current_hid[0])-1]


class Stick:

    def __init__(self, rdidx_x, rdidx_y, dead_zones_x, dead_zones_y, digital_xy=(False, False), low_xy=('low', 'low'),
                 high_xy=('high', 'high'), neutral_xy=('n/a', 'n/a')):
        self.rdidx_x = rdidx_x
        self.rdidx_y = rdidx_y
        self.dead_low_x, self.dead_high_x = dead_zones_x
        self.dead_low_y, self.dead_high_y = dead_zones_y
        self.digital_x, self.digital_y = digital_xy
        self.low_x, self.low_y = low_xy
        self.high_x, self.high_y = high_xy
        self.neut_x, self.neut_y = neutral_xy

    def update(self, value_xy):
        xy = []
        value_x, value_y = value_xy
        del value_xy
        if not self.digital_x:
            xy.append(value_x)
        else:
            if value_x >= self.dead_high_x:
                xy.append(self.high_x)
            elif value_x <= self.dead_low_x:
                xy.append(self.low_x)
            else:
                xy.append(self.neut_x)
        del value_x
        if not self.digital_y:
            xy.append(value_y)
        else:
            if value_y >= self.dead_high_y:
                xy.append(self.high_y)
            elif value_y <= self.dead_low_y:
                xy.append(self.low_y)
            else:
                xy.append(self.neut_y)
        return tuple(xy)


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

gcbuttons = ('lsx', 'lsy', 'lt', 'rt', 'csx', 'csy', 'buttons', 'dpad')


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
            print('recieving input after {} seconds.'.format(delay))
            sleep(delay)
            device.set_raw_data_handler(handle, (device.product_id, buttons))
            while device.is_plugged():
                sleep(1)
        else:
            print('device is not detected')
    finally:
        device.close()
        print('device closed successfully')

device_test(curr_device, gcbuttons)
