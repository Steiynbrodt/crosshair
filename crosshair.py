import sys
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QPen, QColor
from PyQt6.QtWidgets import QApplication, QWidget


class CrosshairOverlay(QWidget):
    def __init__(self):
        super().__init__()

        # Crosshair appearance
        self.size = 12
        self.gap = 4
        self.thickness = 2
        self.outline = 1
        self.color = QColor(0, 255, 0)
        self.outline_color = QColor(0, 0, 0)

        # Window setup: transparent, always on top, click-through
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # Screen geometry
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)

        # Crosshair position (start centered)
        self.cx = self.width() // 2
        self.cy = self.height() // 2

        # Repaint timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(16)

        self.show()

    def draw_crosshair(self, p, cx, cy, size, gap, thickness, color):
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
            self.draw_crosshair(
                p,
                self.cx,
                self.cy,
                self.size,
                self.gap,
                self.thickness + 2 * self.outline,
                self.outline_color,
            )

        self.draw_crosshair(
            p,
            self.cx,
            self.cy,
            self.size,
            self.gap,
            self.thickness,
            self.color,
        )

    def keyPressEvent(self, e):
        step = 2  # pixels per press

        if e.key() == Qt.Key.Key_Escape:
            self.close()
            return

        if e.key() == Qt.Key.Key_Left:
            self.cx -= step
        elif e.key() == Qt.Key.Key_Right:
            self.cx += step
        elif e.key() == Qt.Key.Key_Up:
            self.cy -= step
        elif e.key() == Qt.Key.Key_Down:
            self.cy += step

        # keep inside screen
        self.cx = max(0, min(self.width(), self.cx))
        self.cy = max(0, min(self.height(), self.cy))

        self.update()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    overlay = CrosshairOverlay()
    sys.exit(app.exec())
