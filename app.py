import sys
import json
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, qApp, QInputDialog
from autobahn.twisted.wamp import ApplicationRunner, ApplicationSession
from twisted.internet.defer import Deferred
from wamplay_ui import WAMPLayUI
from connection_dialog import ConnectionDialog
import argparse
import qt5reactor


class MainWindow(QMainWindow, ApplicationSession, WAMPLayUI):

    def __init__(self, config=None):
        QMainWindow.__init__(self)
        ApplicationSession.__init__(self, config)

        self.setupUi(self)
        self.current_topic = ""
        self.push_button_call.clicked.connect(self.on_call_button_pressed)
        self.actionConnect.triggered.connect(self.show_connection_dialog)

    def show_connection_dialog(self):
        print("Couldn't find a solution to change the connection yet")

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
    parser = argparse.ArgumentParser(description="GUI Tool to test wamp topics")
    parser.add_argument("url", metavar="url",
                        type=str, nargs='?', default="ws://127.0.0.1:8080/ws")
    parser.add_argument("realm", metavar="realm",
                        type=str, nargs='?', default="realm1")
    parser.add_argument("--user", metavar="user", type=str)
    parser.add_argument("--password", metavar="user", type=str)
    args = parser.parse_args()
    print(args.url)

    app = QtWidgets.QApplication(sys.argv)
    qt5reactor.install()

    runner = ApplicationRunner(url=args.url,
                               realm=args.realm)
    runner.run(make)


if __name__ == "__main__":
    main()
