import sys, os
from PIL import Image

try:
	imageFileName = sys.argv[1]
except:
	print 'Usage: make_sprites.py path/to/icon'
	sys.exit(2)

image = Image.open(imageFileName)
imageBasename = os.path.basename(imageFileName) # aaa.png
basenameAndExt = os.path.splitext(imageBasename) # ("aaa", ".png")
resultDir = "%s_%s" % (basenameAndExt[0], basenameAndExt[1][1:]) # aaa_png

(imageWidth, imageHeight) = image.size

#check if result directory exists
if not os.path.isdir(resultDir):
	os.makedirs(resultDir)
	
resultImage = Image.new("RGBA", (imageWidth, 360*imageHeight))

for angle in range(0, 360):
	resultImage.paste(image.rotate(-angle), (0, angle*imageHeight))

resultImage.save( "%s/%s" % (resultDir, imageBasename) )