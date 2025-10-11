import os, sys, time, threading, subprocess, ctypes
from datetime import datetime
from pathlib import Path

from PIL import ImageGrab
import winsound

# ----------- 配置 -----------
CFG = {
    "fps": 30,
    "output_dir": "records"
}
os.makedirs(CFG["output_dir"], exist_ok=True)

# ----------- 全局状态 -----------
recording = False
paused    = False
ffmpeg_proc = None

# ----------- 工具函数 -----------
def beep(f=1000, d=200):
    try: winsound.Beep(f, d)
    except: pass

def get_screen_wh():
    return ImageGrab.grab().size

def resource_path(relative_path):
    base_path = getattr(sys, "_MEIPASS", os.path.abspath(os.path.dirname(__file__)))
    return os.path.join(base_path, relative_path)

def start():
    global recording, ffmpeg_proc
    if recording: return
    w, h = get_screen_wh()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(CFG["output_dir"], f"{ts}.mp4")
    if getattr(sys, 'frozen', False):
        base_dir = Path(getattr(sys, '_MEIPASS'))
    else:
        base_dir = Path(__file__).parent
    print(base_dir)
    path = base_dir / 'assets/ffmpeg.exe'
    full_path = path.resolve()
    cmd = [
        full_path, "-y",
        "-f", "rawvideo",
        "-pix_fmt", "rgb24",
        "-s", f"{w}x{h}",
        "-r", str(CFG["fps"]),
        "-i", "-",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-pix_fmt", "yuv420p",
        out_path
    ]
    print(f'命令行：{cmd}')
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    si.wShowWindow = subprocess.SW_HIDE
    try:
        ffmpeg_proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, startupinfo=si)
    except Exception as e:
        # print(str(e))
        raise ValueError("FFmpeg未配置")


    recording = True
    beep(800, 150)
    print(f"🔴 开始录制 → {out_path}")
    threading.Thread(target=capture_loop, daemon=True).start()

def stop():
    global recording
    if not recording: return
    recording = False
    ffmpeg_proc.stdin.close()
    ffmpeg_proc.wait()
    beep(600, 300)
    print("✅ 录制结束")

def toggle_pause():
    global paused
    paused = not paused
    beep(500 if paused else 700, 150)
    print("⏸ 暂停" if paused else "▶️ 继续")

# ----------- 截图循环 -----------
def capture_loop():
    while recording:
        if not paused:
            img = ImageGrab.grab()
            ffmpeg_proc.stdin.write(img.tobytes())
        time.sleep(1/CFG["fps"])

# ----------- 热键注册 -----------
import ctypes.wintypes as wt
user32 = ctypes.WinDLL("user32", use_last_error=True)
RegisterHotKey = user32.RegisterHotKey
UnregisterHotKey = user32.UnregisterHotKey
GetMessageW = user32.GetMessageW
TranslateMessage = user32.TranslateMessage
DispatchMessageW = user32.DispatchMessageW

HOTKEYS = {
    1: (0x0001, ord('R')),   # ALT+R 开始
    2: (0x0001, ord('P')),   # ALT+P 暂停/继续
    3: (0x0001, ord('S')),   # ALT+S 停止
}

def register_hotkeys():
    for kid, (mods, vk) in HOTKEYS.items():
        if not RegisterHotKey(None, kid, mods, vk):
            print("❌ 注册热键失败")
            sys.exit(1)

def hotkey_loop():
    msg = wt.MSG()
    while GetMessageW(ctypes.byref(msg), 0, 0, 0) != 0:
        if msg.message == 0x0312:  # WM_HOTKEY
            kid = msg.wParam
            if kid == 1: start()
            elif kid == 2: toggle_pause()
            elif kid == 3: stop()
        TranslateMessage(ctypes.byref(msg))
        DispatchMessageW(ctypes.byref(msg))

if __name__ == "__main__":
    register_hotkeys()
    print("快捷键：ALT+R 开始  |  ALT+P 暂停/继续  |  ALT+S 停止")
    hotkey_loop()
