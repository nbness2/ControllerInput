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

    def __init__(self, rdidx, button_values, digital=True, c_name=None):
        self.rdidx = rdidx
        self.button_values = button_values
        self.digital = digital
        if c_name:
            self.c_name = c_name
        else:
            self.c_name = 'unidentified'
        #should be tuple\list with button_count entries. little -> big ordered

    def update(self, value):
        if not self.digital:
            return value
        else:
            try:
                pressed = []
                for idx, button in enumerate(value[::-1]):
                    if int(button):
                        pressed.append(self.button_values[idx])
                if not len(pressed):
                    return ['n/a']
                else:
                    return pressed
            except IndexError:
                raise IOError('Extra button(s) detected. {}'.format(self.c_name))


buttonmaps = {'0xbead': {'ls': Stick(2, 6, (59, 65), (59, 66)), 'lt': Buttons(10, ['lt'], False), 'rt': Buttons(22, ['rt'], False),
                         'cs': Stick(14, 18, (60, 66), (60, 65)), 'buttons': Buttons(49, 'abxyzrls'), 'dpad': Buttons(50, 'udlr')}}

gcbuttons = ('ls', 'lt', 'rt', 'cs', 'buttons', 'dpad')


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
            if type(component) == Buttons:
                idx = component.rdidx
                if component.digital:
                    s += 'buttons: '+''.join(b for b in component.update(bin(data[idx])[2:]))
                else:
                    s += str(component.update(data[idx]))
            elif type(component) == Stick:
                idx_x, idx_y = component.rdidx_x, component.rdidx_y
                s += str(component.update((data[idx_x], data[idx_y])))
            s += ' -- '
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
