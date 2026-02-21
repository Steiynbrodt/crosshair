import sys
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPainter, QPen, QColor
from PyQt6.QtWidgets import QApplication, QWidget

from pynput import keyboard


class CrosshairOverlay(QWidget):
    # thread-safe signal from pynput thread -> Qt UI thread
    nudge = pyqtSignal(int, int)
    quit_signal = pyqtSignal()

    def __init__(self):
        super().__init__()

        # Crosshair appearance
        self.size = 12
        self.gap = 4
        self.thickness = 2
        self.outline = 1
        self.color = QColor(0, 255, 0)
        self.outline_color = QColor(0, 0, 0)

        # Window: transparent, topmost, no frame, tool window
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # Cover primary screen
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)

        # Crosshair position
        self.cx = self.width() // 2
        self.cy = self.height() // 2

        # Signals
        self.nudge.connect(self._nudge_pos)
        self.quit_signal.connect(self.close)

        # Repaint timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(16)

        self.show()

        # Start global keyboard listener in background thread
        self.listener = keyboard.Listener(on_press=self._on_key_press)
        self.listener.start()

    def closeEvent(self, event):
        # Stop listener when closing
        try:
            if hasattr(self, "listener") and self.listener is not None:
                self.listener.stop()
        except Exception:
            pass
        super().closeEvent(event)

    def _on_key_press(self, key):
        # Global keys (works even when game is focused)
        step = 3  # pixels per press

        if key == keyboard.Key.esc:
            self.quit_signal.emit()
            return False  # stops listener

        if key == keyboard.Key.left:
            self.nudge.emit(-step, 0)
        elif key == keyboard.Key.right:
            self.nudge.emit(step, 0)
        elif key == keyboard.Key.up:
            self.nudge.emit(0, -step)
        elif key == keyboard.Key.down:
            self.nudge.emit(0, step)

    def _nudge_pos(self, dx, dy):
        self.cx += dx
        self.cy += dy

        # Keep inside screen
        self.cx = max(0, min(self.width(), self.cx))
        self.cy = max(0, min(self.height(), self.cy))

        self.update()

    def _draw_crosshair(self, p, cx, cy, size, gap, thickness, color):
        pen = QPen(color)
        pen.setWidth(thickness)
        p.setPen(pen)

        p.drawLine(cx - gap - size, cy, cx - gap, cy)
        p.drawLine(cx + gap, cy, cx + gap + size, cy)
        p.drawLine(cx, cy - gap - size, cx, cy - gap)
        p.drawLine(cx, cy + gap, cx, cy + gap + size)

    def paintEvent(self, event):
        p = QPainter(self)

        if self.outline:
            self._draw_crosshair(
                p, self.cx, self.cy,
                self.size, self.gap,
                self.thickness + 2 * self.outline,
                self.outline_color
            )

        self._draw_crosshair(
            p, self.cx, self.cy,
            self.size, self.gap,
            self.thickness,
            self.color
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    overlay = CrosshairOverlay()
    sys.exit(app.exec())
