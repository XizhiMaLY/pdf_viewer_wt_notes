import sys
import os
from PyQt5 import QtCore, QtWidgets, QtWebEngineWidgets


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Show directory selection dialog
        dir_path = QtWidgets.QFileDialog.getExistingDirectory(
            None, "Select a Directory", QtCore.QDir.homePath()
        )
        if not dir_path:  # Exit if no directory is selected
            sys.exit()

        # Central widget setup
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)

        # Layout for the main window
        self.layout = QtWidgets.QHBoxLayout(self.central_widget)

        # Directory Tree (Left Side)
        self.dir_model = QtWidgets.QFileSystemModel()
        self.dir_model.setRootPath(dir_path)
        self.dir_model.setNameFilters(["*.pdf"])  # Only show PDFs
        self.dir_model.setNameFilterDisables(False)

        self.dir_view = QtWidgets.QTreeView()
        self.dir_view.setModel(self.dir_model)
        self.dir_view.setRootIndex(self.dir_model.index(dir_path))
        self.dir_view.setColumnWidth(0, 250)
        self.dir_view.clicked.connect(self.load_pdf)

        # PDF Viewer (Center)
        self.pdf_viewer = QtWebEngineWidgets.QWebEngineView()
        self.pdf_viewer.settings().setAttribute(
            QtWebEngineWidgets.QWebEngineSettings.PluginsEnabled, True
        )
        self.pdf_viewer.settings().setAttribute(
            QtWebEngineWidgets.QWebEngineSettings.PdfViewerEnabled, True
        )
        self.pdf_viewer.setZoomFactor(2.0)  # Higher zoom level for better clarity
        

        # Notes Section (Right Side)
        self.notes_editor = QtWidgets.QTextEdit()
        self.notes_editor.setPlaceholderText("Write your notes here...")
        self.notes_editor.textChanged.connect(self.auto_save_notes)
        self.current_pdf = None  # Keep track of the currently loaded PDF

        # Notes Layout (Right)
        self.notes_layout = QtWidgets.QVBoxLayout()
        self.notes_layout.addWidget(self.notes_editor)

        self.notes_widget = QtWidgets.QWidget()
        self.notes_widget.setLayout(self.notes_layout)

        # Add widgets to the main layout
        self.layout.addWidget(self.dir_view, 1)      # Directory tree (1x size)
        self.layout.addWidget(self.pdf_viewer, 4)   # PDF viewer (4x size)
        self.layout.addWidget(self.notes_widget, 2) # Notes editor (2x size)

        # Window settings
        self.setGeometry(300, 100, 1200, 800)
        self.setWindowTitle("PDF Viewer with Auto-Saving Notes")

    def load_pdf(self, index):
        """Load PDF and corresponding notes when a file is clicked."""
        file_path = self.dir_model.filePath(index)

        if file_path.endswith(".pdf"):
            # Load the PDF in the viewer
            self.current_pdf = file_path
            self.pdf_viewer.load(QtCore.QUrl.fromLocalFile(file_path))

            # Load the notes associated with the PDF
            notes_path = self.get_notes_path(file_path)
            if os.path.exists(notes_path):
                with open(notes_path, "r", encoding="utf-8") as f:
                    self.notes_editor.blockSignals(True)  # Prevent triggering auto-save while loading notes
                    self.notes_editor.setPlainText(f.read())
                    self.notes_editor.blockSignals(False)
            else:
                self.notes_editor.blockSignals(True)
                self.notes_editor.clear()
                self.notes_editor.blockSignals(False)

    def auto_save_notes(self):
        """Automatically save notes when the text is modified."""
        if self.current_pdf:
            notes_path = self.get_notes_path(self.current_pdf)
            with open(notes_path, "w", encoding="utf-8") as f:
                f.write(self.notes_editor.toPlainText())

    def get_notes_path(self, pdf_path):
        """Get the path for the notes file corresponding to the PDF."""
        return pdf_path + ".txt"


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("PDF Viewer with Notes")

    main_window = MainWindow()

    # macOS-specific application menu
    print(sys.platform)
    if sys.platform == "darwin":
        menu_bar = QtWidgets.QMenuBar()
        file_menu = menu_bar.addMenu("File")
        quit_action = QtWidgets.QAction("Quit", menu_bar)
        quit_action.triggered.connect(app.quit)
        file_menu.addAction(quit_action)
        main_window.setMenuBar(menu_bar)  # Correctly set the menu bar on QMainWindow

    main_window.show()
    sys.exit(app.exec_())

