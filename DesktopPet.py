import os
import sys
import random
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets, QtGui
import cv2
import numpy
from PIL import Image, ImageDraw, ImageFont, ImageQt
import win32gui	# 仅限Win
import cfg
import math

# pyinstaller -F -w -i favIcon256.ico DesktopPet.py --exclude-module ./cfg.py

'''桌面宠物'''
class DesktopPet(QWidget):
	# 定义信号
	bubbleUpdate = pyqtSignal(QPixmap, int, int, str, int, bool, int)
	menuBubbleUpdate = pyqtSignal(int, int, str, int, int)

	def __init__(self, parent=None, **kwargs):
		super(DesktopPet, self).__init__(parent)

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
		self.currentAction = 0	# 目标姿态（1飞行，0站姿，-1坐姿，-2卧姿）
		self.actualAction = 0 # 实际姿态
		self.running_action = ''
		self.is_running_action = False
		self.direction = 0b0000	# 二进制键值按WASD排列, 如0b1000代表按下W, 0b1100代表按下W和A
		self.mirrored = False

		# 右键扇形菜单
		self.menuBubble = []
		self.menu = {}
		self.menu.update({'备忘录文件夹' : menuBubble(menuLayout('备忘录文件夹', 150, 90), QPixmap('./img/buttom/备忘录文件夹.png'), 'functionButton')})
		self.menu['备忘录文件夹'].functionActive.connect(self.openMemoFolder)
		self.menu.update({'查看当前句柄' : menuBubble(menuLayout('查看当前句柄', 150, 120), QPixmap('./img/buttom/查看当前句柄.png'), 'functionButton')})
		self.menu['查看当前句柄'].functionActive.connect(self.showCurrentHandles)
		self.menu.update({'抽取随机任务' : menuBubble(menuLayout('抽取随机任务', 150, 150), QPixmap('./img/buttom/抽取随机任务.png'), 'functionButton')})
		self.menu['抽取随机任务'].functionActive.connect(self.randomTODOList)
		self.menu.update({'设置' : menuBubble(menuLayout('设置', 150, 180), QPixmap('./img/buttom/设置.png'), 'menuLayer')})
		self.menu['设置'].info.son.update({'运动类' : menuBubble(menuLayout('运动类', 250, 150), QPixmap('./img/buttom/运动类.png'), 'menuLayer')})
		self.menu['设置'].info.son['运动类'].info.son.update({'步长' : menuBubble(menuLayout('步长', 350, 150), QPixmap('./img/buttom/步长.png'), 'functionButton')})
		self.menu['设置'].info.son.update({'文本类' : menuBubble(menuLayout('文本类', 250, 180), QPixmap('./img/buttom/文本类.png'), 'menuLayer')})
		self.menu['设置'].info.son['文本类'].info.son.update({'字体大小' : menuBubble(menuLayout('字体大小', 350, 120), QPixmap('./img/buttom/字体大小.png'), 'functionButton')})
		self.menu['设置'].info.son['文本类'].info.son.update({'字体颜色' : menuBubble(menuLayout('字体颜色', 350, 150), QPixmap('./img/buttom/字体颜色.png'), 'functionButton')})
		self.menu['设置'].info.son['文本类'].info.son.update({'行间距' : menuBubble(menuLayout('行间距', 350, 180), QPixmap('./img/buttom/行间距.png'), 'functionButton')})
		self.menu['设置'].info.son['文本类'].info.son.update({'初始偏移量' : menuBubble(menuLayout('初始偏移量', 350, 210), QPixmap('./img/buttom/初始偏移量.png'), 'functionButton')})
		self.menu['设置'].info.son['文本类'].info.son.update({'相当垂直高度' : menuBubble(menuLayout('相当垂直高度', 350, 240), QPixmap('./img/buttom/相当垂直高度.png'), 'functionButton')})
		self.menu['设置'].info.son.update({'绘制类' : menuBubble(menuLayout('绘制类', 250, 210), QPixmap('./img/buttom/绘制类.png'), 'menuLayer')})
		self.menu['设置'].info.son['绘制类'].info.son.update({'FPS' : menuBubble(menuLayout('FPS', 350, 210), QPixmap('./img/buttom/FPS.png'), 'functionButton')})
		self.menu.update({'保存并退出' : menuBubble(menuLayout('保存并退出', 150, 210), QPixmap('./img/buttom/保存并退出.png'), 'functionButton')})
		self.menu.update({'不保存并退出' : menuBubble(menuLayout('保存并退出', 150, 240), QPixmap('./img/buttom/不保存并退出.png'), 'functionButton')})
		self.menu.update({'关闭' : menuBubble(menuLayout('关闭', 150, 270), QPixmap('./img/buttom/关闭.png'), 'functionButton')})
		self.menu['关闭'].functionActive.connect(self.quit)

		self.traverseMenuToConnect_UpdateSingal(self.menu)	# 连接信号槽
		self.traverseMenuToConnect_CloseSingal(self.menu)	# 连接信号槽

		# 加载资源
		self.picNum = 0
		self.pix = {}
		self.currentText = ''
		self.loadImage()
		self.actionPic = self.pix['stand']
		self.emojiPic = self.pix['emoji'][0]
		self.showBubble = False

		# Win句柄
		self.hwnd_title = {}	# 仅限Wineee

		# 子窗口
		self.bubble = BubbleBox()
		self.parchment = DialogBox('')
		self.tray = TrayIcon()

		# 信号槽
		self.bubbleUpdate.connect(self.bubble.getData)
		self.bubble.showParchment.connect(self.showParchment)
		self.tray.trayQuit.connect(self.quit)

		# 状态机循环
		self.timer = QTimer() # 初始化一个定时器
		self.timer.start(int(1000/30))	# 设置时间间隔并启动定时器
		self.timer.timeout.connect(self.actionCycle)   # 定时器结束，actionCycle()

		self.animationTimer = QTimer()
		self.animationTimer.start(int(1000/cfg.FPS)) # 动画更新速度同步屏幕帧率
		self.animationTimer.timeout.connect(self.update)
		self.animationTimer.timeout.connect(self.bubble.update)
		self.animationTimer.timeout.connect(self.menuBubbleUpdate_)

#		self.handleCheckTimer = QTimer()
#		self.handleCheckTimer.start(int(1000/10))
#		self.handleCheckTimer.timeout.connect(self.checkHandlesAction)

		self.show()

	def initPos(self):
		screen = QDesktopWidget().screenGeometry()  # QDesktopWidget为一个类，调用screenGeometry函数获得屏幕的尺寸
		size = self.geometry()
		x = screen.width() - size.width()
		y = screen.height() - size.height()
		self.move(int(x), int(y)) # 调用move移动到指定位置

	def paintEvent(self, event):	# 绘制窗口
		if not self.showBubble:	# 如果不显示窗口, 则将窗口图案设为空图片
			self.emojiPic = self.pix['emoji'][0]	# pix['emoji'][0]为全透明图片
		self.bubbleUpdate.emit(self.emojiPic, self.posX, self.posY, self.running_action, self.actualAction, self.mirrored, self.picNum)
		self.bubble.show()

		self.menuBubbleUpdate.emit(self.posX, self.posY, self.running_action, self.actualAction, self.picNum)

		paint = QPainter(self)
		self.resize(self.actionPic.size())	# 获取图片大小
		self.setMask(self.actionPic.mask())   # 设置蒙版
		paint.drawPixmap(0, 0, self.actionPic.width(), self.actionPic.height(), self.actionPic)

	'''载入资源'''
	def loadImage(self):
		self.pix.update({'stand' : QPixmap(os.path.join('./img/stand', str(0) + '.png'))})

		temp = []
		for i in range(0, 16):	# 动作帧数
			temp.append(QPixmap(os.path.join('./img/trot', str(i) +'.png')))
		self.pix.update({'trot' : temp})

		temp = []
		for i in range(0, 9):
			temp.append(QPixmap(os.path.join('./img/sit', str(i) +'.png')))
		self.pix.update({'sitDown' : temp})

		temp = []
		for i in range(9, 16):
			temp.append(QPixmap(os.path.join('./img/sit', str(i) +'.png')))
		self.pix.update({'standUp' : temp})

		temp = []
		for i in range(0, 7):
			temp.append(QPixmap(os.path.join('./img/lie', str(i) +'.png')))
		self.pix.update({'lieDown' : temp})

		temp = []
		for i in range(7, 13):
			temp.append(QPixmap(os.path.join('./img/lie', str(i) +'.png')))
		self.pix.update({'getUp' : temp})

#		temp = []
#		for i in range(0, 10):
#			temp.append(QPixmap(os.path.join('./img/fly', str(i) +'.png')))
#		self.pix.update({'fly' : temp})

		temp = []
		for i in range(0, 18):
			temp.append(QPixmap(os.path.join('./img/boop', str(i) +'.png')))
		self.pix.update({'standBoop' : temp})

		temp = []
		for i in range(0, 2):
			temp.append(QPixmap(os.path.join('./img/emoji', str(i) +'.png')))
		self.pix.update({'emoji' : temp})
	''''''

	'''状态机'''
	def actionCycle(self):	# 状态机本机
		self.sitDownAction()
		self.lieDownAction()
		self.getUpAction()
		self.standUpAction()
		self.trotAction()
		self.standBoopAction()
		self.checkHandlesAction()	# 仅限Win

	def standAction(self):
		if not self.mirrored:
			self.actionPic = self.pix['stand']
		else:
			self.actionPic = self.flipHorizontally(self.pix['stand'])

	def trotAction(self):
		screen = QDesktopWidget().screenGeometry()

		if self.direction & 0b0100:	# Left
			self.posX -= cfg.STEP_LEN	# 步长
			if self.posX + self.bubble.textPix['trot'][self.picNum][0] < 0:	# 空气墙
				self.posX += cfg.STEP_LEN
			self.move(self.posX, self.posY)

		if self.direction & 0b0001:	# Right
			self.posX += cfg.STEP_LEN
			if self.posX + self.bubble.textPix['trot'][self.picNum][2] > screen.width():
				self.posX -= cfg.STEP_LEN
			self.move(self.posX, self.posY)

		if self.direction & 0b1000:	# Up
			self.posY -= cfg.STEP_LEN
			if self.posY + self.bubble.textPix['trot'][self.picNum][1] < 0:
				self.posY += cfg.STEP_LEN
			self.move(self.posX, self.posY)

		if self.direction & 0b0010:	# Down
			self.posY += cfg.STEP_LEN
			if self.posY + self.bubble.textPix['trot'][self.picNum][3] > screen.height():
				self.posY -= cfg.STEP_LEN
			self.move(self.posX, self.posY)

		if self.direction & 0b1111:
			self.picNum += 1
			if self.picNum > 15:	# 越界检测
				self.picNum = 0
			self.actionPic = self.pix['trot'][self.picNum]
			if self.mirrored:
				self.actionPic = self.flipHorizontally(self.pix['trot'][self.picNum])

	def sitDownAction(self):
		if self.running_action == 'sitDown':
			if not self.mirrored:
				self.actionPic = self.pix['sitDown'][self.picNum]
			else:
				self.actionPic = self.flipHorizontally(self.pix['sitDown'][self.picNum])
			self.picNum += 1
			if self.picNum > 8:	# 越界检测
				self.running_action = ''
				self.picNum = 0
				self.is_running_action = False

	def lieDownAction(self):
		if self.running_action == 'lieDown':
			if not self.mirrored:
				self.actionPic = self.pix['lieDown'][self.picNum]
			else:
				self.actionPic = self.flipHorizontally(self.pix['lieDown'][self.picNum])
			self.picNum += 1
			if self.picNum > 6:
				self.running_action = ''
				self.picNum = 0
				self.is_running_action = False


	def getUpAction(self):
		if self.running_action == 'getUp':
			if not self.mirrored:
				self.actionPic = self.pix['getUp'][self.picNum]
			else:
				self.actionPic = self.flipHorizontally(self.pix['getUp'][self.picNum])
			self.picNum += 1
			if self.picNum > 5:
				self.running_action = ''
				self.picNum = 0
				self.is_running_action = False


	def standUpAction(self):
		if self.running_action == 'standUp':
			if not self.mirrored:
				self.actionPic = self.pix['standUp'][self.picNum]
			else:
				self.actionPic = self.flipHorizontally(self.pix['standUp'][self.picNum])
			self.picNum += 1
			if self.picNum > 6:
				self.running_action = ''
				self.picNum = 0
				self.is_running_action = False


	def standBoopAction(self):
		if self.running_action == 'standBoop':
			if not self.mirrored:
				self.actionPic = self.pix['standBoop'][self.picNum]
			else:
				self.actionPic = self.flipHorizontally(self.pix['standBoop'][self.picNum])
			self.picNum += 1
			if self.picNum > 17:
				self.running_action = ''
				self.picNum = 0
				self.is_running_action = False

	def checkHandlesAction(self):	# 仅限Win
		handles = []	# 句柄集
		path_list = os.listdir('./memo')
		self.showBubble = False

		handles = self.getHandles()

		for handle in handles:	# 检测关键词备忘录
			existKeyword = []
			longestKey = ''

			for key in path_list:
				if os.path.splitext(key)[1] == '.txt':  # 打开.txt文件
					if key[ : -4] in handle:	# 提取文件名
						existKeyword.append(key[ : -4])

			if len(existKeyword) > 0:
				self.emojiPic = self.pix['emoji'][1]
				self.showBubble = True

				longestKey = existKeyword[0]
				for key in existKeyword:
					if len(key) > len(longestKey):
						longestKey = key

				text = self.readText(os.path.join('./memo', longestKey + '.txt'))
				if text != self.currentText:	# 如果当前窗口文本与已创建的文本不同, 则用当前窗口文本创建一个新的对话框
					self.parchment = DialogBox(text)
					self.currentText = text	# 更新已创建文本

				break	# 只显示最上层句柄的备忘录

		self.hwnd_title = {}
	''''''

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
			self.bubble.moveToPos()
			event.accept()

	def mouseReleaseEvent(self, event):	# 鼠标释放时, 取消绑定
		self.is_follow_mouse = False
		self.setCursor(QCursor(Qt.ArrowCursor))


	def contextMenuEvent(self, event):  # 右键菜单
#		menu = QMenu(self)

#		openFolderAction = menu.addAction('&备忘录文件夹')
#		openFolderAction.triggered.connect(self.openMemoFolder)

#		checkHandlesAction = menu.addAction('&查看当前句柄')
#		checkHandlesAction.triggered.connect(self.showCurrentHandles)

#		checkHandlesAction = menu.addAction('&抽取随机任务')
#		checkHandlesAction.triggered.connect(self.randomTODOList)

#		quitAction = menu.addAction('&退出')
#		quitAction.triggered.connect(self.quit)

#		menu.exec_(event.globalPos())
		for i in self.menu:
			self.menu[i].info.showBubble = True

	def keyPressEvent(self, event):	# 按下键盘检测
		if event.key() == Qt.Key_X and not self.is_running_action:	# 保证动作不会冲突
			self.currentAction -= 1
			if self.currentAction < -2:
				self.currentAction = -2
		elif event.key() == Qt.Key_C and not self.is_running_action:
			self.currentAction += 1
			if self.currentAction > 1:
				self.currentAction = 1
		elif event.key() == Qt.Key_B and not self.is_running_action and self.actualAction == 0:
			self.is_running_action = True
			self.running_action = 'standBoop'
			self.standBoopAction()
		elif event.key() == Qt.Key_W:
			self.direction |= 0b1000
			self.running_action = 'trot'
			self.is_running_action = True
		elif event.key() == Qt.Key_A:
			self.direction |= 0b0100
			self.running_action = 'trot'
			self.is_running_action = True
			self.mirrored = False	# 改变面向方向
		elif event.key() == Qt.Key_S:
			self.direction |= 0b0010
			self.running_action = 'trot'
			self.is_running_action = True
		elif event.key() == Qt.Key_D:
			self.direction |= 0b0001
			self.running_action = 'trot'
			self.is_running_action = True
			self.mirrored = True	# 改变面向方向

		self.actionChange()

	def actionChange(self):
		if self.actualAction == 0 and self.currentAction == -1:	# 由站到坐
			self.running_action = 'sitDown'
			self.is_running_action = True
		elif self.actualAction == -1 and self.currentAction == -2:	# 由坐到卧
			self.running_action = 'lieDown'
			self.is_running_action = True
		elif self.actualAction == -2 and self.currentAction == -1:	# 由卧到坐
			self.running_action = 'getUp'
			self.is_running_action = True
		elif self.actualAction == -1 and self.currentAction == 0:	# 由坐到站
			self.running_action = 'standUp'
			self.is_running_action = True

		self.actualAction = self.currentAction

	def keyReleaseEvent(self, event):	# 松开键盘检测
		if event.isAutoRepeat():	# 防止松开事件重复
			pass
		elif event.key() == Qt.Key_A or event.key() == Qt.Key_D or event.key() == Qt.Key_W or event.key() == Qt.Key_S:
			if event.key() == Qt.Key_W:
				self.direction &= 0b0111
			elif event.key() == Qt.Key_A:
				self.direction &= 0b1011
			elif event.key() == Qt.Key_S:
				self.direction &= 0b1101
			elif event.key() == Qt.Key_D:
				self.direction &= 0b1110

			if self.direction == 0b0000:
				self.picNum = 0
				self.standAction()
				self.is_running_action = False
				self.currentAction = 0
				self.actualAction = self.currentAction
	''''''

	'''其他函数'''
	def quit(self):
		self.close()
		sys.exit()

	def showParchment(self):	# 显示对话框
		self.parchment.show()

	def flipHorizontally(self, pix):	# 水平翻转
		temp = pix.toImage()
		temp = temp.mirrored(True, False)	# 水平翻转图像
		return self.actionPic.fromImage(temp)

	def QtPixmap_to_CVImg(self, QtPixmap):	# QPixmap转OpenCV
		QImg = QtPixmap.toImage()
		temp_shape = (QImg.height(), QImg.bytesPerLine() * 8 // QImg.depth())
		temp_shape += (4 , )
		ptr = QImg.bits()
		ptr.setsize(QImg.byteCount())
		result = numpy.array(ptr, dtype=numpy.uint8).reshape(temp_shape)
		#result = result[..., :3]	# 不带Alpha通道
		return result

	def CVImg_to_QtImg(self, CVImg):	# OpenCV转QImage
		height, width, depth = CVImg.shape
#		CVImg = cv2.cvtColor(CVImg, cv2.COLOR_BGR2RGB)
#		CVImg = QImage(CVImg.data, width, height, width * depth, QImage.Format_RGB888)	# 不带Alpha通道
		CVImg = QImage(CVImg.data, width, height, width * depth, QImage.Format_ARGB32)
		return CVImg

	def readText(self, path):	# 读取txt文件, 返回一个str数组
		temp = []

		f = open(path, encoding = 'utf-8')
		for line in f:
			temp.append(line)

		f.close()
		return temp

	def openMemoFolder(self):	# 打开对应文件夹
		os.startfile(os.path.abspath('./memo'))

	def showCurrentHandles(self):
		self.parchment = DialogBox(self.getHandles())
		self.showParchment()

	def getHandles(self):
		handles = []
		win32gui.EnumWindows(self.get_all_hwnd, 0)
		for h, t in self.hwnd_title.items():
			if t != '':
				handles.append(t)
		return handles

	def get_all_hwnd(self, hwnd, mouse):	# 仅限Win
		if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd):
			self.hwnd_title.update({hwnd : win32gui.GetWindowText(hwnd)})

	def randomTODOList(self):
		listContent = []
		listNum = []
		outText = []

		f = open('./memo/randomTODO.txt', encoding = 'utf-8')
		for line in f:
			if '[' in line:
				listContent.append(line[:line.find('[')])
				listNum.append(int(line[line.find('[') + 1 : line.find(']')]))
		f.close()

		num = 0
		for i in listNum:
			num += i
		num = random.randint(0, num)

		result = -1
		for i in range(0, len(listNum)):
			num -= listNum[i]
			if num <= 0 and listNum[i] > 0:
				result = i
				listNum[i] -= 1
				break

		if result != -1:
			out = open('./memo/randomTODO.txt', 'w', encoding = 'utf-8')
			for i in range(0, len(listNum)):
				out.write(listContent[i] + '[' + str(listNum[i]) + ']\n')
			out.close()

			resultContent = listContent[result]
			outText.append(resultContent)
		else:
			outText.append('无可抽取项')

		self.parchment = DialogBox(outText)
		self.showParchment()

	def traverseMenu(self, menu):
		for i in menu:
			if menu[i].info.showBubble:
				self.menuBubble.append(menu[i])

			if menu[i].info.son != {}:
				self.traverseMenu(menu[i].info.son)

	def traverseMenuToConnect_UpdateSingal(self, menu):
		for i in menu:	# 连接位置更新函数
			self.menuBubbleUpdate.connect(menu[i].getData)

			if menu[i].info.son != {}:	# 子类递归
				self.traverseMenuToConnect_UpdateSingal(menu[i].info.son)

	def traverseMenuToConnect_CloseSingal(self, menu):
		for i in menu:	# 连接同级菜单的关闭函数
			for j in menu:
				if i != j:
					menu[i].closeSubclass.connect(menu[j].menuClose)

			if menu[i].info.son != {}:	# 子类递归
				self.traverseMenuToConnect_CloseSingal(menu[i].info.son)

	def menuBubbleUpdate_(self):
		self.menuBubble = []
		self.traverseMenu(self.menu)
		for bubble in self.menuBubble:
			bubble.update()
			bubble.show()
	''''''

class BubbleBox(QWidget):
	showParchment = pyqtSignal()

	def __init__(self, parent=None, **kwargs):
		super(BubbleBox, self).__init__(parent)
		# 初始化
		self.setWindowFlags(Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint|Qt.SubWindow)
		self.setAutoFillBackground(False)
		self.setAttribute(Qt.WA_TranslucentBackground, True)
		self.update()

		self.BUBBLE_OFFSET = [20, -60]	# 对话框相对于当前姿势有效图片左上角x, y轴的偏移像素
		self.IMG_WIDTH = 80*4

		self.textPix = {}
		self.loadPos()

		# 从信号槽读取
		self.emojiPic = None
		self.posX = 0	# 主窗口坐标
		self.posY = 0	# 主窗口坐标
		self.running_action = ''
		self.actualAction = 0
		self.mirrored = False
		self.picNum = 0

	def paintEvent(self, event):	# 绘制窗口
		self.moveToPos()
		
		paint = QPainter(self)
		self.resize(self.emojiPic.size())	# 获取图片大小
		self.setMask(self.emojiPic.mask())   # 设置蒙版
		paint.drawPixmap(0, 0, self.emojiPic.width(), self.emojiPic.height(), self.emojiPic)

	def moveToPos(self):
		x = 0
		y = 0

		if self.running_action == '':
			if self.actualAction == 0:
				x = self.textPix[''][0][0] + self.BUBBLE_OFFSET[0]
				y = self.textPix[''][0][1] + self.BUBBLE_OFFSET[1]
			elif self.actualAction == -1:
				x = self.textPix['lieDown'][0][0] + self.BUBBLE_OFFSET[0]
				y = self.textPix['lieDown'][0][1] + self.BUBBLE_OFFSET[1]
			elif self.actualAction == -2:
				x = self.textPix['getUp'][0][0] + self.BUBBLE_OFFSET[0]
				y = self.textPix['getUp'][0][1] + self.BUBBLE_OFFSET[1]
		else:
			x = self.textPix[self.running_action][self.picNum][0] + self.BUBBLE_OFFSET[0]
			y = self.textPix[self.running_action][self.picNum][1] + self.BUBBLE_OFFSET[1]
		if self.mirrored:
			x = self.IMG_WIDTH - (x + self.emojiPic.width())
		x += self.posX
		y += self.posY

		self.move(int(x), int(y))	# 调用move移动到指定位置

	def loadPos(self):	# 载入相对位移数据
		self.textPix.update({'' : [self.loadText(os.path.join('./img/stand', str(0) + '.txt'))]})

		temp = []
		for i in range(0, 16):
			temp.append(self.loadText(os.path.join('./img/trot', str(i) + '.txt')))
		self.textPix.update({'trot' : temp})

		temp = []
		for i in range(0, 9):
			temp.append(self.loadText(os.path.join('./img/sit', str(i) +'.txt')))
		self.textPix.update({'sitDown' : temp})

		temp = []
		for i in range(9, 16):
			temp.append(self.loadText(os.path.join('./img/sit', str(i) +'.txt')))
		self.textPix.update({'standUp' : temp})

		temp = []
		for i in range(0, 7):
			temp.append(self.loadText(os.path.join('./img/lie', str(i) +'.txt')))
		self.textPix.update({'lieDown' : temp})

		temp = []
		for i in range(7, 13):
			temp.append(self.loadText(os.path.join('./img/lie', str(i) +'.txt')))
		self.textPix.update({'getUp' : temp})

#		temp = []
#		for i in range(0, 10):
#			temp.append(self.loadText(os.path.join('./img/fly', str(i) +'.txt')))
#		self.textPix.update({'fly' : temp})

		temp = []
		for i in range(0, 18):
			temp.append(self.loadText(os.path.join('./img/boop', str(i) +'.txt')))
		self.textPix.update({'standBoop' : temp})

	def loadText(self, path):
		temp = []

		f = open(path, encoding = 'utf-8')
		for line in f:
			temp.append(int(line))

		return temp

	'''事件处理'''
	def mousePressEvent(self, event):		# 鼠标左键按下时, 打开对话框
		if event.button() == Qt.LeftButton:
			self.showParchment.emit()
			event.accept()
	''''''

	'''信号处理'''
	def getData(self, emojiPic, posX, posY, running_action, actualAction, mirrored, picNum):
		self.emojiPic = emojiPic
		self.posX = posX	# 主窗口坐标
		self.posY = posY	# 主窗口坐标
		self.running_action = running_action
		self.actualAction = actualAction
		self.mirrored = mirrored
		self.picNum = picNum
	''''''

class DialogBox(QWidget):
	def __init__(self, s, parent=None, **kwargs):
		super(DialogBox, self).__init__(parent)
		# 初始化
		self.setWindowFlags(Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint|Qt.SubWindow)
		self.setAutoFillBackground(False)
		self.setAttribute(Qt.WA_TranslucentBackground, True)
		self.update()

		self.textBox = QPixmap('./img/parchment/Dialog.png')
		self.textRaw = s
		self.textSlice = []
		self.textPic = []
		self.textPages = []
		self.currentPage = 0
		self.size = self.textBox.size()	# 获取textBox的大小

		self.charPerLine = int((self.size.width() - cfg.INITIAL_OFFSET[1]) / (cfg.FONT_SIZE + cfg.HORIZONTAL_SPACING))
		self.linePerPage = int((self.size.height() - cfg.INITIAL_OFFSET[0]) / (cfg.FONT_SIZE + cfg.VERTICAL_SPACING))

		self.initPos()
		self.oneRowSlicer()
		for line in self.textSlice:
			self.oneRowGenerater(line, cfg.FONT_SIZE)
		self.pageGenerater()

	def initPos(self):
		screen = QDesktopWidget().screenGeometry()  # QDesktopWidget为一个类，调用screenGeometry函数获得屏幕的尺寸
		x = screen.width()/2 - self.size.width()/2
		y = screen.height() - cfg.BUTTOM_OFFSET
		self.move(int(x), int(y)) # 调用move移动到指定位置

	def paintEvent(self, event):	# 绘制窗口
		paint = QPainter(self)
		self.textBox = self.textPages[self.currentPage]

		self.resize(self.textBox.size())	# 获取图片大小
		self.setMask(self.textBox.mask())   # 设置蒙版
		paint.drawPixmap(0, 0, self.textBox.width(), self.textBox.height(), self.textBox)

	def oneRowGenerater(self, text, font_size = 24): # (内容, 大小)
		font = ImageFont.truetype('./img/parchment/font/方正像素12.ttf', font_size)   # 字体路径及文本大小
		text_width, text_height = font.getsize(text)	# 字体框大小
		image = Image.new(mode = 'RGBA', size = (text_width, text_height))  # 生成图像
		draw_table = ImageDraw.Draw(im = image)
		draw_table.text(xy = (0, 0), text = text, fill = cfg.FONT_COLOR, font = font)	# 生成文本为白色
 
		self.textPic.append(image)

	def oneRowSlicer(self):
		for s in self.textRaw:
			textLen = 0
			counter = 0
			needSlice = False
			for word in s:
				if '\u4e00' <= word <= '\u9fff':	# 中文字符占两位, 英文字符占一位
					textLen += 2
				else:
					textLen += 1
				counter += 1
				if textLen > self.charPerLine*2:
					needSlice = True
					break
			if needSlice:	# 递归剪切过长的片段
				self.textSlice.append(s[:counter])
				self.Slicer(s[counter:])
			else:
				self.textSlice.append(s)

	def Slicer(self, s):	# 递归函数
		textLen = 0
		counter = 0
		for word in s:
			if '\u4e00' <= word <= '\u9fff':	# 中文字符占两位, 英文字符占一位
				textLen += 2
			else:
				textLen += 1
			counter += 1
		if textLen > self.charPerLine*2:
			self.textSlice.append(s[:counter])
			self.Slicer(s[counter:])
		else:
			self.textSlice.append(s)

	def pageGenerater(self):
		if len(self.textPic) > self.linePerPage:
			temp = Image.open('./img/parchment/DialogDownPointer.png')
		else:
			temp = Image.open('./img/parchment/Dialog.png')

		target = Image.new(mode = 'RGBA', size = (temp.width, temp.height))
		for i in range(0, self.linePerPage):
			if i >= len(self.textPic):
				break
			target.paste(self.textPic[i], (cfg.INITIAL_OFFSET[0], cfg.INITIAL_OFFSET[1] + (cfg.FONT_SIZE + cfg.VERTICAL_SPACING)*i))	# 左上角坐标, 初始偏移量(y, x)
		temp = Image.alpha_composite(temp, target)	# 带Alpha通道的粘贴
		temp = ImageQt.toqpixmap(temp)	# QImage => QPixmap

		self.textPages.append(temp)

		if len(self.textPic) > self.linePerPage:
			self.textPic = self.textPic[self.linePerPage:]
			self.pageGenerater()

	def mousePressEvent(self, event):		# 鼠标左键按下时, 换页
		if event.button() == Qt.LeftButton:
			if self.currentPage < len(self.textPages) - 1:
				self.currentPage += 1
				self.update()
			else:
				self.currentPage = 0
				self.quit()
			event.accept()

	def quit(self):
		self.close()

class TrayIcon(QSystemTrayIcon):
	trayQuit = pyqtSignal()

	def __init__(self, parent=None):
		super(TrayIcon, self).__init__(parent)

		self.setIcon(QIcon("./img/favIcon256.ico"))	# 设置图标
		self.icon = self.MessageIcon()
		self.showMenu()
		self.show()

	def showMenu(self):
		self.menu = QMenu()

		self.openMemoFolderAction = QAction("备忘录文件夹", self, triggered = self.openMemoFolder)
		self.quitAction = QAction("退出", self, triggered = self.quit)

		self.menu.addAction(self.openMemoFolderAction)
		self.menu.addAction(self.quitAction)

		self.setContextMenu(self.menu)

	'''其他函数'''
	def quit(self):
		self.trayQuit.emit()

	def openMemoFolder(self):	# 打开对应文件夹
		os.startfile(os.path.abspath('./memo'))

class menuBubble(QWidget):
	# 定义信号
	functionActive = pyqtSignal()	# 触发按钮功能(连接到实现功能的函数)
	closeSubclass = pyqtSignal()	# 关闭同级菜单的子菜单

	def __init__(self, info, icon, function, parent=None, **kwargs):
		super(menuBubble, self).__init__(parent)
		# 初始化
		self.setWindowFlags(Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint|Qt.SubWindow)
		self.setAutoFillBackground(False)
		self.setAttribute(Qt.WA_TranslucentBackground, True)
		self.update()

		self.info = info
		self.icon = icon
		self.function = function

		self.textPix = {}
		self.loadPos()

		# 从信号槽读取
		self.posX = 0	# 主窗口坐标
		self.posY = 0	# 主窗口坐标
		self.running_action = ''
		self.actualAction = 0
		self.mirrored = False
		self.picNum = 0

	def paintEvent(self, event):	# 绘制窗口
		if self.info.showBubble:
			self.moveToPos()
		
			paint = QPainter(self)
			self.resize(self.icon.size())	# 获取图片大小
			self.setMask(self.icon.mask())   # 设置蒙版
			paint.drawPixmap(0, 0, self.icon.width(), self.icon.height(), self.icon)

	def moveToPos(self):
		x = 0
		y = 0

		if self.running_action == '':	# 对齐中心
			if self.actualAction == 0:
				x = (self.textPix[''][0][0] + self.textPix[''][0][2]) / 2
				y = (self.textPix[''][0][1] + self.textPix[''][0][3]) / 2
			elif self.actualAction == -1:
				x = (self.textPix['lieDown'][0][0] + self.textPix['lieDown'][0][2]) / 2
				y = (self.textPix['lieDown'][0][1] + self.textPix['lieDown'][0][3]) / 2
			elif self.actualAction == -2:
				x = (self.textPix['getUp'][0][0] + self.textPix['getUp'][0][2]) / 2
				y = (self.textPix['getUp'][0][1] + self.textPix['getUp'][0][3]) / 2
		else:
			x = (self.textPix[self.running_action][self.picNum][0] + self.textPix[self.running_action][self.picNum][2]) / 2
			y = (self.textPix[self.running_action][self.picNum][1] + self.textPix[self.running_action][self.picNum][3]) / 2
		x -= self.icon.width() / 2
		y -= self.icon.height() / 2
		x += self.posX
		y += self.posY

		x += self.info.r * math.cos(math.radians(-self.info.angle))	# 偏移量计算, 因为math的度数居然是顺时针旋转的, 所以加上负号变为逆时针旋转
		y += self.info.r * math.sin(math.radians(-self.info.angle))

		self.move(int(x), int(y))	# 调用move移动到指定位置

	def loadPos(self):	# 载入相对位移数据
		self.textPix.update({'' : [self.loadText(os.path.join('./img/stand', str(0) + '.txt'))]})

		temp = []
		for i in range(0, 16):
			temp.append(self.loadText(os.path.join('./img/trot', str(i) + '.txt')))
		self.textPix.update({'trot' : temp})

		temp = []
		for i in range(0, 9):
			temp.append(self.loadText(os.path.join('./img/sit', str(i) +'.txt')))
		self.textPix.update({'sitDown' : temp})

		temp = []
		for i in range(9, 16):
			temp.append(self.loadText(os.path.join('./img/sit', str(i) +'.txt')))
		self.textPix.update({'standUp' : temp})

		temp = []
		for i in range(0, 7):
			temp.append(self.loadText(os.path.join('./img/lie', str(i) +'.txt')))
		self.textPix.update({'lieDown' : temp})

		temp = []
		for i in range(7, 13):
			temp.append(self.loadText(os.path.join('./img/lie', str(i) +'.txt')))
		self.textPix.update({'getUp' : temp})

#		temp = []
#		for i in range(0, 10):
#			temp.append(self.loadText(os.path.join('./img/fly', str(i) +'.txt')))
#		self.textPix.update({'fly' : temp})

		temp = []
		for i in range(0, 18):
			temp.append(self.loadText(os.path.join('./img/boop', str(i) +'.txt')))
		self.textPix.update({'standBoop' : temp})

	def loadText(self, path):
		temp = []

		f = open(path, encoding = 'utf-8')
		for line in f:
			temp.append(int(line))

		return temp

	'''事件处理'''
	def mousePressEvent(self, event):		# 鼠标左键按下时, 打开对话框
		if event.button() == Qt.LeftButton:
			if self.function == 'menuLayer':
				for i in self.info.son:
					self.info.son[i].info.showBubble = True
			elif self.function == 'functionButton':
				self.functionActive.emit()
		self.closeSubclass.emit()
	''''''

	'''信号处理'''
	def getData(self, posX, posY, running_action, actualAction, picNum):
		self.posX = posX	# 主窗口坐标
		self.posY = posY	# 主窗口坐标
		self.running_action = running_action
		self.actualAction = actualAction
		self.picNum = picNum

	def menuClose(self):	# 关闭子菜单
		self.update()
		for i in self.info.son:
			self.info.son[i].info.showBubble = False
			self.info.son[i].menuClose()
	''''''

class menuLayout():
	def __init__(self, name, r, angle):
		self.name = name
		self.r = r
		self.angle = angle
		self.son = {}
		self.showBubble = False

'''run'''
if __name__ == '__main__':
	app = QApplication(sys.argv)
	pet = DesktopPet()
	sys.exit(app.exec_())
