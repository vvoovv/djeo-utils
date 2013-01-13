import sys, re, os, getopt
from PIL import Image, ImageDraw, ImageFont

# default value
fontSize = 15
fontFamily = "times"
fontFill = "black"
resultDir = None

try:
	imageFileName = sys.argv[1]
	label = sys.argv[2].decode("cp1251")
	(opts, args) = getopt.getopt(sys.argv[3:], "", ["dir=", "size=", "family=", "fill="])
except:
	print 'Usage: rotate_icon_with_label.py path/to/icon label --dir="dir" --size=15 --family=serif --fill=red'
	print '--dir --size, --family and --fill parameters are optional'
	sys.exit(2)

for o, a in opts:
	if o=="--size":
		fontSize=int(a)
	elif o=="--family":
		fontFamily=a
	elif o=="--fill":
		fontFill=a
	elif o=="--dir":
		resultDir = a

image = Image.open(imageFileName)
imageBasename = os.path.basename(imageFileName) # aaa.png
basenameAndExt = os.path.splitext(imageBasename) # ("aaa", ".png")
if not resultDir: resultDir = "%s_%s" % (basenameAndExt[0], basenameAndExt[1][1:]) # aaa_png

(imageWidth, imageHeight) = image.size

#check if result directory exists
if not os.path.isdir(resultDir):
	os.makedirs(resultDir)

font = ImageFont.truetype("%s.ttf" % fontFamily, fontSize)
(labelWidth, labelHeight) = font.getsize(label)

for angle in range(0, 360):
	resultImage = Image.new("RGBA", (imageWidth+labelWidth+4, imageHeight))
	resultImage.paste(image.rotate(-angle), (0,0))
	ImageDraw.Draw(resultImage).text((imageWidth+4, (imageHeight-labelHeight)/2), label, font=font, fill=fontFill)
	resultImage.save( "%s/%s_%s%s" % (resultDir, basenameAndExt[0], angle, basenameAndExt[1]) )