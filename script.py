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
			if verbose == "true":
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
			if verbose == "true":
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
	if verbose == "true":
		print "***********************EXECUTING FIELDS***********************"
	execute(fidx, fields)
	if verbose == "true":
		print "***********************EXECUTING WEBLINKS***********************"
	execute(widx, webLinks)
	if verbose == "true":
		print "***********************EXECUTING RECORDTYPES***********************"
	execute(rtidx, recordTypes)
	if verbose == "true":
		print "***********************EXECUTING VALIDATIONRULES***********************"
	execute(vidx, validationRules)
	if verbose == "true":
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
					if verbose == "true":
						print "XML already contains element", fileName
					contains = "true"
		if contains == "false":
			if verbose == "true":
				print("adding new element " + newMember.text)
			root[idx].insert(0, newMember)
			if(dryRun == "false"):
				global path
				tree.write(path)

def removeElement(f):
	fileName, fileExtension = os.path.splitext(f)
	directory = rev_extensions[fileExtension]
	idx = directories[directory]
	removed = "false"
	for node in root[idx]:
		#Remove from XML
		if removed == "false":
			if node.text == fileName:
				if verbose == "true":
					print("removing element " + node.text)
				root[idx].remove(node)
				removed = "true"
				if(dryRun == "false"):
					global path
					tree.write(path)

def deleteObj(idx, list):
	for item in list:
		for node in root[idx]:
			if node.text == item:
				#Remove from XML
				print("removing element " + node.text)
				root[idx].remove(node)


def helperAddRemoveElementObject(idx, list, option):
	if(option == "remove"):
		deleteObj(idx, list)
	else:
		iterateList(idx, list)
	if(dryRun == "false"):
		global path
		tree.write(path)

def addRemoveElementObject(f, option):
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
	global rootDir
	path = rootDir + directory + '/' + f
	t = ET.parse(path)
	r = t.getroot()
	for elem in r.findall("./"):
		for fn in elem.findall("./"):
			if "fullName" in fn.tag:
				(name, ext) = os.path.splitext(f)
				item = name + '.' + fn.text
				#print "name: ", name, "fn.text: ", fn.text
				if "fields" in elem.tag:
					print "adding", item, "to fields"
					fields.append(item)
				elif "webLinks" in elem.tag:
					webLinks.append(item)							
				elif "recordTypes" in elem.tag:		
					recordTypes.append(item)							
				elif "validationRules" in elem.tag:
					validationRules.append(item)
	if verbose == "true":
		print "***********************EXECUTING FIELDS***********************"
	helperAddRemoveElementObject(fidx, fields, option)
	if verbose == "true":
		print "***********************EXECUTING WEBLINKS***********************"
	helperAddRemoveElementObject(widx, webLinks, option)
	if verbose == "true":
		print "***********************EXECUTING RECORDTYPES***********************"
	helperAddRemoveElementObject(rtidx, recordTypes, option)
	if verbose == "true":
		print "***********************EXECUTING VALIDATIONRULES***********************"
	helperAddRemoveElementObject(vidx, validationRules, option)
	if verbose == "true":
		print "***********************EXECUTING CUSTOMOBJECT***********************"		
	idx = directories[directory]
	helperAddRemoveElementObject(idx, list, option)

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
			elif(arg == "-root"):
				global rootDir
				idx += 1
				rootDir = sys.argv[idx]
				idx += 1
			elif(arg == "-help"):
				helpMessage()
				idx += 1
			elif(arg == "-verbose"):
				global verbose
				verbose = "true"
				idx += 1
			else:
				print "One or more invalid flags. Use the -help flag for more information.\n"
				idx += 1

def execute(idx, list):
	if root[idx][0].text == "*":
		print "Type contains member *"
	else:	
		iterateXML(idx, list)
		iterateList(idx, list)
		if(dryRun == "false"):
			global path
			tree.write(path)

def prependXmlDeclaration():
	string = '<?xml version="1.0" encoding="UTF-8"?>\n'
	global path
	f=open(path, 'r+')
	firstLine = f.readline()
	if(not string in firstLine):
		f.seek(0)
		lines = f.readlines()
		f.seek(0)
		f.write(string)
		f.writelines(lines)
		f.close()

def helpMessage():
	print("\nFLAGS:\n"
		+ "-d specifies directory(s) to consider\n-a adds file(s) to the XML\n"
		+ "-r removes file(s) from the XML\n-root specifies a root location for the package.xml file\n"
		+ "-verbose includes extra information\n-dry declares it a dry run, where the XML file will not be modified\n"
		+ "Keep in mind that the package.xml file and the directory(s) must be in the same location.\n")
#***************************************MAIN PROGRAM***************************************
rootDir = ""
#-d
checkDirs = [] #list of directories to be compared with XML
#-a, -r, -dry
add = [] #list of files to add
remove = [] #list of files to remove
dryRun = "false" #dryRun mode does not modify XML file
verbose = "false"

parseArgs()

if rootDir != "":
	rootDir = rootDir + '/'
path = rootDir + "package.xml"
tree = ET.parse(path)
root = tree.getroot()

if(verbose == "true"):
	print "dry run:", dryRun
	print "checkDirs:", checkDirs
	print "add:", add
	print "remove:", remove

if(len(checkDirs)):
	if verbose == "true":
		print "Executing directories..."
	for directory in checkDirs:
		longDir = rootDir + directory
		if verbose == "true":
			print "[" + directory + "]"
		if directory == "objects":
			list = handleObjects(longDir)
		elif directory == "email":
			list = handleEmail(longDir)
		else:
			list = listFiles(longDir, extensions[directory])
		idx = directories[directory]
		execute(idx, list)

if(len(add)):
	if verbose == "true":
		print "\nExecuting adds..."
	for f in add:
		if ".object" in f:
			addRemoveElementObject(f, "add")
		else:
			addElement(f)

if(len(remove)):
	if verbose == "true":
		print "\nExecuting removes..."
	for f in remove:
		if ".object" in f:
			addRemoveElementObject(f, "remove")
		else:
			removeElement(f)

prependXmlDeclaration()