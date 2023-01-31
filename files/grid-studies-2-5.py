#! /usr/bin/env python3

import asyncio
import monome

class GridStudies(monome.GridApp):
    def __init__(self):
        super().__init__()

    width = 0
    height = 0
    step = [[0 for col in range(16)] for row in range(16)]
    play_position = -1
    next_position = -1
    cutting = False
    loop_start = 0
    loop_end = width - 1
    keys_held = 0
    key_last = 0
    
    # when grid is plugged in via USB:
    def on_grid_ready(self):
        self.width = self.grid.width
        self.height = self.grid.height
        self.sequencer_rows = self.height-2
        self.connected = True

    def on_grid_disconnect(self,*args):
        self.connected = False

    async def play(self):
        while True:
            await asyncio.sleep(0.1)
            
            if self.cutting:
                self.play_position = self.next_position
            elif self.play_position == self.width - 1:
                self.play_position = 0
            elif self.play_position == self.loop_end:
                self.play_position = self.loop_start
            else:
                self.play_position += 1

            # TRIGGER SOMETHING
            for y in range(self.sequencer_rows):
                if self.step[y][self.play_position] == 1:
                    self.trigger(y)

            self.cutting = False

            if self.connected:
                self.draw()

    def trigger(self, i):
        print("triggered", i)

    def draw(self):
        buffer = monome.GridBuffer(self.width, self.height)

        # display steps
        for x in range(self.width):
            # highlight the play position
            if x == self.play_position:
                highlight = 4
            else:
                highlight = 0

            for y in range(self.sequencer_rows):
                buffer.led_level_set(x, y, self.step[y][x] * 11 + highlight)

        # draw trigger bar and on-states
        for x in range(self.width):
            buffer.led_level_set(x, self.sequencer_rows, 4)

        for y in range(self.sequencer_rows):
            if self.step[y][self.play_position] == 1:
                buffer.led_level_set(self.play_position, self.sequencer_rows, 15)

        # draw play position
        buffer.led_level_set(self.play_position, self.height-1, 15)

        # update grid
        buffer.render(self.grid)

    def on_grid_key(self, x, y, s):
        # toggle steps
        if s == 1 and y < self.sequencer_rows:
            self.step[y][x] ^= 1
            self.draw()
        # cut and loop
        elif y == self.height-1:
            self.keys_held = self.keys_held + (s * 2) - 1
            # cut
            if s == 1 and self.keys_held == 1:
                self.cutting = True
                self.next_position = x
                self.key_last = x
            # set loop points
            elif s == 1 and self.keys_held == 2:
                self.loop_start = self.key_last
                self.loop_end = x

async def main():
    loop = asyncio.get_event_loop()
    grid_studies = GridStudies()

    def serialosc_device_added(id, type, port):
        print('connecting to {} ({})'.format(id, type))
        asyncio.ensure_future(grid_studies.grid.connect('127.0.0.1', port))

    serialosc = monome.SerialOsc()
    serialosc.device_added_event.add_handler(serialosc_device_added)

    play_task = asyncio.create_task(grid_studies.play())

    await serialosc.connect()
    await loop.create_future()

if __name__ == '__main__':
    asyncio.run(main())