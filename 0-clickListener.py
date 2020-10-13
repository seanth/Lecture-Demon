import logging
import sys
import time

global theStart
theStart=time.time()

#https://pypi.org/project/pynput/
from pynput.keyboard import Key, Listener, KeyCode

logging.basicConfig(filename=("lectureTiming.txt"), filemode='w', level=logging.DEBUG, format='%(asctime)s, %(message)s')

def on_press(key):
    global theStart
    if (key == KeyCode.from_char('b') or
            key == Key.page_down or
            key == Key.page_up):
        theNow = time.time()
        theDelta = theNow-theStart
        #logging.info(str(key))
        logging.info(str(theDelta))
        theStart = theNow
    elif key == Key.esc:
        theNow = time.time()
        theDelta = theNow-theStart
        #logging.info(str(key))
        logging.info(str(theDelta))
        Listener.stop
        sys.exit()

with Listener(on_press=on_press) as listener:
    listener.join()


# from pynput.mouse import Listener
# def on_move(x, y):
#     logging.info("Mouse moved to ({0}, {1})".format(x, y))

# def on_click(x, y, button, pressed):
#     if pressed:
#         logging.info('Mouse clicked at ({0}, {1}) with {2}'.format(x, y, button))

# def on_scroll(x, y, dx, dy):
#     logging.info('Mouse scrolled at ({0}, {1})({2}, {3})'.format(x, y, dx, dy))

# with Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll) as listener:
#     listener.join()