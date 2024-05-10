from typing import Final
import os
import pyautogui
import psutil
import time
import numpy
from . import window_finder
from .exceptions import WindowNotFoundError
from .displayscale import get_display_coordinates
from . import randstr

EXPORT_DIR:Final = '.\\.export'
TMP_DIR:Final = '.\\.tmp'
IMAGE_DIR:Final = '.\\images'
IMG_TIMEFRAC:Final = 'timefrac.png'
IMG_ZOOMOUT:Final = 'zoomout.png'

SECION_TARGET_RELATIVE_POS = (0, 200)
SECION_TARGET_SIZE = (None, 190)

SECION_HEADER_RELATIVE_POS = (140, 135)
SECTION_HEADER_SIZE = (-40, 170-135)
SECTION_SCROLL_RELATIVE_POS = (0, 406)
SECTION_SCROLL_SIZE = (None, 20)

SCROLL_PREVIOUS_REVERSE_POS = (-1285, -116)
SCROLL_NEXT_REVERSE_POS = (-42, -118)

ENDOFSCROLL_REVERSE_POS = (-60, -120)

SCREENSHOT_POS:Final = (285, 320)
SCREENSHOT_RANGE:Final = (820-285, 620-320)

os.makedirs(EXPORT_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(TMP_DIR, exist_ok=True)

class AudacityCapturer:
    __display_coordinates = None

    def __init__(self, scale=100):
        self.window = None
        self.scale = scale
        self.positions_cache = {}
        self.accuracy = 0.9
        self.verbose = False
        
        if windows := window_finder.find_window_by_procname('Audacity.exe'):
            self.window = windows[0]
        else:
            raise WindowNotFoundError()
    
    def vprint(self, *texts:str, end='\n'):
        if self.verbose:
            print(' '.join(str(n) for n in texts), end=end)

    def get_region_header(self):
        return self.__convert_region([*SECION_HEADER_RELATIVE_POS, *SECTION_HEADER_SIZE])
    
    def get_region_scroll(self):
        return self.__convert_region([*SECTION_SCROLL_RELATIVE_POS, *SECTION_SCROLL_SIZE])
    
    def make_region_freqeuncy(self, xfrom, xto, debug=False)->tuple[int,int,int,int]:
        x = xfrom
        width = xto - xfrom
        y = SECION_TARGET_RELATIVE_POS[1] + self.window.top
        height = SECION_TARGET_SIZE[1]
        
        if debug:
            y -= 200
            height += 200
        
        return x, y, width, height

    def __convert_position(self, x:int, y:int, reverse=False):
        if reverse:
            x = self.window.left + self.window.width + x
            y = self.window.top + self.window.height + y
        else:
            x += self.window.left
            y += self.window.top
        return x, y

    def __convert_region(self, source):
        region = [*source]
        region[0] += self.window.left
        region[1] += self.window.top
        if region[2] is None:
            region[2] = self.window.width - source[0]
        if region[2] < 0:
            region[2] = self.window.width - source[0] + region[2]
        if region[3] is None:
            region[3] = self.window.height - source[1]
        if region[3] < 0:
            region[3] = self.window.height - source[1] + region[3]
        return region
    
    @classmethod
    def __getimg(cls, image, scale=100):
        return os.path.join(IMAGE_DIR, str(scale), image)

    def validation_frequency(self, *times)->tuple[bool,dict,list]:
        times = [*times]
        times.sort()

        passed = {}
        failed = []
        isfail = False
        max_x = None
        region_header_original = list(self.get_region_header())
        region_header = region_header_original[:]
        for time in times:
            if isfail:
                self.vprint('AUTOFAIL', time)
                failed.append(time)
            else:
                img = self.__getimg(f'timeinfo/{time}.png', scale=self.scale)
                try:
                    print('region', region_header)
                    box = pyautogui.locateOnScreen(img, confidence=self.accuracy, region=region_header)
                except pyautogui.ImageNotFoundException:
                    self.vprint(f'FAIL(noimg) {time}')
                    failed.append(time)
                    continue
                except ValueError:
                    self.vprint(f'FAIL(exceed) {time}')
                    failed.append(time)
                    continue

                if max_x is None or max_x <= box.left:
                    max_x = box.left+5
                    passed[time] = box

                    region_header = region_header_original[:]
                    w = max_x - region_header[0]
                    region_header[0] += w
                    region_header[2] -= w
                    
                    self.vprint(f'PASS {time}')
                else:
                    isfail = True
                    failed.append(time)

                    self.vprint(f'FAIL {time}')
                    self.vprint(f'reason : max_x condition - {max_x} < {box.left}')
        return not bool(failed), passed, failed


    def capture_frequency(self, from_:str, to:str, *, check_timefrac=None, debug=False):
        if check_timefrac is None:
            check_timefrac = [from_, to]
        
        ispass, boxes, failed = self.validation_frequency(*check_timefrac)
        if not ispass:
            raise Exception(f"Validation Failed : {failed}")
        
        boxfrom = boxes[from_]
        boxfrom += 0, 0, 0, 32
        boxto = boxes[to]
        boxto += 0, 0, 0, 32
            
        try:
            xfrom = self.find_time_position(from_, region=boxfrom)
            xto = self.find_time_position(to, region=boxto)

            region = self.make_region_freqeuncy(xfrom, xto, debug=debug)
            if debug:
                self.capture(f'{self.title}_{from_}_{to}_DEBUG.png', pos=region)
            else:
                self.capture(f'{self.title}_{from_}_{to}.png', pos=region)
            
        except Exception:
            raise
        
    def find_time_position(self, timefrac:str, region=None):
        if region is None:
            region_header = self.get_region_header()
            region = region_header
        
        img_tf = self.__getimg(f'timeinfo\\{timefrac}.png', scale=self.scale)
        img_mark = self.__getimg(f'timemark.png', scale=self.scale)

        box = pyautogui.locateOnScreen(img_tf, confidence=self.accuracy, region=region)
        
        region = (box.left, box.top, box.width, box.height+16)
        box = pyautogui.locateOnScreen(img_mark, confidence=self.accuracy, region=region)
        
        return box.left + 1

    def parse_position_each_time(self):
        img_timrfrac = self.__getimg('frac.png', scale=self.scale)
        img_timemark = self.__getimg('timemark.png', scale=self.scale)
        region_header = self.get_region_header()
        try:
            for box in pyautogui.locateAllOnScreen(img_timrfrac, confidence=self.accuracy, region=region_header):
                x, y = int(box[0]-16), int(box[1])
                self.capture_temporary(pos=(x-16, y, 48, 18))
        except pyautogui.ImageNotFoundException:
            print("not found")
            return None
        
    def capture_timefrac(self):
        img_timrfrac = self.__getimg('frac.png', scale=self.scale)
        img_timemark = self.__getimg('timemark.png', scale=self.scale)
        region_header = self.get_region_header()
        try:
            for box in pyautogui.locateAllOnScreen(img_timrfrac, confidence=self.accuracy, region=region_header):
                x, y = int(box[0]-16), int(box[1])
                self.capture_temporary(pos=(x-16, y, 48, 18))
        except pyautogui.ImageNotFoundException:
            print("not found")
            return None
    
    def capture_temporary(self, pos:tuple[int,int,int,int])->str:
        filename = randstr.generate_with_date(4, include_microsec=True).lower() + '.png'
        self.capture(filename, pos=pos, directory=TMP_DIR)
        return filename
        
    def capture(self, filename:str, pos:tuple[int,int,int,int], directory=None):
        if type(pos[0]) is not int or type(pos[1]) is not int:
            pos = [int(i) for i in pos]
        if directory is None:
            directory = '.export'

        screenshot = pyautogui.screenshot(region = pos)
        screenshot.save(os.path.join(directory, filename))
    
    def isendofscroll(self)->bool:
        x, y = self.__convert_position(*ENDOFSCROLL_REVERSE_POS, reverse=True)
        color = pyautogui.pixel(x, y)

        return color == (133, 133, 133)

    def scroll_next(self, count=2):
        x, y = self.__convert_position(*SCROLL_NEXT_REVERSE_POS, reverse=True)
        print(x, y)
        pyautogui.moveTo(x, y)
        pyautogui.click(clicks=count)
        
    def scroll_previous(self, count=2):
        x, y = self.__convert_position(*SCROLL_PREVIOUS_REVERSE_POS, reverse=True)
        pyautogui.moveTo(x, y)
        pyautogui.click(clicks=count)

    def test_capture(self):
        region = self.get_region_header()
        self.capture('region-header.png', directory='.tmp', pos=region)

    @property
    def title(self):
        return self.window.title
    
    def position(self)->list[int, int]:
        return self.window.left, self.window.top

    def size(self)->list[int, int]:
        return self.window.width, self.window.height

def screenshot(path:str):
    left, top, width, height = 0, 0, 1920, 1080
    screenshot = pyautogui.screenshot(region=(left, top, width, height))
    screenshot.save(path)