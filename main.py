import time
from dataclasses import astuple, dataclass, field
from pprint import pprint
from typing import Callable

from cv2 import cv2
import numpy as np
from PIL import Image
from mss import mss

import pyautogui
import keyboard
import mouse


def my_wait(condition: Callable, delay: float):
    while condition():
        time.sleep(delay)


def find(screen, template):
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    screen_gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
    res = cv2.matchTemplate(screen_gray, template_gray, cv2.TM_CCOEFF_NORMED)

    _, w, h = template.shape[::-1]
    threshold = 0.98
    loc = np.where(res >= threshold)
    for pt in zip(*loc[::-1]):
        return pt[0], pt[1]


def main():
    screenshot_pos_begin = (0, 0)
    screenshot_pos_end = pyautogui.size()
    # print(keyboard._canonical_names.canonical_names.items())

    with open('keys.txt', 'w', encoding='utf-8') as file:
        file.writelines([f'{a} : {b}\n' for a, b in keyboard._canonical_names.canonical_names.items()])

    while True:
        got_bobber = False
        template_bobber = None
        while not got_bobber:
            ...
            if keyboard.is_pressed('end'):
                region = (*screenshot_pos_begin,  # x_start, y_start
                          screenshot_pos_end[0] - screenshot_pos_begin[0],  # x_end - x_start = x_len
                          screenshot_pos_end[1] - screenshot_pos_begin[1])  # y_end - y_start = y_len

                print(f'{region=}')
                screenshot = pyautogui.screenshot(region=region)
                screenshot.show()
                template_bobber = screenshot
                got_bobber = True

            if keyboard.is_pressed('home'):
                print('Tap mouse left to set begin of screenshot area')

                my_wait(lambda: not mouse.is_pressed(mouse.RIGHT), 0.05)  # wait left right and get cursor pos

                screenshot_pos_begin = pyautogui.position()

                my_wait(lambda: mouse.is_pressed(mouse.RIGHT), 0.05)  # wait until mouse right released

                print(f'home pos changed to: {screenshot_pos_begin}')

                print('Tap mouse left to set end of screenshot area')

                my_wait(lambda: not mouse.is_pressed(mouse.RIGHT), 0.05)  # wait right click

                screenshot_pos_end = pyautogui.position()
                print(f'end pos changed to: {screenshot_pos_end}')

            # print(pyautogui.position())
            time.sleep(0.05)

        with mss() as sct:
            template_gray = cv2.cvtColor(np.array(template_bobber), cv2.COLOR_BGR2GRAY)
            template_edged = cv2.Canny(template_gray, 20, 20)
            while True:
                sct_img = sct.grab((0, 0, *pyautogui.size()))
                img = np.array(sct_img)

                gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
                edged = cv2.Canny(gray, 20, 20)

                res = cv2.matchTemplate(edged, template_edged, cv2.TM_CCOEFF)
                _, maxVal, _, maxLoc = cv2.minMaxLoc(res)

                cv2.rectangle(
                    edged,
                    (maxLoc[0], maxLoc[1]),
                    (maxLoc[0] + template_bobber.width, maxLoc[1] + template_bobber.height),
                    (255, 0, 0),
                    2
                )

                cv2.imshow('temp', template_edged)
                cv2.imshow('screen', edged)

                if (cv2.waitKey(1) & 0xFF) == ord('q'):
                    cv2.destroyAllWindows()
                    break


if __name__ == "__main__":
    main()
