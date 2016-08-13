from pywinusb import hid
from pyautogui import press, hotkey
from time import sleep


hids = hid.find_all_hid_devices()
with open('curr_hid.txt', 'r') as curr_hid:
    current_hid = curr_hid.readline().split(',')
curr_device = hids[int(current_hid[0])-1]


class Stick:

    def __init__(self, rdidx_x, rdidx_y, dead_zones_x, dead_zones_y, digital_xy=(False, False), low_xy=('low', 'low'),
                 high_xy=('high', 'high'), neutral_xy=('n/a', 'n/a'), c_name='stick'):
        self.rdidx_x = rdidx_x
        self.rdidx_y = rdidx_y
        self.dead_low_x, self.dead_high_x = dead_zones_x
        self.dead_low_y, self.dead_high_y = dead_zones_y
        self.digital_x, self.digital_y = digital_xy
        self.low_x, self.low_y = low_xy
        self.high_x, self.high_y = high_xy
        self.neut_x, self.neut_y = neutral_xy
        self.c_name = c_name

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


class Button:

    def __init__(self, rdidx, button_values, digital=True, c_name='buttons'):
        self.rdidx = rdidx
        self.button_values = button_values
        self.digital = digital
        self.c_name = c_name
        #should be tuple\list with button_count entries. little -> big ordered

    def update(self, value):
        if not self.digital:
            return value
        else:
            try:
                pressed = []
                if type(value) == int:
                    value = bin(value)[2:]
                for idx, button in enumerate(value[::-1]):
                    if int(button):
                        pressed.append(self.button_values[idx])
                if not len(pressed):
                    return ['n/a']
                else:
                    return pressed
            except IndexError:
                raise IOError('Extra button(s) detected. {}'.format(self.c_name))

    def toggle_digital(self):
        self.set_digital(not self.digital)

    def set_digital(self, digital):
        self.digital = bool(digital)


class Controller:

    def __init__(self, **kwargs):
        self.components = {}
        for arg, value in kwargs.items():
            if arg in ['Sticks', 'Buttons']:
                for component in value:
                    self.components[component.c_name] = component
            if arg in ['c_name', 'product_id', 'vendor_id']:
                setattr(self, arg, value)

    def update(self, rawdata):
        data = {}
        for component in self.components.values():
            if type(component) == Stick:
                udata = (rawdata[component.rdidx_x], rawdata[component.rdidx_y])
            else:
                udata = rawdata[component.rdidx]
            data[component.c_name] = component.update(udata)
        return data


def handle(rawdata, controller):
    data = rawdata
    print(controller.update(rawdata))


def device_test(device, controller, delay=1):
    try:
        if device.is_plugged():
            print('device is detected')
            device.open()
            print('device opened successfully')
            print('recieving input after {} seconds.'.format(delay))
            sleep(delay)
            device.set_raw_data_handler(handle,  controller)
            while device.is_plugged():
                sleep(1)
        else:
            print('device is not detected')
    finally:
        device.close()
        print('device closed successfully')

device_test(curr_device, gcbuttons)
buttonmaps = {'0xbead': {'ls': Stick(2, 6, (59, 65), (59, 66), c_name='Left Stick'),
                         'lt': Button(10, ['lt'], False, c_name='Left Trigger'),
                         'rt': Button(22, ['rt'], False, c_name='Right Trigger'),
                         'cs': Stick(14, 18, (60, 66), (60, 65), c_name='C-Stick'),
                         'buttons': Button(49, 'abxyzrls', c_name='Buttons'),
                         'dpad': Button(50, 'udlr', c_name='D-pad')}}

controllers = {'vJoy - Gamecube': Controller(Sticks=(Stick(2, 6, (59, 65), (59, 66), c_name='Left Stick'),
                                                     Stick(14, 18, (60, 66), (60, 65), c_name='C-Stick')),
                                             Buttons=(Button(10, ['lt'], False, c_name='Left Trigger'),
                                                      Button(22, ['rt'], False, c_name='Right Trigger'),
                                                      Button(49, 'abxyzrls', c_name='Buttons'),
                                                      Button(50, 'udlr', c_name='D-pad')),
                                             c_name='Gamecube Controller',
                                             product_id='0xbead',
                                             vendor_id='0x1234')}

gcbuttons = ('ls', 'lt', 'rt', 'cs', 'buttons', 'dpad')

if __name__ == '__main__':
    pass
