import pyautogui
import psutil
import pyautogui
import time
from capture_audacity import AudacityCapturer, EndOfRange
from typing import Final
import argparse
import mouse

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--scale', default=125, type=int, help='set display scale menually')
parser.add_argument('-p', '--period', default=2, type=int, help='set display scale menually')
parser.add_argument('--start', default=0, type=int, help='set display scale menually')
parser.add_argument('-c', '--capture', action='store_true')
parser.add_argument('-t', '--test', action='store_true')
parser.add_argument('-e', '--extract', action='store_true')
parser.add_argument('--mouse', action='store_true')
args = parser.parse_args()

def main():
    def update_scroll(needed:list[int]):
        needed = needed[:]
        needed.sort()
        while True:
            time.sleep(1)
            ispass, passed, failed = capturer.validation_frequency(*needed, )
            print('P/F:', passed, failed)

            if ispass:
                return True
            elif capturer.isendofscroll():
                raise EndOfRange()
            elif failed != needed:
                n = len(failed)
                if needed[:n] == failed: # 앞부분 매치
                    capturer.scroll_previous(2)
                    continue
                elif needed[-n:] == failed: # 뒷부분 매치
                    capturer.scroll_next(2)
                    continue
                
            print('자동으로 조절할 수 없습니다')
            print('수동으로 스크롤 조절후 ENTER를 눌러주세요')
            print('NEEDED :', *needed)
            print("PASSED :", *passed)
            print("FAILED :", *failed)
            input('Press Enter...')
                
    index = args.start
    period = args.period
    capturer = AudacityCapturer(scale=args.scale)
    visibled = list(range(index, index+5))

    update_scroll(visibled)
    try:
        while True:
            if index in visibled and index+period in visibled:
                print('capture:', index, index+period)
                capturer.capture_frequency(index, index+period, check_timefrac=visibled)
                capturer.capture_frequency(index, index+period, check_timefrac=visibled, debug=True)
                index += period
            else:
                print('add', visibled)
                del visibled[0]
                num = visibled[-1]+1
                if num // 60 > 0:
                    a = num // 60
                    b = num % 60
                    visibled.append(a*100+b)
                else:
                    visibled.append(num)
                update_scroll(visibled)
    except EndOfRange:
        pass

def extact_timefrac_img():
    capturer = AudacityCapturer(scale=args.scale)
    print('저장 위치 : ./tmp')
    print('추출할 timefrac 이 보이도록 스크롤을 두고 Enter')
    while True:
        input()
        capturer.capture_timefrac()
        print('capture')
        

def trace_mouse():
    capturer = AudacityCapturer(scale=args.scale)
    pressed = False
    lastpressed = False

    print('position:', capturer.position())
    print('size:', capturer.size())
    try:
        while True:
            lastpressed = pressed
            posx, posy = capturer.position()
            x, y = pyautogui.position()
            width, height = capturer.size()
            
            nx = x - posx
            ny = y - posy
            rx = nx - width
            ry = ny - height
            posstr = f'N({x-posx}, {y-posy}) R({rx}, {ry}) : G({x}, {y})'
            
            pressed = mouse.is_pressed('left')
            if pressed and not lastpressed:
                print('click:', posstr, ' '*10)
            else:
                print(posstr, ' '*10, end='\r')
    except KeyboardInterrupt:
        pass

def capture():
    capturer = AudacityCapturer(scale=args.scale)
    capturer.test_capture()

def test():
    capturer = AudacityCapturer(scale=args.scale)
    visibled = [0,1,2,3,4,5,6,7]
    capturer.accuracy = 0.85
    capturer.verbose = True
    print(capturer.validation_frequency(*visibled))

if __name__ == "__main__":
    if args.extract:
        extact_timefrac_img()
    elif args.test:
        test()
    elif args.capture:
        capture()
    elif args.mouse:
        trace_mouse()
    else:
        main()
    #print(capturer.find_time())
    