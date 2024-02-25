import sys
from PySide6.QtCore import Qt, QPointF, QRect, QSize
from PySide6.QtGui import QPixmap, QPainter, QPen, QIcon, QImage
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QGraphicsScene, QGraphicsView, QRubberBand, QColorDialog

class Widget(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setGeometry(0, 0, 800, 600)
        self.setWindowTitle('PhotoEdit')

        main_layout = QVBoxLayout(self)

        toolbar_layout = QHBoxLayout()
        self.pushButton_5 = QPushButton('Open', self)
        self.pushButton_4 = QPushButton('New', self)
        self.pushButton_3 = QPushButton('Crop', self)
        self.pushButton_2 = QPushButton('Grayscale', self)
        self.pushButton = QPushButton('Draw', self)
        self.color_button = QPushButton('Select Color', self)
        self.save_button = QPushButton('Save', self)

        self.pushButton_5.setIcon(QIcon.fromTheme('document-open'))
        self.pushButton_4.setIcon(QIcon.fromTheme('document-new'))
        self.pushButton_3.setIcon(QIcon.fromTheme('edit-cut'))
        self.pushButton_2.setIcon(QIcon.fromTheme('image-filter-grayscale'))
        self.pushButton.setIcon(QIcon.fromTheme('draw-brush'))
        self.color_button.setIcon(QIcon.fromTheme('color-picker'))
        self.save_button.setIcon(QIcon.fromTheme('document-save'))

        toolbar_layout.addWidget(self.pushButton_5)
        toolbar_layout.addWidget(self.pushButton_4)
        toolbar_layout.addWidget(self.pushButton_3)
        toolbar_layout.addWidget(self.pushButton_2)
        toolbar_layout.addWidget(self.pushButton)
        toolbar_layout.addWidget(self.color_button)
        toolbar_layout.addWidget(self.save_button)

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene, self)
        self.view.setGeometry(0, 0, 800, 600)

        self.rubber_band = QRubberBand(QRubberBand.Rectangle, self.view)
        self.start_point = QPointF()
        self.line_color = Qt.red

        main_layout.addLayout(toolbar_layout)
        main_layout.addWidget(self.view)

        self.setLayout(main_layout)

        self.pushButton_5.clicked.connect(self.openImage)
        self.pushButton_4.clicked.connect(self.newImage)
        self.pushButton_3.clicked.connect(self.cropImage)
        self.pushButton_2.clicked.connect(self.grayscaleImage)
        self.pushButton.clicked.connect(self.drawLine)
        self.color_button.clicked.connect(self.chooseColor)
        self.save_button.clicked.connect(self.saveImage)

        self.selection_rect = None

    def saveImage(self):
        if not self.scene.items():
            return

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        options |= QFileDialog.DontUseCustomDirectoryIcons
        filters = "PNG(*.png);;JPG(*.jpg);;BMP(*.bmp);;All Files (*)"
        fileName, selected_filter = QFileDialog.getSaveFileName(self, "Save Image", "", filters, "", options=options)

        if fileName:
            pixmap = self.scene.items()[0].pixmap()

            format = selected_filter.split("(*.")[1][:-1] if "(*." in selected_filter else None
            fileName += "." + format
            pixmap.save(fileName, format)

    def openImage(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.bmp);;All Files (*)", options=options)
        if fileName:
            pixmap = QPixmap(fileName)
            self.scene.clear()
            self.scene.addPixmap(pixmap)

            self.view.mousePressEvent = None
            self.view.mouseMoveEvent = None
            self.view.mouseReleaseEvent = None



    def newImage(self):
        self.scene.clear()
        blank_pixmap = QPixmap(800, 600)
        blank_pixmap.fill(Qt.white)
        self.scene.addPixmap(blank_pixmap)

    def cropImage(self):
        if not self.scene.items():
            return

        self.rubber_band.setGeometry(QRect())

        def mousePressEvent(event):
            self.start_point = event.pos()
            self.rubber_band.setGeometry(QRect(self.start_point, QSize()))

        def mouseMoveEvent(event):
            if not self.start_point.isNull():
                rect = QRect(self.start_point, event.pos()).normalized()
                self.rubber_band.setGeometry(rect)
                self.rubber_band.show()

        def mouseReleaseEvent(event):
            if not self.start_point.isNull():
                rect = QRect(self.start_point, event.pos()).normalized()
                self.rubber_band.setGeometry(rect)

                pixmap = self.scene.items()[0].pixmap()
                cropped_pixmap = pixmap.copy(rect)
                self.scene.clear()
                self.scene.addPixmap(cropped_pixmap)

                self.start_point = QPointF()
                self.rubber_band.hide()

        self.view.mousePressEvent = mousePressEvent
        self.view.mouseMoveEvent = mouseMoveEvent
        self.view.mouseReleaseEvent = mouseReleaseEvent


        self.view.mousePressEvent = mousePressEvent
        self.view.mouseMoveEvent = mouseMoveEvent
        self.view.mouseReleaseEvent = mouseReleaseEvent

    def grayscaleImage(self):
        if not self.scene.items():
            return

        pixmap = self.scene.items()[0].pixmap()
        image = pixmap.toImage()

        grayscale = image.convertToFormat(QImage.Format_Grayscale8)
        grayscale_pixmap = QPixmap.fromImage(grayscale)
        self.scene.clear()
        self.scene.addPixmap(grayscale_pixmap)

    def drawLine(self):
        self.drawing = False
        self.last_point = QPointF()

        def mousePressEvent(event):
            self.last_point = self.view.mapToScene(event.pos())
            self.drawing = True

        def mouseMoveEvent(event):
            if not self.drawing:
                return

            scene_pos = self.view.mapToScene(event.pos())
            pixmap = self.scene.items()[0].pixmap()
            image = pixmap.toImage()

            painter = QPainter(image)
            pen = QPen(self.line_color, 2)
            painter.setPen(pen)
            painter.drawLine(self.last_point, scene_pos)
            self.last_point = scene_pos
            painter.end()

            self.scene.clear()
            self.scene.addPixmap(QPixmap.fromImage(image))

        def mouseReleaseEvent(event):
            self.drawing = False

        self.view.mousePressEvent = mousePressEvent
        self.view.mouseMoveEvent = mouseMoveEvent
        self.view.mouseReleaseEvent = mouseReleaseEvent

    def chooseColor(self):
        color = QColorDialog.getColor(initial=self.line_color, parent=self)
        if color.isValid():
            self.line_color = color

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = Widget()
    widget.show()
    sys.exit(app.exec())
