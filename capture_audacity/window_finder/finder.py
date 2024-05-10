import win32gui
import win32process
import pygetwindow as gw
import pygetwindow
import psutil
import ctypes

EnumWindows = ctypes.windll.user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
GetWindowText = ctypes.windll.user32.GetWindowTextW
GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
IsWindowVisible = ctypes.windll.user32.IsWindowVisible

def get_pid_by_name(process_name):
    qobuz_pids = []

    for proc in psutil.process_iter():
        if process_name in proc.name():
            qobuz_pids.append(proc.pid)

    return qobuz_pids

def get_windows_by_pid(hwnd_list:list):
    windows = []
    for window in pygetwindow.getAllWindows():
        if window._hWnd in hwnd_list:
            windows.append(window)
    return windows

def get_hwnd_by_pid(pid_list:list):
    def callback(hwnd, hwnds):
        _, found_pid = win32process.GetWindowThreadProcessId(hwnd)

        if found_pid in pid_list:
            hwnds.append(hwnd)
        return True
    hwnds = []
    win32gui.EnumWindows(callback, hwnds)
    return hwnds

def find_window_by_procname(process_name):
    pid_list = get_pid_by_name(process_name)
    if not pid_list:
        return []
    
    hwnd_list = get_hwnd_by_pid(pid_list)
    if not hwnd_list:
        return []
    return get_windows_by_pid(hwnd_list)