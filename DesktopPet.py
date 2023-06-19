# pyinstaller -F -w -i favIcon256.ico DesktopPet.py --exclude-module ./cfg.py

from PyQt5.QtWidgets import *

import os
import sys

import cfg
from src.bubbleBox import *
#from src.bubbleDialogBox import *
from src.dialogBox import *
from src.menuBubble import *
from src.menuLayout import *
from src.trayIcon import *

'''桌面宠物'''
class DesktopPet(QWidget):
	# 定义信号
	bubbleUpdate = pyqtSignal(QPixmap, int, int, str, int, bool, int)
#	bubbleDialogUpdate = pyqtSignal(int, int, str, int, bool, int)	# 已将 信号槽机制 改造为 文件读写, 因为两个窗口会互相抢夺控制, 消息刷新时小马无法正常行动
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
		self.menu['备忘录文件夹'].functionActive.connect(self.openMemo)

		self.menu.update({'直播机' : menuBubble(menuLayout('直播机', 150, 180), QPixmap('./img/buttom/直播机.png'), 'functionButton')})
		self.menu['直播机'].functionActive.connect(self.openLiveDM)

		self.menu.update({'关闭' : menuBubble(menuLayout('关闭', 150, 270), QPixmap('./img/buttom/关闭.png'), 'functionButton')})
		self.menu['关闭'].functionActive.connect(self.closeMenu)

		self.traverseMenuToConnect_UpdateSingal(self.menu)	# 连接信号槽
		self.traverseMenuToConnect_CloseSingal(self.menu)	# 连接信号槽

		# 加载资源
		self.picNum = 0
		self.pix = {}
		self.currentText = ''
		self.loadImage()
		self.actionPic = self.pix['stand']
		self.emojiPic = self.pix['emoji'][0]

		# 子窗口
		self.bubble = BubbleBox()
#		self.bubbleDialog = BubbleDialogBox('')
		self.parchment = DialogBox('')
		self.tray = TrayIcon()

		# 子窗口判定
		self.showBubble = False
		self.showBubbleDialog = False
		self.bubbleDialogText = ''

		# 信号槽
		self.bubbleUpdate.connect(self.bubble.getData)
		#self.bubbleDialogUpdate.connect(self.bubbleDialog.getData)	# 每次创建新对象都要重新连接信号槽, 所以在读取处连接
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

		self.animationTimer.timeout.connect(self.openBubbleDialogText)	# 读取弹幕文本信息
#		self.animationTimer.timeout.connect(self.bubbleDialogUpdate_)
		self.animationTimer.timeout.connect(self.bubbleDialogPosWriteIntoFile)

		self.show()

	def initPos(self):
		screen = QDesktopWidget().screenGeometry()  # QDesktopWidget为一个类，调用screenGeometry函数获得屏幕的尺寸
		size = self.geometry()
		x = screen.width() - size.width()
		y = screen.height() - size.height()
		self.move(int(x), int(y)) # 调用move移动到指定位置

	def paintEvent(self, event):	# 绘制窗口
		self.bubbleUpdate.emit(self.emojiPic, self.posX, self.posY, self.running_action, self.actualAction, self.mirrored, self.picNum)
#		self.bubbleDialogUpdate.emit(self.posX, self.posY, self.running_action, self.actualAction, self.mirrored, self.picNum)
		self.menuBubbleUpdate.emit(self.posX, self.posY, self.running_action, self.actualAction, self.picNum)

		if not self.showBubble:	# 如果不显示窗口, 则将窗口图案设为空图片
			self.emojiPic = self.pix['emoji'][0]	# pix['emoji'][0]为全透明图片
		self.bubble.show()	# menu使用计时器更新, bubble使用paintEvent更新, 前者为更先进的解决办法

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
		''' 旧右键菜单
		menu = QMenu(self)

		openFolderAction = menu.addAction('&备忘录文件夹')
		openFolderAction.triggered.connect(self.openMemo)

		quitAction = menu.addAction('&退出')
		quitAction.triggered.connect(self.quit)

		menu.exec_(event.globalPos())
		'''
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

	def closeMenu(self):
		for i in self.menu:
			self.menu[i].info.showBubble = False

	def showParchment(self):	# 显示对话框
		self.parchment.show()

	def flipHorizontally(self, pix):	# 水平翻转
		temp = pix.toImage()
		temp = temp.mirrored(True, False)	# 水平翻转图像
		return self.actionPic.fromImage(temp)

	def readText(self, path):	# 读取txt文件, 返回一个str数组
		temp = []

		f = open(path, encoding = 'utf-8')
		for line in f:
			temp.append(line)

		f.close()
		return temp

	def openBubbleDialogText(self):	# 打开对应文件夹
		text = open('./headBubble.txt', 'r', encoding = 'utf-8').readline()
		if text.find('欢迎') != -1:	# 有人进入直播间自动boop	# 目前仅限于standBoop, 因为动作集还没有更新
			open('./headBubble.txt', 'w', encoding = 'utf-8').write('')
			self.is_running_action = True
			self.running_action = 'standBoop'
			self.standBoopAction()


	def openMemo(self):	# 打开对应文件夹
		text = self.readText(os.path.join('./memo.txt'))
		self.parchment = DialogBox(text)
		self.showParchment()

	def openLiveDM(self):	# 打开直播模块组
#		os.system('python ./liveFunction.py')	# 不能在桌宠函数内调用sys，需要等待
		None

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

#	def bubbleDialogUpdate_(self):
#		self.bubbleDialog.update()
#		if self.showBubbleDialog:	# 如果无新内容, 则不更新头顶气泡
#			self.bubbleDialog.show()
#			self.showBubbleDialog = False

	def bubbleDialogPosWriteIntoFile(self):	# 将小马位置信息写入文件
		open('./ponyPos.txt', 'w', encoding = 'utf-8').write(
			f'{self.posX}\n{self.posY}\n{self.running_action}\n{self.actualAction}\n{self.mirrored}\n{self.picNum}')
	''''''

'''run'''
if __name__ == '__main__':
	app = QApplication(sys.argv)
	pet = DesktopPet()
	sys.exit(app.exec_())