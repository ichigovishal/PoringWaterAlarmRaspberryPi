from aiohttp import web
import asyncio
import time
import os
import aiohttp_jinja2
import jinja2
import RPi.GPIO as GPIO


PUMP_WAIT_TIME = 5
WAIT_TIME = PUMP_WAIT_TIME
CHN_IN = 20
CHN_OUT = 21
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
path_to_static_folder = os.path.join(BASE_DIR, "static")
path_to_template_folder = os.path.join(BASE_DIR, "template")


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
        self.WAIT_TIME = WAIT_TIME
        self.PUMP_WAIT_TIME = PUMP_WAIT_TIME
        self.water_pump = _Controller()

    def get_pump_wait_time(self):
        return self.PUMP_WAIT_TIME


class Alarm(_ALARM):

    async def alarm_act(self):
        update_wait_on_status(new_status=True)
        self.water_pump.turn_ON()
        print("Alarm-ACT")
        await asyncio.sleep(PUMP_WAIT_TIME)
        print("Alarm-OFF")
        self.water_pump.turn_OFF()
        self.water_pump.clear()
        await asyncio.sleep(60)
        return self.get_pump_wait_time()


class _StopButtonCheck:
    def __init__(self, new_status=False):
        self.new_status = new_status
        self.WAIT_TIME = WAIT_TIME
        self.water_pump = _Controller()
        self.ALARM_WAIT_ON = Alarm()


class StopButtonAutoCheck(_StopButtonCheck):

    async def autocheck(self):
        t_end = time.time() + self.WAIT_TIME
        while time.time() < t_end:
            # button_signal = GPIO.input(CHN_IN)
            button_signal = False
            if button_signal:
                self.water_pump.turn_OFF()
                print("Button pushed")
        await asyncio.sleep(.00001)
        return self.WAIT_TIME


async def main():
    try:
        task1 = Alarm()
        task1_act = task1.alarm_act()
        task2 = StopButtonAutoCheck()
        task2_act = task2.autocheck()
        total = asyncio.gather(task1_act, task2_act)
        await total
        return total.result()
    finally:
        clean = _Controller()
        clean.clear()



async def post_hander(request):
    data = await request.post()
    global PUMP_WAIT_TIME
    PUMP_WAIT_TIME = data.get('time')
    print(data)
    if data.get('name') in ["vishal", "prakhar", "abhinav"]:
        await main()
    return web.HTTPFound('/')


async def handler(request):
    context = {}
    response = aiohttp_jinja2.render_template('index.html',
                                              request,
                                              context)
    response.headers['Content-Language'] = 'ru'
    return response


def init_func(argv):
    env = jinja2
    env.Environment(auto_reload=True)
    routes = [web.get('/', handler),
              web.post('/request', post_hander),
              web.static('/static', path_to_static_folder, append_version=True)]
    app = web.Application()
    aiohttp_jinja2.setup(app, loader=env.FileSystemLoader(path_to_template_folder))
    app.add_routes(routes)
    web.run_app(app)
    return app

