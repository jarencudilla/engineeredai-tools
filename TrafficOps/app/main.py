"""
app/main.py

Entry point. Run this to launch TrafficOps:

    python -m app.main

This file does one thing: start the Qt application and show the
main window. No business logic belongs here.
"""

import sys
from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
