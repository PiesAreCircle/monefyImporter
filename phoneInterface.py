# This Python file uses the following encoding: utf-8
import time
import cv2
import numpy
import re

from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtQuick

#Phone Stuff
from ppadb.client import Client
from ppadb import keycode

class phoneInterface():
    MONEFY_PACKAGE_NAME = "com.monefy.app.lite"
    MONEFY_ACTIVITY_NAME = "com.monefy.activities.main.MainActivity_"
    NUMPAD_KEYS = ["div" , "equal", "0", ".", "mult", "9", "8", "7", "min", "6", "5", "4", "plus", "3", "2", "1"]
    SUBLIST = ['PURCHASE AUTHORIZED ON.+\/[0-9][0-9] ',
               'S[0-9].+CARD.+[0-9]',
               'REF NUMBER.+']

    #Pre-Defined Colors
    DEFAULT_CATEGORY = (142, 251, 117)
    INCOME_BUTTON = (157, 208, 137)
    EXPENSE_BUTTON = (135, 138, 231)

    def __init__(self):
        adb = Client(host='127.0.0.1',port=5037)
        devices = adb.devices()

        if len(devices) == 0:
            print("No Devices Attached")
            quit()

        self.phone = devices[0]
        self.size = self.phone.wm_size()

        if self.phone.is_installed(self.MONEFY_PACKAGE_NAME) :
            self.phone.shell(f"am start --activity-single-top {self.MONEFY_PACKAGE_NAME}/{self.MONEFY_ACTIVITY_NAME}")
        else :
            print("Monefy is not installed")
            quit()

        time.sleep(0.5)

        # Locate Expense and Income Buttons
        self.expenses = self.findCenter(self.EXPENSE_BUTTON)
        self.income = self.findCenter(self.INCOME_BUTTON)

        self.phone.input_tap(self.expenses[0],self.expenses[1])
        time.sleep(0.25)

        #Find and Define Keypad
        screen = self.phone.screencap()
        screen = cv2.imdecode(numpy.frombuffer(screen, numpy.uint8), cv2.IMREAD_GRAYSCALE)
        edges = cv2.inRange(screen, 190, 200)
        contours = cv2.findContours(edges,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)[0]
        keypad = []
        for i in contours:
            epsilon = 0.05*cv2.arcLength(i,True)
            approx = cv2.approxPolyDP(i,epsilon,True)
            if cv2.contourArea(approx) > 1:
                keypad.append(numpy.mean(approx, axis=0, dtype=int)[0])

        self.enter = keypad[0]
        self.numkeys = dict(zip(self.NUMPAD_KEYS, keypad[1::]))

        self.phone.input_keyevent(keycode.KEYCODE_BACK)

    def findCenter(self, color) :
        screen = self.phone.screencap()
        screen = cv2.imdecode(numpy.frombuffer(screen, numpy.uint8), cv2.IMREAD_COLOR)

        colorFind = cv2.inRange(screen, color, color)
        E = cv2.moments(colorFind)
        if E["m00"] != 0:
            coords = [int(E["m10"] / E["m00"]), int(E["m01"] / E["m00"])]
        else:
            coords = [0, 0]

        return coords

    def clickIcon(self, fileName) :
        screen = self.phone.screencap()
        screen = cv2.imdecode(numpy.frombuffer(screen, numpy.uint8), cv2.IMREAD_COLOR)
        Icon = cv2.imread(fileName)
        result = cv2.matchTemplate(Icon, screen, cv2.TM_SQDIFF_NORMED)
        _,_,mnLoc,_ = cv2.minMaxLoc(result)
        self.phone.input_tap(mnLoc[0],mnLoc[1])

    def enterAmount(self, string) :
        for element in range(0, len(string)) :
            position = self.numkeys.get(string[element], False)
            if not numpy.all(position) :
                continue
            self.phone.input_tap(position[0],position[1])

    def closeKeyboard(self):
        while True :
            if ('mInputShown=true' in self.phone.shell('dumpsys input_method')):
                self.phone.input_keyevent(keycode.KEYCODE_BACK)
            else :
                break
            time.sleep(0.05)

    def addInfo(self, line) :
        if float(line[1]) >0 :
            self.phone.input_tap(self.income[0],self.income[1])
        else :
            self.phone.input_tap(self.expenses[0],self.expenses[1])

        #Add Date
        time.sleep(0.25) # wait for app to load
        self.phone.input_tap(self.size.width * 1/2, self.size.height * 1/6) #Date Box
        time.sleep(0.25)

        self.clickIcon("editIcon.png")

        for i in range(10) :
            self.phone.input_keyevent(keycode.KEYCODE_DEL)
        self.phone.input_text(line[0])
        self.closeKeyboard()
        time.sleep(0.25)
        self.clickIcon("okIcon.png")

        time.sleep(0.25)
        self.enterAmount(line[1])
        time.sleep(0.25)

        #Add Note
        self.clickIcon("noteIcon.png")

        for words in self.SUBLIST:
            line[4] = re.sub(words, "", line[4])
        self.phone.input_text(line[4])
        time.sleep(0.25)
        self.closeKeyboard()

        time.sleep(0.25)
        self.phone.input_tap(self.enter[0],self.enter[1])
        time.sleep(0.5)

        #Add to Category
        clickLoc = self.findCenter(self.DEFAULT_CATEGORY)
        self.phone.input_tap(clickLoc[0],clickLoc[1])
