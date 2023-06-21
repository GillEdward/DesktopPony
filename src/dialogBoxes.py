from src.textToDialogBubble import *
from src.followPonyPos import *

class ScreenCenterDialogBox(textToDialogBubble):
	'屏幕中下方的对话框'

	def __init__(self, s, parent=None, **kwargs):
		# 调用父类初始化函数
		textToDialogBubble.__init__(self, s, './img/parchment/DialogDownPointer.png', './img/parchment/Dialog.png')

		self.initPos()

	def initPos(self):
		screen = QDesktopWidget().screenGeometry()  # QDesktopWidget为一个类，调用screenGeometry函数获得屏幕的尺寸
		x = screen.width()/2 - self.size.width()/2
		y = screen.height() - cfg.BUTTOM_OFFSET
		self.move(int(x), int(y)) # 调用move移动到指定位置

	def mousePressEvent(self, event):		# 鼠标左键按下时, 换页
		if event.button() == Qt.LeftButton:
			if self.currentPage < len(self.textPages) - 1:
				self.currentPage += 1
				self.update()
			else:
				self.currentPage = 0
				self.close()
			event.accept()

''''''

class OverheadDialogBox(textToDialogBubble_WithFadeOut, followPonyPos):
	'头顶对话框'

	def __init__(self, s, textBox_NormalPage_Path : str, textBox_LastPage_Path : str, parent=None, **kwargs):
		# 调用父类初始化函数
		textToDialogBubble_WithFadeOut.__init__(self, s, textBox_NormalPage_Path, textBox_LastPage_Path)
		followPonyPos.__init__(self)

		self.BUBBLE_OFFSET = [-85, -90]	# 对话框相对于当前姿势有效图片左上角x, y轴的偏移像素

	def paintEvent(self, event):	# 绘制窗口
		x, y = self.moveToPos()
		self.move(x, y)

		self.paintTextBox()

''''''

class Pony_OverheadDialogBox(OverheadDialogBox):
	'跟踪小马头顶对话框'

	def __init__(self, s, textBox_NormalPage_Path : str, textBox_LastPage_Path : str, parent=None, **kwargs):
		# 调用父类初始化函数
		OverheadDialogBox.__init__(self, s, textBox_NormalPage_Path, textBox_LastPage_Path)

	def getData(self):
		data = open('./temp/ponyPos.txt', 'r').readlines()
		if data != []:
			self.posX = int(data[0])
			self.posY = int(data[1])
			self.running_action = str(data[2][:-1])	# 字符串有\n结尾
			self.actualAction = int(data[3])
			self.mirrored = True if str(data[4][:-1]) == 'True' else False	# str无法直接转bool, 要用判断式
			self.picNum = int(data[5])

''''''

class TV_OverheadDialogBox(OverheadDialogBox):
	'跟踪小电视头顶对话框'

	def __init__(self, s, textBox_NormalPage_Path : str, textBox_LastPage_Path : str, parent=None, **kwargs):
		# 调用父类初始化函数
		OverheadDialogBox.__init__(self, s, textBox_NormalPage_Path, textBox_LastPage_Path)

		self.BUBBLE_OFFSET = [-80, -80]	# 对话框相对于当前姿势有效图片左上角x, y轴的偏移像素

	def moveToPos(self):
		x = self.BUBBLE_OFFSET[0]
		y = self.BUBBLE_OFFSET[1]

		x += self.posX
		y += self.posY

		return x, y

	def getData(self, posX, posY):
		self.posX = posX	# 主窗口坐标
		self.posY = posY	# 主窗口坐标