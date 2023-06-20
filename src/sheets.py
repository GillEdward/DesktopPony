# 对应./src/ts/common/sheets.ts

# width	# 每帧的宽度
# height	# 每帧的长度,也是相对Y偏移量
# offset	# 下一帧的相对X偏移量
# offsetY	# 下一帧的额外相对Y偏移量
# padLeft
# empties
# wrap	# 多行素材情况下,每行的素材数
# paletteOffset
# rows	# 总计素材数

frontLegsCount = 40	# 前腿动作帧数量
backLegsCount = 27	# 后腿动作帧数量

frontLegsSheet = {	# 前腿素材表(下列相同)
	'width' : 55,	# 每帧的宽度
	'height' : 60,	# 每帧的长度
	'offset' : 50,	# 下一帧的相对坐标偏移量
}

backLegsSheet = {
	'width' : 55,
	'height' : 60,
	'offset' : 55,
}

bodySheet = {
	'width' : 60,
	'height' : 60,
	'offset' : 50,
}

chestSheet = {
	'width' : 60,
	'height' : 60,
	'offset' : 60,
}

waistSheet = chestSheet

singleFrameSheet = bodySheet

headSheet = {
	'width' : 60,
	'height' : 75,
	'offset' : 60,
	'offsetY' : 20,
};

wingSheet = {
	'width' : 80,
	'height' : 70,
	'offset' : 70,
	'offsetY' : 10,
}

tailSheet = {
	'width' : 80,
	'height' : 70,
	'offset' : 70,
	'padLeft' : 20,
}

frontLegsHoovesSheet = frontLegsSheet

frontLegsAccessoriesSheet = frontLegsSheet

frontLegsSleevesSheet = frontLegsSheet

backLegsHoovesSheet = backLegsSheet

backLegsAccessoriesSheet = backLegsSheet

backLegsSleevesSheet = backLegsSheet
backLegsSleevesSheet['rows'] = 2

bodyWingsSheet = {
	'width' : 80,
	'height' : 70,
	'offset' : 70,
	'offsetY' : 10,
}

neckAccessory = bodySheet

chestAccessorySheet = bodySheet

backAccessorySheet = chestSheet

waistAccessorySheet = waistSheet

earsSheet = singleFrameSheet
earsSheet['wrap'] = 8
earsSheet['paletteOffsetY'] = 30

hornSheet = headSheet
hornSheet['wrap'] = 8

manesSheet = headSheet
manesSheet['empties'] = [3, 10, 13]
manesSheet['wrap'] = 8

facialHairSheet = singleFrameSheet
facialHairSheet['wrap'] = 8
facialHairSheet['paletteOffsetY'] = 35

earAccessorySheet = singleFrameSheet
earAccessorySheet['wrap'] = 8

headAccessorySheet = headSheet
headAccessorySheet['wrap'] = 8

faceAccessorySheet = headSheet
faceAccessorySheet['wrap'] = 8

extraAccessorySheet = headSheet
extraAccessorySheet['wrap'] = 8
extraAccessorySheet['paletteOffsetY'] = 45

backAccessorySheet = {
	'width' : 55,
	'height' : 40,
	'offset' : 55,
	'offsetY' : 10,
}

wingsSheet = bodySheet

cmSheet = bodySheet

neckAccessorySheet = bodySheet

hatsSheet = {
	'width' : 55,
	'height' : 40,
	'offset' : 55,
	'offsetY' : 10,
	'rows' : 19,
}

earringsSheet = {
	'width' : 55,
	'height' : 40,
	'offset' : 55,
	'offsetY' : 10,
	'rows' : 13,
}

extraSheet = {
	'width' : 55,
	'height' : 40,
	'offset' : 55,
	'offsetY' : 10,
	'rows' : 17,
}

sheet = {}	# 字典的字典, 索引是素材文件夹名
sheet['back-legs'] = backLegsSheet
sheet['back-legs-accessories'] = backLegsAccessoriesSheet
sheet['back-legs-hooves'] = backLegsHoovesSheet
sheet['back-legs-sleeves'] = backLegsSleevesSheet
sheet['body'] = bodySheet
sheet['body-back-accessory'] = backAccessorySheet
sheet['body-chest-accessory'] = chestAccessorySheet
sheet['body-waist-accessory'] = waistAccessorySheet
sheet['body-wings'] = bodyWingsSheet
sheet['ear-accessory'] = earAccessorySheet
sheet['ears'] = earsSheet
sheet['extra-accessory'] = extraAccessorySheet
sheet['face-accessory'] = faceAccessorySheet
sheet['facial-hair'] = facialHairSheet
sheet['front-legs'] = frontLegsSheet
sheet['front-legs-accessories'] = frontLegsAccessoriesSheet
sheet['front-legs-hooves'] = frontLegsHoovesSheet
sheet['front-legs-sleeves'] = frontLegsSleevesSheet
sheet['head'] = headSheet
sheet['head-accessory'] = headAccessorySheet
sheet['horns'] = hornSheet
sheet['manes'] = manesSheet
sheet['neck-accessory'] = neckAccessorySheet
sheet['tails'] = tailSheet