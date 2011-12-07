import sys, os, json
import xml.dom.minidom as minidom
import kml
json.encoder.FLOAT_REPR = lambda o: format(o, ".3f")

#TODO:
# allow users to ignore some attributes so djeo can overide them

if len(sys.argv) == 1:
	print 'Usage: kml2djeo.py <path to a kml file> <output file name (optional)>'
	sys.exit(0)

kmlFileName = sys.argv[1]
resultFileName = ''
if len(sys.argv) > 2:
	resultFileName = sys.argv[2]
else:
	resultFileName = os.path.splitext( os.path.basename(kmlFileName) )[0] + ".js"

resultFeatures = []
kmlDoc = minidom.parse(kmlFileName)

# build registry of Style and StyleMap nodes
styleRegistry = dict(Style={}, StyleMap={})
for styleNode in kmlDoc.getElementsByTagName("Style"):
	styleRegistry["Style"][styleNode.getAttribute("id")] = styleNode
for styleMapNode in kmlDoc.getElementsByTagName("StyleMap"):
	styleRegistry["StyleMap"][styleMapNode.getAttribute("id")] = styleMapNode

folders = kml.getTopLevelFolders(kmlDoc)
kml.processFolders(folders, resultFeatures, styleRegistry)

resultFile=open(resultFileName, "w")
resultFile.write("define([],")
resultFile.write(json.dumps(resultFeatures, ensure_ascii=False))
resultFile.write(");")