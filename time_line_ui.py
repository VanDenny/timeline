# -*- coding: utf-8 -*-
# python 3.6 pyqt 5
from PyQt5 import QtCore, QtGui, QtWidgets
from Time_line.time_line import Geo_Point, clawer
import time
import sys

class Timeline_Ui(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)


        self.resize(500, 500)
        self.center()
        # self.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint)
        self.setFixedSize(self.width(), self.height())
        self.setWindowTitle("高德等时线生成工具v2018.02.13")
        self.setWindowIcon(QtGui.QIcon(r'time_line.jpg'))
        self.statusBar().showMessage('就绪')

        # 第一步，输入中心点经纬度
        self.step_Box_1 = QtWidgets.QGroupBox(self)
        self.step_Box_1.setGeometry(QtCore.QRect(20, 20, 460, 60)) # x,y,w,h
        self.step_Box_1.setTitle("Step01: 输入中心点经纬度")

        self.widget_1 = QtWidgets.QWidget(self.step_Box_1)
        self.step_1_layout = QtWidgets.QHBoxLayout(self.widget_1)

        self.label_1 = QtWidgets.QLabel(self.widget_1)
        self.label_1.setText('中心点经纬度：')
        self.step_1_layout.addWidget(self.label_1)
        self.lineEdit_1 = QtWidgets.QLineEdit(self.widget_1)
        self.lineEdit_1.setText('113.316345,23.063429')
        self.lineEdit_1.setToolTip('用逗号分隔经维度 lng,lat')
        self.step_1_layout.addWidget(self.lineEdit_1)

        self.step_Box_1.setLayout(self.step_1_layout)

        # 第二步，输入高德地图密钥
        self.step_Box_2 = QtWidgets.QGroupBox(self)
        self.step_Box_2.setGeometry(QtCore.QRect(20, 100, 460, 60)) # x,y,w,h
        self.step_Box_2.setTitle("Step02: 输入高德密钥")

        self.widget_2 = QtWidgets.QWidget(self.step_Box_2)
        self.step_2_layout = QtWidgets.QHBoxLayout(self.widget_2)

        self.label_2 = QtWidgets.QLabel(self.widget_2)
        self.label_2.setText('高德KEY：')
        self.step_2_layout.addWidget(self.label_2)
        self.lineEdit_2 = QtWidgets.QLineEdit(self.widget_2)
        self.lineEdit_2.setText('70de561d24ed370ab68d0434d834d106')
        self.step_2_layout.addWidget(self.lineEdit_2)

        self.step_Box_2.setLayout(self.step_2_layout)

        # 第三步,选择绘制模式复选框
        self.groupBox = QtWidgets.QGroupBox(self)
        self.groupBox.setGeometry(QtCore.QRect(20, 180, 460, 60))
        self.groupBox.setTitle("Step03: 绘制模式")

        self.widget = QtWidgets.QWidget(self.groupBox)
        self.groupBox_Layout = QtWidgets.QHBoxLayout(self.widget)

        self.checkBox = QtWidgets.QCheckBox(self.widget)
        self.checkBox.toggle()
        self.checkBox.setText("步行")
        self.checkBox.setToolTip('计算步行耗时')
        self.groupBox_Layout.addWidget(self.checkBox)

        self.checkBox_2 = QtWidgets.QCheckBox(self.widget)
        self.checkBox_2.toggle()
        self.checkBox_2.setText("公交")
        self.checkBox_2.setToolTip('计算公交耗时')
        self.groupBox_Layout.addWidget(self.checkBox_2)

        self.checkBox_3 = QtWidgets.QCheckBox(self.widget)
        self.checkBox_3.toggle()
        self.checkBox_3.setText("驾车")
        self.checkBox_3.setToolTip('计算驾车耗时')
        self.groupBox_Layout.addWidget(self.checkBox_3)

        self.groupBox.setLayout(self.groupBox_Layout)

        # 第四步，储存文件夹位置
        self.step_Box_4 = QtWidgets.QGroupBox(self)
        self.step_Box_4.setGeometry(QtCore.QRect(20, 260, 460, 60)) # x,y,w,h
        self.step_Box_4.setTitle("Step04: 储存文件夹位置")

        self.widget_4 = QtWidgets.QWidget(self.step_Box_4)
        self.step_4_layout = QtWidgets.QHBoxLayout(self.widget_4)

        self.label_3 = QtWidgets.QLabel(self.widget_4)
        self.label_3.setText('储存文件夹：')
        self.step_4_layout.addWidget(self.label_3)
        self.lineEdit_3 = QtWidgets.QLineEdit(self.widget_4)
        self.lineEdit_3.setText('D:\program_lib\Time_line')
        self.step_4_layout.addWidget(self.lineEdit_3)
        self.toolButton = QtWidgets.QToolButton(self.widget_4)
        self.toolButton.setText('...')
        self.step_4_layout.addWidget(self.toolButton)

        self.step_Box_4.setLayout(self.step_4_layout)

        # 第五步，启动
        self.step_Box_5 = QtWidgets.QGroupBox(self)
        self.step_Box_5.setGeometry(QtCore.QRect(20, 340, 460, 120)) # x,y,w,h
        self.step_Box_5.setTitle("Step05: 启动程序")

        self.widget_5 = QtWidgets.QWidget(self.step_Box_5)
        self.step_5_layout = QtWidgets.QVBoxLayout(self.widget_5)

        self.process_statue = QtWidgets.QLabel(self.widget_5)
        self.step_5_layout.addWidget(self.process_statue)
        self.progressBar = QtWidgets.QProgressBar(self.widget_5)
        self.progressBar.setProperty("value", 0)
        self.step_5_layout.addWidget(self.progressBar)
        self.pushButton = QtWidgets.QPushButton(self.widget_5)
        self.pushButton.setText('生成等时线')
        self.step_5_layout.addWidget(self.pushButton)
        self.step_Box_5.setLayout(self.step_5_layout)

        # 按钮链接
        self.toolButton.clicked.connect(self.file_path)
        self.pushButton.clicked.connect(self.main_process)
        self.show()

    def file_path(self):
        download_path = QtWidgets.QFileDialog.getExistingDirectory(self, "储存文件夹", ".")
        self.lineEdit_3.setText(download_path)


    def center(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def closeEvent(self, event):
        reply = QtWidgets.QMessageBox.question(self, '确认退出', "确定要退出吗？",
                                               QtWidgets.QMessageBox.Yes,
                                               QtWidgets.QMessageBox.No
                                               )
        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def main_process(self):
        pass


class Ui_Input(Timeline_Ui):
    def __init__(self, parent=None):
        super(Ui_Input, self).__init__(parent)

    def center_point_input(self):
        self.str_point = self.lineEdit_1.text()
        if ',' in self.str_point:
            alist = self.str_point.split(',')
            alist = [round(float(i),6)for i in alist]
            return Geo_Point(*tuple(alist))
        else:
            self.statusBar().showMessage('请输入正确的经纬度')

    def gd_key_input(self):
        self.str_key = self.lineEdit_2.text()
        if self.str_key:
            return self.str_key.split(',')
        else:
            self.statusBar().showMessage('请输入高德API密钥')

    def mode_list_input(self):
        self.walk_state = self.checkBox.checkState()
        self.bus_state = self.checkBox_2.checkState()
        self.car_state = self.checkBox_3.checkState()
        mode_list = []
        if self.walk_state == 2:
            mode_list.append('步行')
        if self.bus_state == 2:
            mode_list.append('公交')
        if self.car_state == 2:
            mode_list.append('驾车')
        if mode_list:
            return mode_list
        else:
            self.statusBar().showMessage('请选择一种绘制模式')

    def path_input(self):
        self.path = self.lineEdit_3.text()
        if self.path:
            return self.path
        else:
            self.statusBar().showMessage('请输入储存文件夹')



    def main_process(self):
        print(self.center_point_input())
        print(self.gd_key_input())
        print(self.mode_list_input())
        print(self.path_input())
        if self.center_point_input() and self.gd_key_input() and self.mode_list_input() and self.path_input():
            self.pushButton.setDisabled(True)
            for mode in self.mode_list_input():
                from Time_line.time_line import ClawerThread
                self.statusBar().showMessage('正在生成%s等时线'%(mode))
                input_tuple = (self.center_point_input(),self.gd_key_input(),mode,self.path_input())
                # clawer(*input_tuple)
                self.clawer_thread = ClawerThread(*input_tuple)
                self.clawer_thread.progressSignal.connect(self.set_process_staue)
                self.clawer_thread.statusSignal.connect(self.set_status_bar)
                self.clawer_thread.finishSignal.connect(self.work_end)
                self.clawer_thread.start()
        else:
            pass

    def set_process_staue(self,p_num, p_str):
        # print('get!')
        self.progressBar.setProperty("value", p_num)
        self.process_statue.setText(p_str)

    def set_status_bar(self, p_str):
        self.statusBar().showMessage(p_str)

    def work_end(self):
        self.pushButton.setDisabled(False)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ui = Ui_Input()
    sys.exit(app.exec_())
