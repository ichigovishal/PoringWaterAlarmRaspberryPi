import asyncio
import time
import datetime
import RPi.GPIO as GPIO


CHECK_BUTTON_ON = False
ALARM_OFF_STATUS = False
ALARM_WAIT_ON = True
MINUTE = 10
HOUR = 8
DAY = [2]
WAIT_TIME = 30
PUMP_WAIT_TIME = 2
CHN_IN = 20
CHN_OUT = 21


def get_wait_on_status():
    return ALARM_WAIT_ON


def update_wait_on_status(new_status):
    global ALARM_WAIT_ON
    ALARM_WAIT_ON = new_status
    return ALARM_WAIT_ON


class _Controller:
    def __init__(self):
        pass

    def turn_ON(self):
        turn_on = True
        GPIO.output(CHN_OUT, True)
        return turn_on

    def turn_OFF(self):
        turn_off = True
        GPIO.output(CHN_OUT, False)
        return turn_off

    def clear(self):
        clear = True
        GPIO.cleanup()
        return clear


class _ALARM:
    def __init__(self):
        self.ALARM_OFF_STATUS = ALARM_OFF_STATUS
        self.CHECK_BUTTON_ON = CHECK_BUTTON_ON
        self.MINUTE = MINUTE
        self.WAIT_TIME = WAIT_TIME
        self.HOUR = HOUR
        self.DAY = DAY
        self.ALARM_TIME = datetime.timedelta(hours=self.HOUR, minutes=self.MINUTE)
        self.PUMP_WAIT_TIME = PUMP_WAIT_TIME
        self.water_pump = _Controller()

    def check_alarm_off_status(self):
        return self.ALARM_OFF_STATUS

    def update_alarm_status(self):
        self.ALARM_OFF_STATUS = self.CHECK_BUTTON_ON
        return self.ALARM_OFF_STATUS

    def get_alarm_time(self):
        return self.ALARM_TIME

    def get_alarm_day(self):
        return self.DAY

    def current_time(self):
        hour = int(datetime.datetime.now().strftime('%H'))
        minute = int(datetime.datetime.now().strftime('%M'))
        return datetime.timedelta(hours=hour, minutes=minute)

    def current_day(self):
        return datetime.date.today().weekday()

    def get_pump_wait_time(self):
        return self.PUMP_WAIT_TIME


class Alarm(_ALARM):
    def is_alarm_ring_time(self):
        if self.check_alarm_off_status() is False and self.current_day() in self.get_alarm_day() and self.current_time() == self.get_alarm_time():
            return True
        else:
            return False

    async def alarm_act(self):
        if self.is_alarm_ring_time() is True:
            update_wait_on_status(new_status=True)
            self.water_pump.turn_ON()
            print("Alarm-ACT")
            await asyncio.sleep(self.get_pump_wait_time())
            print("Alarm-OFF")
            self.water_pump.turn_OFF()
            self.water_pump.clear()
            return self.get_pump_wait_time()

        else:
            update_wait_on_status(new_status=False)
            print("Sleep-IN")
            time.sleep(60)
            print("Sleep-OUT")
            self.water_pump.clear()


class _StopButtonCheck:
    def __init__(self, new_status=False):
        self.current_state = CHECK_BUTTON_ON
        self.new_status = new_status
        self.ALARM_WAIT_ON = ALARM_WAIT_ON
        self.WAIT_TIME = WAIT_TIME
        self.CHECK_BUTTON_ON = CHECK_BUTTON_ON
        self.water_pump = _Controller()
        self.ALARM_WAIT_ON = Alarm()

    def get_current_status(self):
        return self.current_state

    def create_new_status(self, _new_status):
        _new_status = self.new_status
        self.CHECK_BUTTON_ON = _new_status
        return self.current_state


class StopButtonAutoCheck(_StopButtonCheck):

    async def autocheck(self):
        if get_wait_on_status() is True:
            t_end = time.time() + self.WAIT_TIME
            while time.time() < t_end:
                button_signal = GPIO.input(CHN_IN)
                self.create_new_status(_new_status=button_signal)
                if button_signal:
                    self.water_pump.clear()
                    print("Button pushed")
        await asyncio.sleep(.00001)
        return self.ALARM_WAIT_ON


async def main():
    task1 = Alarm()
    task1_act = task1.alarm_act()
    task2 = StopButtonAutoCheck()
    task2_act = task2.autocheck()

    await asyncio.gather(task1_act, task2_act)


while True:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(CHN_IN, GPIO.IN, GPIO.PUD_DOWN)
        GPIO.setup(CHN_OUT, GPIO.OUT)
        asyncio.run(main())
