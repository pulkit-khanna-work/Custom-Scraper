import pyautogui
from pyHM import mouse


def click(x, y):
    mouse.click(x, y)


def move(x, y):
    mouse.move(x, y)


def write(*args, interval=0.25):
    pyautogui.write(*args, interval=interval)
