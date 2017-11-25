import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, qApp, QAction, QPushButton
from autobahn.twisted.wamp import ApplicationRunner, ApplicationSession
from autobahn import wamp
from twisted.internet.defer import inlineCallbacks, returnValue

import qt5reactor


class MainWindow(QMainWindow, ApplicationSession):

    def __init__(self, config=None):
        QMainWindow.__init__(self)
        ApplicationSession.__init__(self, config)

        test_button = QPushButton("Execute RPC", self)
        test_button.move(50, 50)
        test_button.clicked.connect(self.on_test_button_clicked)

        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle("Simple Menu")
        self.show()

    @inlineCallbacks
    def whatever_test(self):
        response = yield self.call(u"wamp.registration.list")
        returnValue(response)

    def on_test_button_clicked(self):
        d = self.whatever_test()
        d.addCallback(lambda x: print(x))

    def closeEvent(self, event):
        self.leave()
        event.accept()

    def onLeave(self, details):
        from twisted.internet import reactor
        if reactor.threadpool is not None:
            reactor.threadpool.stop()
        qApp.quit()

    @wamp.register(u"com.rlang.test_function")
    def test_function(data):
        print(data)


def make(config):
    session = MainWindow(config)
    session.show()
    return session


def main():

    app = QtWidgets.QApplication(sys.argv)
    qt5reactor.install()

    runner = ApplicationRunner(url=u"ws://192.168.178.52:8080",
                               realm=u"realm1")
    runner.run(make)


if __name__ == "__main__":
    main()
