import sys
import os
from typing import Optional
from image_resizer_ui import Ui_MainWindow
from PyQt5.QtWidgets import (
    QMainWindow,
    QApplication,
    QWidget,
    QFileDialog,
    QScroller,
    QCompleter,
    QFileSystemModel,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

HOME_PATH = os.path.expanduser("~")


class ImageResizer(QMainWindow, Ui_MainWindow):
    def __init__(
        self,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        super().setupUi(self)

        # Setting up file completer for inputFileEdit
        completer = QCompleter(self)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        fs_model = QFileSystemModel(completer)
        fs_model.setRootPath(HOME_PATH)
        fs_model.setNameFilters(("*.png", "*.jpg"))
        completer.setModel(fs_model)
        self.inputFileEdit.setCompleter(completer)

        # Make scroll possible by mouse drag in imageScrollArea
        QScroller.grabGesture(self.imageScrollArea, QScroller.LeftMouseButtonGesture)

        # Setting widgets initial states
        self.inputFileEdit.setFocus()
        self.imageLabel.setText("To start, choose an image file.")
        self.widthEdit.setEnabled(False)
        self.heightEdit.setEnabled(False)
        self.ratioCheckBox.setCheckState(Qt.CheckState.Checked)
        self.ratioCheckBox.setEnabled(False)
        self.saveButton.setEnabled(False)
        self.resizeButton.setEnabled(False)

        self.image = None
        self.resized_image = None

        # Connecting signals
        self.inputFileButton.clicked.connect(self.image_from_dialog)
        self.inputFileEdit.editingFinished.connect(self.image_from_edit)
        self.widthEdit.editingFinished.connect(self.width_watcher)
        self.heightEdit.editingFinished.connect(self.height_watcher)
        self.saveButton.clicked.connect(self.save_image)
        self.resizeButton.clicked.connect(self.resize_image)

    def display_image(self, image: QPixmap):
        # Enabling initialy disabled widgets
        self.imageLabel.setPixmap(image)
        self.widthEdit.setEnabled(True)
        self.heightEdit.setEnabled(True)
        self.ratioCheckBox.setEnabled(True)
        self.saveButton.setEnabled(True)
        self.resizeButton.setEnabled(True)

        self.widthEdit.setText(str(image.width()))
        self.heightEdit.setText(str(image.height()))

    def image_from_dialog(self):
        """
        Open a dialog to choose input file, create a Pixmap
        from it and set it to imageLabel
        """
        input_path, _ = QFileDialog.getOpenFileName(
            self.centralwidget,
            "Chose File",
            directory=HOME_PATH,
            filter="Images (*.png *.jpg)",
        )
        self.inputFileEdit.setText(input_path)
        self.image = QPixmap(input_path)
        self.display_image(self.image)

    def save_image(self):
        """
        Open a dialog to save the resized image
        """
        output_path, _ = QFileDialog.getSaveFileName(
            self.centralwidget,
            "Save File",
            directory=HOME_PATH,
            filter="Images (*.png *.jpg)",
        )
        self.resized_image.save(output_path)
        self.statusBar.showMessage(f"Resized image saved to {output_path}", msecs=6000)

    def image_from_edit(self):
        """
        Check if path in inputFileEdit exists.
        If so, create a Pixmap from the given file
        and set it to image label
        """
        input_path = self.inputFileEdit.text()
        if not os.path.exists(input_path):
            self.statusBar.showMessage("This file does not exist", msecs=3000)
            return
        if os.path.isdir(input_path):
            self.statusBar.showMessage("This file is a directory", msecs=3000)
            return

        self.image = QPixmap(input_path)
        self.display_image(self.image)

    def width_watcher(self):
        """
        Update heightEdit value on widthEdit change
        """
        new_width = int(self.widthEdit.text())
        if new_width > self.image.width():
            self.widthEdit.setText(str(self.image.width()))
            self.statusBar.showMessage(
                "Width value need to be smaller than the image width"
            )
            return
        check_state = self.ratioCheckBox.checkState()
        if check_state == Qt.CheckState.Checked:
            new_height = int(new_width * self.image.height() / self.image.width())
            self.heightEdit.setText(str(new_height))

    def height_watcher(self):
        """
        Update widthEdit value on heightEdit change
        """
        new_height = int(self.heightEdit.text())
        if new_height > self.image.height():
            self.heightEdit.setText(str(self.image.height()))
            self.statusBar.showMessage(
                "Height value need to be smaller than the image height"
            )
            return
        check_state = self.ratioCheckBox.checkState()
        if check_state == Qt.CheckState.Checked:
            new_width = int(new_height * self.image.width() / self.image.height())
            self.widthEdit.setText(str(new_width))

    def resize_image(self):
        """
        Resize the image and display it on the imageLabel
        """
        width = int(self.widthEdit.text())
        height = int(self.heightEdit.text())
        self.resized_image = self.image.scaled(
            width,
            height,
            aspectRatioMode=Qt.KeepAspectRatio
            if self.ratioCheckBox.checkState() == Qt.CheckState.Checked
            else Qt.IgnoreAspectRatio,
            transformMode=Qt.SmoothTransformation,
        )
        self.saveButton.setEnabled(True)
        self.display_image(self.resized_image)


if __name__ == "__main__":
    qt = QApplication(sys.argv)
    app = ImageResizer()
    app.show()
    qt.exec_()
