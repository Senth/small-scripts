#!/usr/bin/python3

import sys
import time
from threading import Thread
from typing import Optional
from subprocess import run
from PyQt5 import QtWidgets
from apscheduler.schedulers.qt import QtScheduler

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QMainWindow, QApplication

testing = False

minute = "5,35"
clicks_to_hide = 20
break_time = 3.5 * 60
if testing:
    clicks_to_hide = 5
    break_time = 5
    minute = "*"

skip_breaks = ["Slack | Slack call", "(Meeting) | Microsoft Teams"]


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint
            | QtCore.Qt.FramelessWindowHint
            | QtCore.Qt.X11BypassWindowManagerHint
        )
        width = 7680
        if testing:
            width = 2000
        self.setGeometry(0, 0, width, 1440)
        self.setWindowOpacity(0.75)
        self.presses = 0
        self.delay_thread: Optional[Thread] = None
        self.create_gui()

    def create_gui(self) -> None:
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        vbox = QtWidgets.QVBoxLayout()
        vbox.setAlignment(QtCore.Qt.AlignCenter)
        central_widget.setLayout(vbox)
        self.time_passed_label = QtWidgets.QLabel()
        self.time_passed_label.setFixedWidth(500)
        self.time_passed_label.setText("XX:XX")
        self.time_passed_label.setAlignment(QtCore.Qt.AlignCenter)
        vbox.addWidget(self.time_passed_label)

    def show_and_hide(self) -> None:
        if should_activate_break():
            super().show()
            self.delay_thread = Thread(target=self.delayed_hide)
            self.delay_thread.start()

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        self.presses += 1
        if self.presses >= clicks_to_hide:
            self.hide()

    def delayed_hide(self) -> None:
        done_at = time.time() + break_time
        while time.time() < done_at:
            seconds_left = int(done_at - time.time())
            minutes_left = int(seconds_left / 60)
            seconds_left = seconds_left - minutes_left * 60
            time_left = (
                f"{minutes_left}".rjust(2, "0") + ":" + f"{seconds_left}".rjust(2, "0")
            )
            self.time_passed_label.setText(time_left)
            time.sleep(0.5)

        self.hide()
        self.delay_thread = None


def should_activate_break() -> bool:
    return not in_a_meeting()


def in_a_meeting() -> bool:
    get_windows = run(["wmctrl", "-l"], capture_output=True, encoding="utf-8")
    windows = get_windows.stdout.splitlines()

    for window in windows:
        for skip in skip_breaks:
            if skip in window:
                return True
    return False


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet("QLabel{font-size: 72pt;}")
    window = MainWindow()

    scheduler = QtScheduler()
    scheduler.add_job(window.show_and_hide, trigger="cron", minute=minute)
    scheduler.start()

    app.exec_()
