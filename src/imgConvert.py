# 遗留文件, 不知道什么时候有用

def QtPixmap_to_CVImg(QtPixmap):	# QPixmap转OpenCV
	QImg = QtPixmap.toImage()
	temp_shape = (QImg.height(), QImg.bytesPerLine() * 8 // QImg.depth())
	temp_shape += (4 , )
	ptr = QImg.bits()
	ptr.setsize(QImg.byteCount())
	result = numpy.array(ptr, dtype=numpy.uint8).reshape(temp_shape)
	#result = result[..., :3]	# 不带Alpha通道
	return result

def CVImg_to_QtImg(CVImg):	# OpenCV转QImage
	height, width, depth = CVImg.shape
#	CVImg = cv2.cvtColor(CVImg, cv2.COLOR_BGR2RGB)
#	CVImg = QImage(CVImg.data, width, height, width * depth, QImage.Format_RGB888)	# 不带Alpha通道
	CVImg = QImage(CVImg.data, width, height, width * depth, QImage.Format_ARGB32)
	return CVImg
