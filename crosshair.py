import sys
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QPen, QColor
from PyQt6.QtWidgets import QApplication, QWidget

class CrosshairOverlay(QWidget):
    def __init__(self):
        super().__init__()

        # Crosshair settings
        self.size = 12
        self.gap = 4
        self.thickness = 2
        self.outline = 1
        self.color = QColor(0, 255, 0)
        self.outline_color = QColor(0, 0, 0)

        # Window flags: always on top, no frame, click-through
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )

        # Transparent + click-through
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # Cover primary screen
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)

        # Repaint timer (~60 FPS)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(16)

        self.show()

    def draw_crosshair(self, p, cx, cy, size, gap, thickness, color):
        pen = QPen(color)
        pen.setWidth(thickness)
        p.setPen(pen)

        # Left
        p.drawLine(cx - gap - size, cy, cx - gap, cy)
        # Right
        p.drawLine(cx + gap, cy, cx + gap + size, cy)
        # Up
        p.drawLine(cx, cy - gap - size, cx, cy - gap)
        # Down
        p.drawLine(cx, cy + gap, cx, cy + gap + size)

    def paintEvent(self, event):
        p = QPainter(self)
        cx = self.width() // 2
        cy = self.height() // 2

        # Outline
        if self.outline:
            self.draw_crosshair(
                p, cx, cy,
                self.size, self.gap,
                self.thickness + 2 * self.outline,
                self.outline_color
            )

        # Main
        self.draw_crosshair(
            p, cx, cy,
            self.size, self.gap,
            self.thickness,
            self.color
        )

    def keyPressEvent(self, e):
        k = e.key()

        if k == Qt.Key.Key_Escape:
            self.close()

        elif k in (Qt.Key.Key_Plus, Qt.Key.Key_Equal):
            self.size = min(200, self.size + 1)

        elif k == Qt.Key.Key_Minus:
            self.size = max(1, self.size - 1)

        elif k == Qt.Key.Key_BracketLeft:
            self.gap = max(0, self.gap - 1)

        elif k == Qt.Key.Key_BracketRight:
            self.gap = min(100, self.gap + 1)

        elif k == Qt.Key.Key_O:
            self.outline = 0 if self.outline else 1

        self.update()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    overlay = CrosshairOverlay()
    sys.exit(app.exec())