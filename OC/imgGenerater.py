import cv2
import os
import shutil

def scanFile(path):
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

def scanThisDir(path):  #扫描文件夹，通过递归遍历
    path_list = os.listdir(path)
    for filename in path_list:
        filesrc = os.path.join(path, filename)
        if os.path.isdir(filesrc):  #打开文件夹，下一层递归
            scanThisDir(filesrc)
        if os.path.splitext(filename)[1] == '.png':  #打开.png文件
            scanFile(filesrc)

'''run'''
if __name__ == '__main__':
	# 截取素材
	width = 80
	height = 90
	offset = 80

	path = os.getcwd()  # 获得当前目录
	path_list = os.listdir(path)	# 当前目录内的文件表

	for filename in path_list:
		if os.path.splitext(filename)[1] == '.png' and filename.find('-') != -1:	# 截去OC名字, 因为OpenCV2不认识中文qwq
			shutil.move(os.path.join(path + '/' + filename), os.path.join(path + '/' + filename[filename.find('-') + 1:]))

	for filename in path_list:
		if os.path.splitext(filename)[1] == '.png':  # 打开.png文件
			img = cv2.imread(filename, -1)
			imgHeight = img.shape[0]
			imgWidth = img.shape[1]

			for i in range(0, int(imgWidth / offset)):
				x = offset * i
				img_ = img[0 : 90, x : x + offset]
				print(0, 90, x, x + offset)

				save_path_file = os.path.join('../img/' + filename[:-4] + '/' + str(i) + '.png')
				#								   放大(x,y)		插值方式:基于局部像素的重采样
				img_ = cv2.resize(img_, None, img_, 4, 4, cv2.INTER_AREA)
				cv2.imwrite(save_path_file, img_)

	# 截取有效帧并重新排序
	shutil.move('../img/sit/12.png', '../img/sit/0.png')
	shutil.move('../img/sit/13.png', '../img/sit/1.png')
	shutil.move('../img/sit/15.png', '../img/sit/2.png')
	shutil.move('../img/sit/17.png', '../img/sit/3.png')
	shutil.move('../img/sit/18.png', '../img/sit/4.png')
	shutil.move('../img/sit/19.png', '../img/sit/5.png')
	shutil.move('../img/sit/20.png', '../img/sit/6.png')
	shutil.move('../img/sit/21.png', '../img/sit/7.png')
	shutil.move('../img/sit/22.png', '../img/sit/8.png')
	for i in range(0, 7):
		shutil.copy('../img/sit/' + str(i) + '.png', '../img/sit/' + str(15 - i) + '.png')

	shutil.move('../img/lie/12.png', '../img/lie/0.png')
	shutil.move('../img/lie/13.png', '../img/lie/1.png')
	shutil.move('../img/lie/14.png', '../img/lie/2.png')
	shutil.move('../img/lie/15.png', '../img/lie/3.png')
	shutil.move('../img/lie/16.png', '../img/lie/4.png')
	shutil.move('../img/lie/17.png', '../img/lie/5.png')
	shutil.move('../img/lie/19.png', '../img/lie/6.png')
	for i in range(0, 6):
		shutil.copy('../img/lie/' + str(i) + '.png', '../img/lie/' + str(12 - i) + '.png')

	# 生成位置文件
	scanThisDir('../img')   #从当前目录开始扫描