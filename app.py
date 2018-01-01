import sys
import json
import qt5reactor

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, qApp
from wamplay_ui import WAMPLayUI

from autobahn.twisted.component import Component, run


class MainWindow(QMainWindow, WAMPLayUI):

    def __init__(self, component):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.component = component
        self.session = component.session_factory()

    def print_hello():
        print("hello world")

    def closeEvent(self, event):
        self.session.leave()
        self.component.stop()

    @component.on_join
    def on_join(session, details):
        print("Joined")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    qt5reactor.install()

    component = Component(transports="ws://localhost:8080/ws", realm="realm1")

    main_window = MainWindow(component)
    main_window.show()
    run([component])

    sys.exit(app.exec_())
