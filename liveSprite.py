from PyQt5.QtWidgets import *

import os
import sys
 
import cfg
from src.dialogBoxes import *

'''小电视'''
class liveSprite(QWidget):
	# 定义信号
	bubbleDialogUpdate = pyqtSignal(int, int)

	def __init__(self, parent=None, **kwargs):
		super(liveSprite, self).__init__(parent)

		# 初始化
		self.setWindowFlags(Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint|Qt.SubWindow)
		self.setAutoFillBackground(False)
		self.setAttribute(Qt.WA_TranslucentBackground, True)
		self.update()

		self.is_follow_mouse = False	# 是否跟随鼠标
		self.mouse_drag_pos = self.pos()	# 防止宠物拖拽时移动僵硬
		self.initPos()   # 定位窗口位置

		self.posX = self.x()
		self.posY = self.y()

		# 右键扇形菜单

		# 加载资源
		self.pix = None
		self.loadImage()

		# 子窗口
		self.bubbleDialog = TV_OverheadDialogBox('', './img/parchment/DialogBubble.png', './img/parchment/DialogBubble.png')

		# 子窗口判定
		self.showBubbleDialog = False
		self.bubbleDialogText = ''

		# 信号槽

		# 状态机循环
		self.animationTimer = QTimer()
		self.animationTimer.start(int(1000/cfg.FPS)) # 动画更新速度同步屏幕帧率
		self.animationTimer.timeout.connect(self.update)
		self.animationTimer.timeout.connect(self.openBubbleDialogText)	# 读取弹幕文本信息
		self.animationTimer.timeout.connect(self.bubbleDialogUpdate_)

		self.show()

	def initPos(self):
		screen = QDesktopWidget().screenGeometry()  # QDesktopWidget为一个类，调用screenGeometry函数获得屏幕的尺寸
		size = self.geometry()
		x = screen.width() - size.width()
		y = screen.height() - size.height()
		self.move(int(x), int(y)) # 调用move移动到指定位置

	def paintEvent(self, event):	# 绘制窗口
		self.bubbleDialogUpdate.emit(self.posX, self.posY)

		paint = QPainter(self)
		self.resize(self.pix.size())	# 获取图片大小
		self.setMask(self.pix.mask())   # 设置蒙版
		paint.drawPixmap(0, 0, self.pix.width(), self.pix.height(), self.pix)

	def loadImage(self):
		self.pix = QPixmap(os.path.join('./img/sprite/computer.png'))

	'''事件处理'''
	def mousePressEvent(self, event):		# 鼠标左键按下时, 宠物将和鼠标位置绑定
		if event.button() == Qt.LeftButton:
			self.is_follow_mouse = True
			self.mouse_drag_pos = event.globalPos() - self.pos()
			event.accept()
			self.setCursor(QCursor(Qt.OpenHandCursor))

	def mouseMoveEvent(self, event):	# 鼠标移动, 则宠物也移动
		if Qt.LeftButton and self.is_follow_mouse:
			self.posX = self.x()
			self.posY = self.y()
			self.move(event.globalPos() - self.mouse_drag_pos)
			event.accept()

	def mouseReleaseEvent(self, event):	# 鼠标释放时, 取消绑定
		self.is_follow_mouse = False
		self.setCursor(QCursor(Qt.ArrowCursor))
	''''''

	'''其他函数'''
	def quit(self):
		self.close()
		sys.exit()

	def readText(self, path):	# 读取txt文件, 返回一个str数组
		temp = []

		f = open(path, encoding = 'utf-8')
		for line in f:
			temp.append(line)

		f.close()
		return temp

	def openBubbleDialogText(self):	# 打开对应文件夹
		text = self.readText(os.path.join('./temp/liveDM.txt'))
		if text != self.bubbleDialogText and text != []:
			self.bubbleDialogText = text
			self.bubbleDialog = TV_OverheadDialogBox(text, './img/parchment/DialogBubble.png', './img/parchment/DialogBubble.png')
			self.showBubbleDialog = True
			self.bubbleDialogUpdate.connect(self.bubbleDialog.getData)	# 每次创建新对象都要重新连接信号槽

	def bubbleDialogUpdate_(self):
		self.bubbleDialog.update()
		if self.showBubbleDialog:	# 如果无新内容, 则不更新头顶气泡
			self.bubbleDialog.show()
			self.showBubbleDialog = False
	''''''

'''run'''
if __name__ == '__main__':
	app = QApplication(sys.argv)
	pet = liveSprite()
	sys.exit(app.exec_())