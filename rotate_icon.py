import sys, re, os
from PIL import Image, ImageDraw

try:
	imageFileName = sys.argv[1]
except:
	print 'Usage: rotate_icon.py path/to/icon'
	sys.exit(2)

image = Image.open(imageFileName)
imageBasename = os.path.basename(imageFileName) # aaa.png
basenameAndExt = os.path.splitext(imageBasename) # ("aaa", ".png")
resultDir = "%s_%s" % (basenameAndExt[0], basenameAndExt[1][1:]) # aaa_png

#check if result directory exists
if not os.path.isdir(resultDir):
	os.makedirs(resultDir)

for angle in range(0, 360):
	rotatedImage = image.rotate(-angle)
	rotatedImage.save( "%s/%s_%s%s" % (resultDir, basenameAndExt[0], angle, basenameAndExt[1]) )