import sys
import json
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, qApp, QInputDialog
from autobahn.twisted.wamp import ApplicationRunner, ApplicationSession
from twisted.internet.defer import Deferred, inlineCallbacks
from wamplay_ui import WAMPLayUI
import argparse
import qt5reactor


class MainWindow(QMainWindow, ApplicationSession, WAMPLayUI):

    def __init__(self, config=None):
        QMainWindow.__init__(self)
        ApplicationSession.__init__(self, config)

        self.setupUi(self)
        self.current_topic = ""
        self.button_subscribe.clicked.connect(self.on_subscribe_button_pressed)
        self.button_call.clicked.connect(self.on_call_button_pressed)
        self.button_publish.clicked.connect(self.on_publish_button_pressed)
        self.last_subscription = None

    def response_to_string(resp):
        return json.dumps(resp)

    def on_call_button_pressed(self, event):
        self.current_topic = self.line_edit_call_topic.text()
        data = ""

        if not self.text_edit_call_data.toPlainText:
            data = json.loads(self.text_edit_call_data.toPlainText())

        def errback_handler(fail=None, msg=None):
            self.text_edit_response.setPlainText(fail.getErrorMessage())

        d = Deferred()
        try:
            d = self.call(self.current_topic,
                          data)
        except Exception as e:
            print(e.msg)

        d.addCallback(MainWindow.response_to_string)
        d.addCallback(self.text_edit_call_response.setPlainText)
        d.addErrback(errback_handler)

    @inlineCallbacks
    def on_subscribe_button_pressed(self, event):
        topic = self.line_edit_subscription_topic.text()

        if self.last_subscription is not None:
            self.last_subscription.unsubscribe()

        self.last_subscription = yield \
            self.subscribe(self.on_subscribtion_data_received, topic)

    def on_subscribtion_data_received(self, data):
        self.text_edit_subscription_response.appendPlainText(data)

    @inlineCallbacks
    def on_publish_button_pressed(self, event):
        topic = self.line_edit_publish_topic.text()
        data = self.text_edit_publish_data.toPlainText()

        yield self.publish(topic, data)

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
