import sys
import ctypes
from ctypes import wintypes

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPainter, QPen, QColor
from PyQt6.QtWidgets import QApplication, QWidget
from pynput import keyboard

user32 = ctypes.WinDLL("user32", use_last_error=True)

GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x00080000
WS_EX_TRANSPARENT = 0x00000020
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_NOACTIVATE = 0x08000000

HWND_TOPMOST = -1
SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
SWP_NOACTIVATE = 0x0010
SWP_SHOWWINDOW = 0x0040

user32.GetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int]
user32.GetWindowLongW.restype = ctypes.c_long
user32.SetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_long]
user32.SetWindowLongW.restype = ctypes.c_long
user32.SetWindowPos.argtypes = [
    wintypes.HWND, wintypes.HWND,
    ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
    wintypes.UINT
]
user32.SetWindowPos.restype = wintypes.BOOL


class CrosshairOverlay(QWidget):
    nudge = pyqtSignal(int, int)
    quit_signal = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.size = 12
        self.gap = 4
        self.thickness = 2
        self.outline = 1
        self.color = QColor(0, 255, 0)
        self.outline_color = QColor(0, 0, 0)

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)

        self.cx = self.width() // 2
        self.cy = self.height() // 2

        self.nudge.connect(self._nudge_pos)
        self.quit_signal.connect(self.close)

        self.show()
        self._apply_clickthrough_styles()

        self.topmost_timer = QTimer(self)
        self.topmost_timer.timeout.connect(self._force_topmost)
        self.topmost_timer.start(500)
        self._force_topmost()

        self.paint_timer = QTimer(self)
        self.paint_timer.timeout.connect(self.update)
        self.paint_timer.start(16)

        self.listener = keyboard.Listener(on_press=self._on_key_press)
        self.listener.start()

    def _hwnd(self):
        return int(self.winId())

    def _apply_clickthrough_styles(self):
        hwnd = self._hwnd()
        ex = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        ex |= (WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE)
        user32.SetWindowLongW(hwnd, GWL_EXSTYLE, ex)

    def _force_topmost(self):
        hwnd = self._hwnd()
        user32.SetWindowPos(
            hwnd, HWND_TOPMOST,
            0, 0, 0, 0,
            SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_SHOWWINDOW
        )

    def _on_key_press(self, key):
        step = 3

        # Only ESC exits
        if key == keyboard.Key.esc:
            self.quit_signal.emit()
            return False

        if key == keyboard.Key.left:
            self.nudge.emit(-step, 0)
        elif key == keyboard.Key.right:
            self.nudge.emit(step, 0)
        elif key == keyboard.Key.up:
            self.nudge.emit(0, -step)
        elif key == keyboard.Key.down:
            self.nudge.emit(0, step)

    def _nudge_pos(self, dx, dy):
        self.cx = max(0, min(self.width(), self.cx + dx))
        self.cy = max(0, min(self.height(), self.cy + dy))
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)

        def draw(cx, cy, thickness, color):
            pen = QPen(color)
            pen.setWidth(thickness)
            p.setPen(pen)
            p.drawLine(cx - self.gap - self.size, cy, cx - self.gap, cy)
            p.drawLine(cx + self.gap, cy, cx + self.gap + self.size, cy)
            p.drawLine(cx, cy - self.gap - self.size, cx, cy - self.gap)
            p.drawLine(cx, cy + self.gap, cx, cy + self.gap + self.size)

        if self.outline:
            draw(self.cx, self.cy, self.thickness + 2 * self.outline, self.outline_color)
        draw(self.cx, self.cy, self.thickness, self.color)

    def closeEvent(self, event):
        try:
            if getattr(self, "listener", None):
                self.listener.stop()
        except Exception:
            pass
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    overlay = CrosshairOverlay()
    sys.exit(app.exec())
