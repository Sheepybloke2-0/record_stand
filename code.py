import asyncio
import board
import busio
import neopixel
import adafruit_framebuf
from adafruit_is31fl3731.matrix import Matrix as Display

i2c = busio.I2C(scl=board.GP1, sda=board.GP0)

LED_COUNT = 22
neopixels = neopixel.NeoPixel(board.GP16, LED_COUNT, brightness=0.75, auto_write=False)

display = Display(i2c)

text_to_show = "Now Playing"
music_notes_1 = (
    (1, 6),
    (1, 7),
    (2, 2),
    (2, 3),
    (2, 4),
    (2, 5),
    (2, 6),
    (2, 7),
    (3, 1),
    (4, 0),
    (4, 5),
    (4, 6),
    (5, 0),
    (5, 1),
    (5, 2),
    (5, 3),
    (5, 4),
    (5, 5),
    (5, 6),
    (8, 6),
    (8, 7),
    (9, 2),
    (9, 3),
    (9, 4),
    (9, 5),
    (9, 6),
    (9, 7),
    (10, 2),
    (11, 5),
    (11, 6),
    (12, 1),
    (12, 2),
    (12, 3),
    (12, 4),
    (12, 5),
    (12, 6),
)

music_notes_2 = (
    (1, 4),
    (1, 5),
    (2, 0),
    (2, 1),
    (2, 2),
    (2, 3),
    (2, 4),
    (2, 5),
    (3, 0),
    (4, 1),
    (4, 6),
    (4, 7),
    (5, 2),
    (5, 3),
    (5, 4),
    (5, 5),
    (5, 6),
    (5, 7),
    (8, 7),
    (8, 8),
    (9, 3),
    (9, 4),
    (9, 5),
    (9, 6),
    (9, 7),
    (9, 8),
    (11, 4),
    (11, 5),
    (12, 1),
    (12, 2),
    (12, 3),
    (12, 4),
    (12, 5),
    (13, 0),
)
music_notes = (music_notes_1, music_notes_2)

# Create a framebuffer for our display
buf = bytearray(32)  # 2 bytes tall x 16 wide = 32 bytes (9 bits is 2 bytes)
fb = adafruit_framebuf.FrameBuffer(
    buf, display.width, display.height, adafruit_framebuf.MVLSB
)


def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0:
        return (0, 0, 0)
    if pos > 255:
        return (0, 0, 0)
    if pos < 85:
        return (int(pos * 3), int(255 - (pos * 3)), 0)
    elif pos < 170:
        pos -= 85
        return (int(255 - pos * 3), 0, int(pos * 3))
    else:
        pos -= 170
        return (0, int(pos * 3), int(255 - pos * 3))


async def led_cycle(i: int = 0):
    while True:
        for j in range(LED_COUNT):
            idx = int((j * 256 / LED_COUNT) + i)
            neopixels[j] = wheel(idx % 255)
        neopixels.show()
        i = (i + 1) % 255
        await asyncio.sleep(0.01)


async def cycle_text(frame: int = 0):
    NOTE_CYCLES = 4
    while True:
        for k in range(len(text_to_show) * 9):
            fb.fill(0)
            fb.text(text_to_show, -k + display.width, 0, color=1)

            # to improve the display flicker we can use two frame
            # fill the next frame with scrolling text, then
            # show it.
            display.frame(frame, show=False)
            # turn all LEDs off
            display.fill(0)
            for x in range(display.width):
                # using the FrameBuffer text result
                bite = buf[x]
                for y in range(display.height):
                    bit = 1 << y & bite
                    # if bit > 0 then set the pixel brightness
                    if bit:
                        display.pixel(x, y, 128)

            # now that the frame is filled, show it.
            display.frame(frame, show=True)
            frame = 0 if frame else 1
            await asyncio.sleep(0)

        await asyncio.sleep(0.5)
        frame = 0
        display.sleep(True)  # turn display off while frames are updated
        display.fill(0)
        for note in music_notes:
            display.frame(frame, show=False)
            for pixel in note:
                display.pixel(pixel[0], pixel[1], 128)
            frame = 1
        display.sleep(False)  # turn display off while frames are updated
        for l in range(NOTE_CYCLES * len(music_notes)):
            display.frame(frame, show=True)
            frame = 0 if frame else 1
            await asyncio.sleep(1)


async def main():
    led_task = asyncio.create_task(led_cycle())
    text_task = asyncio.create_task(cycle_text())

    await asyncio.gather(led_task, text_task)


asyncio.run(main())
