import sys
import json
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, qApp
from autobahn.twisted.wamp import ApplicationRunner, ApplicationSession
from twisted.internet.defer import Deferred
from wamplay_ui import WAMPLayUI

import qt5reactor


class MainWindow(QMainWindow, ApplicationSession, WAMPLayUI):

    def __init__(self, config=None):
        QMainWindow.__init__(self)
        ApplicationSession.__init__(self, config)

        self.setupUi(self)
        self.current_topic = ""
        self.push_button_call.clicked.connect(self.on_call_button_pressed)

    def response_to_string(resp):
        return json.dumps(resp)

    def on_call_button_pressed(self, event):
        self.current_topic = self.line_edit_topic.text()

        def errback_handler(fail=None, msg=None):
            self.text_edit_response.setPlainText(fail.getErrorMessage())

        d = Deferred()
        try:
            d = self.call(self.current_topic,
                          json.loads(self.plainTextEdit.toPlainText()))
        except Exception as e:
            print(e.msg)

        d.addCallback(MainWindow.response_to_string)
        d.addCallback(self.text_edit_response.setPlainText)
        d.addErrback(errback_handler)

    def closeEvent(self, event):
        self.leave()
        event.accept()

    def onLeave(self, details):
        from twisted.internet import reactor
        if reactor.threadpool is not None:
            reactor.threadpool.stop()
        qApp.quit()


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
