#! /usr/bin/env python3

import asyncio
import monome

class GridStudies(monome.Monome):
    def __init__(self):
        super().__init__('/monome')

    def ready(self):
        self.buffer = monome.LedBuffer(self.width, self.height)

    def grid_key(self, x, y, s):
        print("key:", x, y, s)
        self.buffer.led_level_set(x, y, s*15)
        self.buffer.render(self)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    asyncio.async(monome.create_serialosc_connection(GridStudies))
    loop.run_forever()