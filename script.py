import os
import sys
import xml.etree.ElementTree as ET

ET.register_namespace("","http://soap.sforce.com/2006/04/metadata")

#CustomLabel???
directories = {'classes': 0, 'pages': 1, 'triggers': 2, 'objects': 5, 'email': 6, 'layouts': 8, 'profiles': 9,
 'staticresources': 12, 'permissionsets': 13, 'translations': 14, 'tabs': 15, 'components': 16}

extensions = {'classes': '.cls', 'pages': '.page', 'triggers': '.trigger', 'objects': '.object', 'email': '.email', 'layouts': '.layout',
 'profiles': '.profile', 'staticresources': '.resource', 'permissionsets': '.permissionset', 'translations': '.translation',
 'tabs': '.tab', 'components': '.component'}

rev_extensions = dict((v,k) for k,v in extensions.iteritems())

objectsMap = {'fields': 3, 'validationRules': 7, 'recordTypes': 10, 'webLinks': 11}

#Gets a list of the files in the specified directory
def listFiles(dir, ext):
	list = []
	for file in os.listdir(dir):
		if file.endswith(ext):
			(name, ext) = os.path.splitext(file)
			list.append(name)
	return list

#Iterates through the XML, deleting extra elements (those that aren't in directory)
def iterateXML(idx, list):
	for node in root[idx]:
		if node.text not in list and not "name" in node.tag:
			#Remove from XML
			print("removing element " + node.text)
			root[idx].remove(node)

#Iterates through list, adding elements into XML as needed
def iterateList(idx, list):
	for elem in list:
		exist = "false"
		for xmlElem in root[idx]:
			if xmlElem.text == elem:
				exist = "true"
		if exist == "false":
			print("adding new element " + elem)
			newMember = ET.Element("members")
			newMember.text = elem
			#Add to XML
			root[idx].insert(0, newMember)

#Handles email specifically
def handleEmail(dir):
	list = []
	for directory in os.listdir(dir):
		print(directory)
		if not directory[:1] == '.':
			path = dir + '/' + directory
			item = directory + '/'
			#print "path:", path
			for file in os.listdir(path):
				if file.endswith('.email'):
					(name, ext) = os.path.splitext(file)
					file = item + name
					#print file
					list.append(file)
	return list

#Handles objects specifically
def handleObjects(dir):	
	#|list| will be the "regular" list, mapping to CustomObject
	list = []
	#these are the other lists
	fields = []
	webLinks = []
	recordTypes = []
	validationRules = []

	fidx = objectsMap["fields"]
	widx = objectsMap["webLinks"]
	rtidx = objectsMap["recordTypes"]
	vidx = objectsMap["validationRules"]

	for f in os.listdir(dir):
		if not f[:1] == '.':
			(name, ext) = os.path.splitext(f)
			list.append(name)
			path = dir + '/' + f
			t = ET.parse(path)
			r = t.getroot()
			for elem in r.findall("./"):
				for fn in elem.findall("./"):
					if "fullName" in fn.tag:
						#print elem.tag
						(name, ext) = os.path.splitext(f)
						item = name + '.' + fn.text
						#print "name: ", name, "fn.text: ", fn.text
						if "fields" in elem.tag:
							fields.append(item)
						elif "webLinks" in elem.tag:
							webLinks.append(item)							
						elif "recordTypes" in elem.tag:							
							recordTypes.append(item)							
						elif "validationRules" in elem.tag:
							validationRules.append(item)
	print "***********************EXECUTING FIELDS***********************"
	execute(fidx, fields)
	print "***********************EXECUTING WEBLINKS***********************"
	execute(widx, webLinks)
	print "***********************EXECUTING RECORDTYPES***********************"
	execute(rtidx, recordTypes)
	print "***********************EXECUTING VALIDATIONRULES***********************"
	execute(vidx, validationRules)
	print "***********************EXECUTING CUSTOMOBJECT***********************"
	return list


def addElement(f):
	fileName, fileExtension = os.path.splitext(f)
	directory = rev_extensions[fileExtension]
	newMember = ET.Element("members")
	newMember.text = fileName
	idx = directories[directory]
	contains = "false"
	#Add to XML if this type doesnt have member *
	if not root[idx][0].text == "*":
		for node in root[idx]:
			if contains == "false":
				if fileName == node.text:
					print "XML already contains element", fileName
					contains = "true"
		if contains == "false":
			print("adding new element " + newMember.text)
			root[idx].insert(0, newMember)
			if(dryRun == "false"):
				tree.write("package.xml")

def addElementObject(f):
	list = []

	fields = []
	webLinks = []
	recordTypes = []
	validationRules = []

	fidx = objectsMap["fields"]
	widx = objectsMap["webLinks"]
	rtidx = objectsMap["recordTypes"]
	vidx = objectsMap["validationRules"]

	fileName, fileExtension = os.path.splitext(f)
	list.append(fileName)
	directory = rev_extensions[fileExtension]
	path = directory + '/' + f
	t = ET.parse(path)
	r = t.getroot()
	for elem in r.findall("./"):
		for fn in elem.findall("./"):
			if "fullName" in fn.tag:
				#print elem.tag
				(name, ext) = os.path.splitext(f)
				item = name + '.' + fn.text
				#print "name: ", name, "fn.text: ", fn.text
				if "fields" in elem.tag:
					fields.append(item)
				elif "webLinks" in elem.tag:
					webLinks.append(item)							
				elif "recordTypes" in elem.tag:							
					recordTypes.append(item)							
				elif "validationRules" in elem.tag:
					validationRules.append(item)
	print "***********************EXECUTING FIELDS***********************"
	iterateList(fidx, fields)
	if(dryRun == "false"):
		tree.write("package.xml")
	print "***********************EXECUTING WEBLINKS***********************"
	iterateList(widx, webLinks)
	if(dryRun == "false"):
		tree.write("package.xml")
	print "***********************EXECUTING RECORDTYPES***********************"
	iterateList(rtidx, recordTypes)
	if(dryRun == "false"):
		tree.write("package.xml")
	print "***********************EXECUTING VALIDATIONRULES***********************"
	iterateList(vidx, validationRules)
	if(dryRun == "false"):
		tree.write("package.xml")
	print "***********************EXECUTING CUSTOMOBJECT***********************"		
	idx = directories[directory]
	iterateList(idx, list)
	if(dryRun == "false"):
		tree.write("package.xml")

def removeElement(f):
	fileName, fileExtension = os.path.splitext(f)
	directory = rev_extensions[fileExtension]
	idx = directories[directory]
	removed = "false"
	for node in root[idx]:
		#Remove from XML
		if removed == "false":
			if node.text == fileName:
				print("removing element " + node.text)
				root[idx].remove(node)
				removed = "true"
				if(dryRun == "false"):
					tree.write("package.xml")

#def removeElementObject():


def getArgs(idx, list):
	while(idx + 1 < len(sys.argv)):
		idx += 1
		arg = str(sys.argv[idx])
		firstChar = arg[:1]
		if(not firstChar == "-"):
			getattr(list, "append")(arg)
		else:
			return idx
	return idx + 1

def parseArgs():
	idx = 1
	num = len(sys.argv)
	while idx < num:
		arg = str(sys.argv[idx])
		firstChar = arg[:1]
		if(firstChar == "-"):
			if(arg == "-d"):
				idx = getArgs(idx, checkDirs)
			elif(arg == "-a"):
				idx = getArgs(idx, add)
			elif(arg == "-r"):
				idx = getArgs(idx, remove)
			elif(arg == "-dry"):
				global dryRun
				dryRun = "true"
				idx += 1
			else:
				idx += 1

def execute(idx, list):
	if root[idx][0].text == "*":
		print "Type contains member *"
	else:	
		iterateXML(idx, list)
		iterateList(idx, list)
		if(dryRun == "false"):
			tree.write("package.xml")
#***************************************MAIN PROGRAM***************************************
tree = ET.parse('package.xml')
root = tree.getroot()

#-d
checkDirs = [] #list of directories to be compared with XML
#-a, -r, -dry
add = [] #list of files to add
remove = [] #list of files to remove
dryRun = "false" #dryRun mode does not modify XML file

parseArgs()

print "dry run:", dryRun
print "checkDirs:", checkDirs
print "add:", add
print "remove:", remove

if(len(checkDirs)):
	print "Executing directories..."
	for directory in checkDirs:
		print "[" + directory + "]"
		if directory == "objects":
			list = handleObjects(directory)
		elif directory == "email":
			list = handleEmail(directory)
		else:
			list = listFiles(directory, extensions[directory])
		idx = directories[directory]
		#Checks to see if the type has *
		execute(idx, list)

if(len(add)):
	print "\nExecuting adds..."
	for f in add:
		if ".object" in f:
			addElementObject(f)
		else:
			addElement(f)

if(len(remove)):
	print "\nExecuting removes..."
	for f in remove:
		removeElement(f)