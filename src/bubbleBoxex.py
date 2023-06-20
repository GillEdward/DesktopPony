from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from src.followPonyPos import *

class BubbleBox(QWidget, followPonyPos):
	showParchment = pyqtSignal()

	def __init__(self, emojiPic, parent=None, **kwargs):
		super(BubbleBox, self).__init__(parent)
		followPonyPos.__init__(self)
		# 初始化
		self.setWindowFlags(Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint|Qt.SubWindow)
		self.setAutoFillBackground(False)
		self.setAttribute(Qt.WA_TranslucentBackground, True)
		self.update()

		self.BUBBLE_OFFSET = [20, -60]	# 对话框相对于当前姿势有效图片左上角x, y轴的偏移像素
		self.IMG_WIDTH = 80*4
		self.emojiPic = emojiPic

		self.textPix = {}
		self.loadPos()

	def paintTextBox(self):	# 绘制文本框
		paint = QPainter(self)
		self.resize(self.emojiPic.size())	# 获取图片大小
		self.setMask(self.emojiPic.mask())   # 设置蒙版
		paint.drawPixmap(0, 0, self.emojiPic.width(), self.emojiPic.height(), self.emojiPic)

	def paintEvent(self, event):	# 绘制窗口
		x, y = self.moveToPos()
		self.move(x, y)

		self.paintTextBox()

	'''事件处理'''
	def mousePressEvent(self, event):		# 鼠标左键按下时, 打开对话框
		if event.button() == Qt.LeftButton:
			self.showParchment.emit()
			event.accept()
	''''''