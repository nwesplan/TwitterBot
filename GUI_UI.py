# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'GUI_UI.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1063, 818)
        self.comboBox = QtWidgets.QComboBox(Dialog)
        self.comboBox.setGeometry(QtCore.QRect(20, 40, 201, 22))
        self.comboBox.setObjectName("comboBox")
        self.getTableButton = QtWidgets.QPushButton(Dialog)
        self.getTableButton.setGeometry(QtCore.QRect(70, 160, 91, 23))
        self.getTableButton.setObjectName("getTableButton")
        self.TableLabel = QtWidgets.QLabel(Dialog)
        self.TableLabel.setGeometry(QtCore.QRect(20, 200, 391, 31))
        self.TableLabel.setObjectName("TableLabel")
        self.searchTextInput = QtWidgets.QLineEdit(Dialog)
        self.searchTextInput.setGeometry(QtCore.QRect(130, 270, 131, 31))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.searchTextInput.setFont(font)
        self.searchTextInput.setObjectName("searchTextInput")
        self.searchTextLabel = QtWidgets.QLabel(Dialog)
        self.searchTextLabel.setGeometry(QtCore.QRect(20, 270, 151, 31))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.searchTextLabel.setFont(font)
        self.searchTextLabel.setObjectName("searchTextLabel")
        self.searchTextButton = QtWidgets.QPushButton(Dialog)
        self.searchTextButton.setGeometry(QtCore.QRect(280, 270, 81, 31))
        self.searchTextButton.setObjectName("searchTextButton")
        self.listWidgetColumns = QtWidgets.QListWidget(Dialog)
        self.listWidgetColumns.setGeometry(QtCore.QRect(760, 280, 256, 192))
        self.listWidgetColumns.setObjectName("listWidgetColumns")
        self.calendarWidget = QtWidgets.QCalendarWidget(Dialog)
        self.calendarWidget.setGeometry(QtCore.QRect(710, 20, 312, 183))
        self.calendarWidget.setObjectName("calendarWidget")
        self.datelabel = QtWidgets.QLabel(Dialog)
        self.datelabel.setGeometry(QtCore.QRect(770, 250, 171, 16))
        self.datelabel.setObjectName("datelabel")
        self.checkbox_bar = QtWidgets.QCheckBox(Dialog)
        self.checkbox_bar.setGeometry(QtCore.QRect(250, 90, 81, 21))
        self.checkbox_bar.setObjectName("checkbox_bar")
        self.checkbox_geo = QtWidgets.QCheckBox(Dialog)
        self.checkbox_geo.setGeometry(QtCore.QRect(250, 170, 70, 17))
        self.checkbox_geo.setObjectName("checkbox_geo")
        self.toplabel = QtWidgets.QLabel(Dialog)
        self.toplabel.setGeometry(QtCore.QRect(410, 210, 47, 13))
        self.toplabel.setObjectName("toplabel")
        self.horizontal_slider = QtWidgets.QSlider(Dialog)
        self.horizontal_slider.setGeometry(QtCore.QRect(410, 270, 211, 41))
        self.horizontal_slider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontal_slider.setObjectName("horizontal_slider")
        self.slider_label = QtWidgets.QLabel(Dialog)
        self.slider_label.setGeometry(QtCore.QRect(490, 200, 111, 31))
        self.slider_label.setObjectName("slider_label")
        self.stopword_label = QtWidgets.QLabel(Dialog)
        self.stopword_label.setGeometry(QtCore.QRect(20, 330, 131, 31))
        self.stopword_label.setObjectName("stopword_label")
        self.stop_words_input = QtWidgets.QLineEdit(Dialog)
        self.stop_words_input.setGeometry(QtCore.QRect(130, 330, 131, 20))
        self.stop_words_input.setObjectName("stop_words_input")
        self.add_stop_word_button = QtWidgets.QPushButton(Dialog)
        self.add_stop_word_button.setGeometry(QtCore.QRect(280, 330, 75, 23))
        self.add_stop_word_button.setObjectName("add_stop_word_button")
        self.text_hashtag_combo = QtWidgets.QComboBox(Dialog)
        self.text_hashtag_combo.setGeometry(QtCore.QRect(20, 80, 201, 22))
        self.text_hashtag_combo.setObjectName("text_hashtag_combo")
        self.device_used_combo = QtWidgets.QComboBox(Dialog)
        self.device_used_combo.setGeometry(QtCore.QRect(20, 120, 201, 22))
        self.device_used_combo.setObjectName("device_used_combo")
        self.checkBox_sentiment = QtWidgets.QCheckBox(Dialog)
        self.checkBox_sentiment.setGeometry(QtCore.QRect(250, 130, 121, 17))
        self.checkBox_sentiment.setObjectName("checkBox_sentiment")
        self.refresh_table_button = QtWidgets.QPushButton(Dialog)
        self.refresh_table_button.setGeometry(QtCore.QRect(250, 40, 111, 31))
        self.refresh_table_button.setObjectName("refresh_table_button")
        self.stopwords_label = QtWidgets.QLabel(Dialog)
        self.stopwords_label.setGeometry(QtCore.QRect(140, 380, 151, 16))
        self.stopwords_label.setObjectName("stopwords_label")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.getTableButton.setText(_translate("Dialog", "Select Options"))
        self.TableLabel.setText(_translate("Dialog", "TextLabel"))
        self.searchTextLabel.setText(_translate("Dialog", "Search text:"))
        self.searchTextButton.setText(_translate("Dialog", "Search"))
        self.datelabel.setText(_translate("Dialog", "TextLabel"))
        self.checkbox_bar.setText(_translate("Dialog", "Bar Chart"))
        self.checkbox_geo.setText(_translate("Dialog", "Geo Map"))
        self.toplabel.setText(_translate("Dialog", "Top"))
        self.slider_label.setText(_translate("Dialog", "TextLabel"))
        self.stopword_label.setText(_translate("Dialog", "Add stop word:"))
        self.add_stop_word_button.setText(_translate("Dialog", "Add"))
        self.checkBox_sentiment.setText(_translate("Dialog", "Sentiment Analysis"))
        self.refresh_table_button.setText(_translate("Dialog", "Refresh Table List"))
        self.stopwords_label.setText(_translate("Dialog", "Added stop word:"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
