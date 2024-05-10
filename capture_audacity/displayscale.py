import ctypes
import ctypes.wintypes
import win32api
import pywintypes

user32 = ctypes.windll.user32

def get_display_count():
    # 연결된 모든 디스플레이의 수를 가져오는 Win32 API 호출
    num_displays = win32api.GetSystemMetrics(80)  # SM_CMONITORS: 연결된 모니터의 수
    return num_displays

def get_display_scales():
    # Get the number of monitors
    monitors = ctypes.windll.shcore.GetSystemMetrics(77)
    monitor_scales = []

    for i in range(monitors):
        # Get the handle of the monitor
        monitor = ctypes.windll.user32.MonitorFromPoint(0, i)
        # Get the scale of the monitor
        scale = ctypes.windll.user32.GetScaleFactorForDevice(monitor, 0)
        monitor_scales.append(scale)

    return monitor_scales

def get_display_coordinates():
    displays = win32api.EnumDisplayMonitors(0, None)
    
    coords = []
    for display in displays:
        coords.append(display[2])

    return coords

def get_main_display_scale():
    return ctypes.windll.shcore.GetScaleFactorForDevice(0)


if __name__ == "__main__":
    pass