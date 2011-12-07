import xml.dom.minidom as minidom

def getTopLevelFolders(node, folders=[]):
	for childNode in [e for e in node.childNodes if e.nodeType == e.ELEMENT_NODE]:
		if childNode.tagName == "Folder" or childNode.tagName == "Document":
			folders.append(childNode)
		elif childNode.tagName == "kml":
			getTopLevelFolders(childNode, folders)
	return folders

def getChildElementsByTagName(node, tagName):
	return [e for e in node.childNodes if e.nodeType == e.ELEMENT_NODE and e.tagName == tagName]

def processFolders(folders, resultFeatures, styleRegistry):
	for folder in folders:
		featureContainer = dict(
			name = folder.getElementsByTagName("name")[0].firstChild.data.encode("utf-8"),
			features=[]
		)
		featureContainerAppended = False
		visibility = getChildElementsByTagName(folder, "visibility")
		if len(visibility)==0 or visibility[0].firstChild.data!="0":
			# process Placemarks in the folder
			for placemark in getChildElementsByTagName(folder, "Placemark"):
				# check placemark visibility
				visibility = getChildElementsByTagName(placemark, "visibility")
				if len(visibility)>0 and visibility[0].firstChild.data=="0": continue

				placemarkValid = False

				point = placemark.getElementsByTagName("Point")
				lineString = placemark.getElementsByTagName("LineString")
				polygon = placemark.getElementsByTagName("Polygon")
				# Point
				if len(point):
					point = point[0]
					geometry = point
					coordinates = geometry.getElementsByTagName("coordinates")
					if len(coordinates):
						type = "Point"
						coordinates = coordinates[0].firstChild.data.split(",")
						coordinates = map(lambda x: float(x), coordinates)
						placemarkValid = True
				# LineString
				elif len(lineString):
					lineString = lineString[0]
					geometry = lineString
					coordinates = geometry.getElementsByTagName("coordinates")
					if len(coordinates):
						type = "LineString"
						coordinates = coordinates[0].firstChild.data.split()
						coordinates = map(lambda coords: map( lambda x: float(x), coords.split(",") ), coordinates)
						placemarkValid = True
				# Polygon
				elif len(polygon):
					polygon = polygon[0]
					geometry = polygon
					coordinates = geometry.getElementsByTagName("coordinates")
					if len(coordinates):
						type = "Polygon"
						coordinates = coordinates[0].firstChild.data.split()
						coordinates = map(lambda coords: map( lambda x: float(x), coords.split(",") ), coordinates)
						coordinates = [coordinates]
						placemarkValid = True

				if placemarkValid:
					if featureContainerAppended == False:
						resultFeatures.append(featureContainer)
						featureContainerAppended = True
					# check if we have altitudeMode
					altitudeMode = geometry.getElementsByTagName("altitudeMode")
					if len(altitudeMode): altitudeMode = altitudeMode[0].firstChild.data
					else: altitudeMode = None
					name = placemark.getElementsByTagName("name")[0].firstChild.data.encode("utf-8")
					_placemark = dict(
						name = name,
						type = type,
						coords = coordinates
					)
					id = placemark.getAttribute("id")
					if id:
						_placemark["id"] = id.encode("utf-8")
					if name.find("Division Pechora")==0:
						_placemark["label"] = name
					if altitudeMode: _placemark["altitudeMode"] = altitudeMode.encode("utf-8")
					style = getJsonStyle(placemark, styleRegistry)
					if style: _placemark["style"] = style
					featureContainer["features"].append(_placemark)
			_resultFeatures = []
			# process Folders in the folder
			processFolders(getChildElementsByTagName(folder, "Folder"), _resultFeatures, styleRegistry)
			if len(_resultFeatures)>0:
				if featureContainerAppended == False:
					resultFeatures.append(featureContainer)
					featureContainerAppended = True
				for _feature in _resultFeatures:
					featureContainer["features"].append(_feature)


def getJsonStyle(placemark, styleRegistry):
	styleUrl = placemark.getElementsByTagName("styleUrl")
	if len(styleUrl)==0: return None
	resultStyle = None
	styleNode = None
	styleId = styleUrl[0].firstChild.data[1:]
	if styleId in styleRegistry["StyleMap"]:
		styleMap = styleRegistry["StyleMap"][styleId]
		for pair in styleMap.getElementsByTagName("Pair"):
			key = pair.getElementsByTagName("key")[0].firstChild.data
			if key == "normal":
				styleId = pair.getElementsByTagName("styleUrl")[0].firstChild.data[1:]
				if styleId in styleRegistry["Style"]:
					styleNode = styleRegistry["Style"][styleId]
				break
	elif styleId in styleRegistry["Style"]:
		styleNode = styleRegistry["Style"][styleId]

	if styleNode:
		# process IconStyle
		iconStyle = styleNode.getElementsByTagName("IconStyle")
		if len(iconStyle):
			iconStyle = iconStyle[0]
			# href
			href = iconStyle.getElementsByTagName("href")
			if len(href): href = href[0].firstChild.data.encode("utf-8")
			else: href = None
			# scale
			scale = iconStyle.getElementsByTagName("scale")
			if len(scale): scale = float(scale[0].firstChild.data)
			else: scale = None
			
			if href or scale:
				if not resultStyle: resultStyle = {}
				if href:
					resultStyle["img"] = href
				if scale:
					resultStyle["scale"] = scale

		# process LineStyle
		lineStyle = styleNode.getElementsByTagName("LineStyle")
		if len(lineStyle):
			lineStyle = lineStyle[0]
			# color
			color = lineStyle.getElementsByTagName("color")
			if len(color):
				color = color[0].firstChild.data.encode("utf-8")
				strokeOpacity = int(color[0]+color[1], 16)/255.
				# convert to rrggbb
				color = "#"+color[6]+color[7]+color[4]+color[5]+color[2]+color[3]
			else:
				color = None
			# width
			width = lineStyle.getElementsByTagName("width")
			if len(width): width = float(width[0].firstChild.data)
			else: width = None
			
			if color or width:
				if not resultStyle: resultStyle = {}
				if color:
					resultStyle["stroke"] = color
					#resultStyle["strokeOpacity"] = strokeOpacity
				if width: resultStyle["strokeWidth"] = width

		# process PolyStyle
		polyStyle = styleNode.getElementsByTagName("PolyStyle")
		if len(polyStyle):
			polyStyle = polyStyle[0]
			# color
			color = polyStyle.getElementsByTagName("color")
			if len(color):
				color = color[0].firstChild.data.encode("utf-8")
				fillOpacity = int(color[0]+color[1], 16)/255.
				# convert to rrggbb
				color = "#"+color[6]+color[7]+color[4]+color[5]+color[2]+color[3]
				if not resultStyle: resultStyle = {}
				resultStyle["fill"] = color
				resultStyle["fillOpacity"] = fillOpacity

	return resultStyle