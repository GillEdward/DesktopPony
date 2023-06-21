import cv2
import os
import shutil

def scanFile(path):	# 图片边界数据生成器
	img = cv2.imread(path, -1)
	out = open(os.path.join(path[ :-4] + '.txt'), 'w')
	height = img.shape[0]
	width = img.shape[1]

	minX = width
	minY = height
	maxX = 0
	maxY = 0

	for x in range(0, width):
		for y in range(0, height):
			if img[y][x][3] != 0:
				if x < minX:
					minX = x
				if y < minY:
					minY = y
				if x > maxX:
					maxX = x
				if y > maxY:
					maxY = y

	out.write(str(minX) + '\n' + str(minY) + '\n' + str(maxX) + '\n' + str(maxY))
	print(minX, minY, maxX, maxY)
	out.close()

def scanThisDir(path):  # 扫描文件夹，通过递归遍历
    path_list = os.listdir(path)
    for filename in path_list:
        filesrc = os.path.join(path, filename)
        if os.path.isdir(filesrc):  # 打开文件夹，下一层递归
            scanThisDir(filesrc)
        if os.path.splitext(filename)[1] == '.png':  #打开.png文件
            scanFile(filesrc)

def clearFolder(path):  # 扫描文件夹，通过递归遍历
	path_list = os.listdir(path)
	for filename in path_list:
		filesrc = os.path.join(path, filename)
		if os.path.isdir(filesrc):  # 打开文件夹，下一层递归
			clearFolder(filesrc)
		if os.path.splitext(filename)[1] == '.txt' or os.path.splitext(filename)[1] == '.png':  # 删除老的.txt和.png文件
			os.remove(os.path.join(path, filename))

def clearUselessFiles(key, effectiveLength):
	path_list = os.listdir(os.path.join('../img/ponyAction/', key))	# 对应目录内的文件表

	path_list = [int(i[:-4]) for i in path_list]	# str'0.png' -> int'0', 便于接下来排序
	path_list.sort()

	for i in path_list[effectiveLength:]:	# 删除多余图片
		os.remove(os.path.join('../img/ponyAction/', key, str(i) + '.png'))
	shutil.copy(os.path.join('../img/ponyAction/', key, '0.png'), os.path.join('../img/ponyAction/', key, str(effectiveLength) + '.png'))	# 复制第一帧->最后一帧

'''run'''
if __name__ == '__main__':
	# 截取素材
	width = 320	# 尺寸等于单独导出一张stand的图片大小
	height = 360	# 可以写个自动化读取, Later~
	offset = width

	path = os.getcwd()  # 获得当前目录
	path = path + '/input'
	path_list = os.listdir(path)	# 当前目录内的文件表

	clearFolder('../img/ponyAction/')	# 清除老文件

	actionNames = ['stand', 'trot', 'boop', 'sit', 'boop-sit', 'lie', 'boop-lie', 'fly', 'boop-fly']

	for filename in path_list:	# 截去多余部分(OpenCV2不认识中文qwq)
		if os.path.splitext(filename)[1] == '.png':
			longestKey = ''	# 符合条件的最长关键词,
			for action in actionNames:	# 遍历动作集
				if filename.find(action) != -1 and len(action) > len(longestKey):
					longestKey = action

			shutil.move(os.path.join(path + '/' + filename), os.path.join(path + '/' + longestKey + '.png'))	# 根据动作重命名

	for filename in path_list:
		if os.path.splitext(filename)[1] == '.png':  # 打开.png文件
			img = cv2.imread('./input/' + filename, -1)
			imgHeight = img.shape[0]
			imgWidth = img.shape[1]

			for i in range(0, int(imgWidth / offset)):	# 根据 width height offset 将原图切割为单个文件
				x = offset * i
				img_ = img[0 : height, x : x + offset]	# (y, x)
				#print(0, height, x, x + offset)

				#								放大倍率(x,y), 插值方式:基于局部像素的重采样
				#img_ = cv2.resize(img_, None, img_, 4, 4, cv2.INTER_AREA)	# PT官方导出有倍率放大功能了, 所以禁用该功能
				save_path_file = os.path.join('../img/ponyAction/' + filename[:-4], str(i) + '.png')
				cv2.imwrite(save_path_file, img_)

	# 截取有效帧并重新排序

	# stand
	None	# 输出本来就是顺序的, 不需要重新排序

	# trot
	None

	# boop
	for i in range(0, 7):	# 倒放
		shutil.copy('../img/ponyAction/boop/' + str(i) + '.png', '../img/ponyAction/boop/' + str(14 - i) + '.png')
	clearUselessFiles('boop', 14)

	# sit
	shutil.move('../img/ponyAction/sit/16.png', '../img/ponyAction/sit/0.png')
	shutil.move('../img/ponyAction/sit/17.png', '../img/ponyAction/sit/1.png')
	shutil.move('../img/ponyAction/sit/19.png', '../img/ponyAction/sit/2.png')
	shutil.move('../img/ponyAction/sit/21.png', '../img/ponyAction/sit/3.png')
	shutil.move('../img/ponyAction/sit/22.png', '../img/ponyAction/sit/4.png')
	shutil.move('../img/ponyAction/sit/23.png', '../img/ponyAction/sit/5.png')
	shutil.move('../img/ponyAction/sit/24.png', '../img/ponyAction/sit/6.png')
	shutil.move('../img/ponyAction/sit/25.png', '../img/ponyAction/sit/7.png')
	shutil.move('../img/ponyAction/sit/26.png', '../img/ponyAction/sit/8.png')
	for i in range(0, 8):	# 倒放
		shutil.copy('../img/ponyAction/sit/' + str(i) + '.png', '../img/ponyAction/sit/' + str(16 - i) + '.png')
	clearUselessFiles('sit', 16)

	# boop-sit
	for i in range(0, 8):
		shutil.copy('../img/ponyAction/boop-sit/' + str(i) + '.png', '../img/ponyAction/boop-sit/' + str(16 - i) + '.png')
	clearUselessFiles('boop-sit', 16)

	# lie
	shutil.move('../img/ponyAction/lie/24.png', '../img/ponyAction/lie/0.png')
	shutil.move('../img/ponyAction/lie/25.png', '../img/ponyAction/lie/1.png')
	shutil.move('../img/ponyAction/lie/26.png', '../img/ponyAction/lie/2.png')
	shutil.move('../img/ponyAction/lie/27.png', '../img/ponyAction/lie/3.png')
	shutil.move('../img/ponyAction/lie/28.png', '../img/ponyAction/lie/4.png')
	shutil.move('../img/ponyAction/lie/29.png', '../img/ponyAction/lie/5.png')
	shutil.move('../img/ponyAction/lie/31.png', '../img/ponyAction/lie/6.png')
	for i in range(0, 6):
		shutil.copy('../img/ponyAction/lie/' + str(i) + '.png', '../img/ponyAction/lie/' + str(12 - i) + '.png')
	clearUselessFiles('lie', 12)

	# boop-lie
	for i in range(0, 7):	# 倒放
		shutil.copy('../img/ponyAction/boop-lie/' + str(i) + '.png', '../img/ponyAction/boop-lie/' + str(14 - i) + '.png')
	clearUselessFiles('boop-lie', 14)

	# fly
	None

	# boop-fly
	clearUselessFiles('boop-fly', 12)

	# 生成位置文件
	scanThisDir('../img/ponyAction')   #从当前目录开始扫描