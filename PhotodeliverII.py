#!/usr/bin/python3

''' This script moves camera file-media to a folder on our hard disk.
	it will group files in foldes due to its date of creation '''

# Module import
import sys, os, shutil, logging, datetime, time, re
from glob import glob
from gi.repository import GExiv2  # Dependencies: gir1.2-gexiv2   &   python-gobject


# ================================
# =========  Utils ===============
# ================================

def itemcheck(a):
	if os.path.isfile(a):
		return 'file'
	if os.path.isdir(a):
		return 'folder'
	if os.path.islink(a):
		return 'link'
	return ""


def to2(month):
	if month > 9:
		strmonth = str(month)
	else:
		strmonth = "0" + str(month)
	return strmonth

# Variable definition >>>>>>>>

# Load user config:
# Getting user folder to place log files....
userpath = os.path.join(os.getenv('HOME'),".Photodeliver")
userfileconfig = os.path.join(userpath,"Photodelivercfg.py")
if itemcheck (userpath) != "folder":
	os.makedirs(userpath)

if itemcheck (userfileconfig) == "file":
	print ("Loading user configuration....")
	sys.path.append(userpath)
	import Photodelivercfg
else:
	print ("There isn't an user config file: " + userfileconfig)
	# Create a new config file
	f = open(userfileconfig,"w")
	f.write ('''
# Photodeliver Config file.
# This options can be overriden by entering a command line options
# This is a python file. Be careful and see the sintaxt.

originlocation = '%(home)s/originlocation'  #  Path from where retrieve new images.
destination = '%(home)s/destlocation'  # 'Path to where you want to store your photos'
renamemovies = True  # This option adds a creation date in movies file-names (wich doesn't have Exif Metadata)
renamephotos = True  # This option adds a creation date in media file-names (useful if you want to modify them)
eventminpictures = 8  # minimum number of pictures to assign a day-event
gap = 60*60*5  # number of seconds between shots to be considered both pictures to the same event.
copymode = 'm'  # 'c' for copy or 'm' to move new files
considerdestinationitems = True  # Consider destination items in order to group media files in events.
moveexistentfiles = False  # True / False ...... True for move/reagroup or False to keep existent files at its place (Do nothing).
ignoreTrash = True  # True / False .... Ignore paths starting with '.Trash'
preservealbums = True  #  True / False  .... Do not include in fileScanning albums. An album is defined by a path that ends in _  pex.  /2015/2015 my album to preserve_/items.png 
forceassignfromfilename = True  # True / False   .... Force assign from a date found from filename if any. (This allows to override EXIF assignation if it is found).
cleaning = True  # True / False .....  Cleans empty folders (only folders that had contained photos)
latestmediagap = 6*30*24*60*60  # Seconds from 'now' to consider that item is one of the lattest media. You can override interact with this media.
donotmovelastmedia = True  # True / False ..... True means that the new lattest media will not be moved from its place.
filterboost = True  # True / False .......  True means that only consider destination folders that contains in its paths one of the years that have been retrieved from origin files. So it boost destination media scanning by filtering it.
'''%{'home':os.getenv('HOME')}
	)
	f.close()
	print ("An user config file has been created at:", userfileconfig)
	print ("Please customize by yourself before run this software again.")
	print ("This software is going to try to open with a text editor (gedit).")
	os.system ("gedit " + userfileconfig)
	exit()

# Getting variables.
originlocation = Photodelivercfg.originlocation  #  Place from where retrieve media
destination =  Photodelivercfg.destination  #  Place to store files once procesed
renamemovies = Photodelivercfg.renamemovies  # This option adds a creation date in movies file-names (wich doesn't have Exif Metadata)
renamephotos = Photodelivercfg.renamephotos  # This option adds a creation date in media file-names
eventminpictures = Photodelivercfg.eventminpictures  # minimun number of pictures to assign a day-event
gap = Photodelivercfg.gap  # number of seconds between shots to be considered both pictures to the same event.
copymode = Photodelivercfg.copymode  # 'c' for copy or 'm' to move new files
considerdestinationitems = Photodelivercfg.considerdestinationitems  # Consider destination items in order to group media files in events.
moveexistentfiles = Photodelivercfg.moveexistentfiles  # True for move/reagroup or False to keep existent files at its place (Do nothing).
ignoreTrash = Photodelivercfg.ignoreTrash  # Ignore paths starting with '.Trash'
preservealbums = Photodelivercfg.preservealbums  #  True / False  .... Do not include in fileScanning albums. An album is defined by a path that ends in _  pex.  /2015/2015 my album to preserve_/items.png 
forceassignfromfilename = Photodelivercfg.forceassignfromfilename  #  True / False   .... Force assign from a date found from filename if any. (This allows to override EXIF assignation if it is found).
cleaning = Photodelivercfg.cleaning  # Cleans empty folders (only folders that had contained photos)
latestmediagap = Photodelivercfg.latestmediagap  # Amount in seconds since 'now' to consider a media-file is one of the latest 
donotmovelastmedia = Photodelivercfg.donotmovelastmedia  # Flag to move or not move the latest media bunch.
filterboost = Photodelivercfg.filterboost

# Checking parameters to override user preferences.
# TO DO


# Internal variables.
moviesmedia = ['mov','avi','m4v', 'mpg', '3gp', 'mp4']
wantedmedia = ['jpg','jpeg','raw','png'] + moviesmedia
dummy = False  #  True / False   __  When True Do not perform any file movements. Play on dummy mode.
justif = 20  #  number of characters to justify logging info.


# ===============================
# The logging module.
# ===============================
loginlevel = 'DEBUG'
logpath = './'
logging_file = os.path.join(logpath, 'Photodeliver.log')


# Getting current date and time
now = datetime.datetime.now()
today = "/".join([str(now.day), str(now.month), str(now.year)])
tohour = ":".join([str(now.hour), str(now.minute)])

print ("Loginlevel:", loginlevel)
logging.basicConfig(
	level = loginlevel,
	format = '%(asctime)s : %(levelname)s : %(message)s',
	filename = logging_file,
	filemode = 'w'  # a = add
)
print ("logging to:", logging_file)


# Starting log file
logging.info("======================================================")
logging.info("================ Starting a new sesion ===============")
logging.info("======================================================")
logging.info('From:' + originlocation)
logging.info('  To:' + destination)


# Check inconsistences
if originlocation != '':
	if itemcheck(originlocation) != 'folder':
		print('Source folder does not exist')
		logging.critical('Source folder does not exist')
		print ('Exitting....')
		exit()
else:
	if moveexistentfiles == True :
		print ('Origin location have been not entered, this will reagroup destination items.')
		logging.info ('No origin location entered: Reagrouping existent pictures')
	else:
		print ('No origin location was introduced, and you do not want to reagroup existent items.')
		print ('Exitting....')
		logging.critical ('No origin location was introduced, and no interaction was selected.')
		exit()

if itemcheck(destination) != 'folder':
	print('Destination folder does not exist')
	logging.critical('Source folder does not exist')
	print ('Exitting....')
	exit()


def lsdirectorytree( directory = os.getenv( 'HOME')):
	""" Returns a list of a directory and its child directories

	usage:
	lsdirectorytree ("start directory")
	By default, user's home directory"""
	#init list to start
	dirlist = [directory]
	#setting the first scan
	moredirectories = dirlist
	while len(moredirectories) != 0:
		newdirectories = moredirectories
		#reset flag to 0; we assume from start, that there aren't child directories
		moredirectories = []
		# print ('\n\n\n','nueva iteración', moredirectories)
		for a in newdirectories:
			# checking for items (child directories)
			# print ('Checking directory', a)
			añadir = addchilddirectory(a)
			#adding found items to moredirectories
			for b in añadir:
				moredirectories.append(b)
		#adding found items to dirlist
		for a in moredirectories:
			dirlist.append(a)
	return dirlist


def addchilddirectory(directorio):
	""" Returns a list of child directories

	Usage: addchilddirectory(directory with absolute path)"""
	paraañadir = []
	ficheros = os.listdir(directorio)
	#print ('ficheros encontrados en: ',directorio, ':\n' , ficheros, '\n')
	for a in ficheros:
		item = os.path.join(directorio, a)
		#check, and if directory, it's added to paths-list
		if os.path.isdir(item):
			# print('Directory found: '+ item)
			# print('Añadiendo elemento para escanear')
			paraañadir.append(item)
	# print ('este listado hay que añadirlo para el escaneo: ', paraañadir)
	return paraañadir


class mediafile:
	""" This Class objet represents a media file.
	It is initialized by passing file related absolute path as argument.

	atributes:
		<related to file>
		self.abspath:	file absolute path (str)
		self.filename:	filename without extension (str)
		self.fileext:	filename extension (str)
		self.fileTepoch:Time since Epoch of file creation (stat)
		self.filebytes:	file-lenght in bytes

		self.imdateserial: True / False  Means that filename has a full date in its filename
		self.imserie:	serie clasification (IMG, PICT, \tfulldate, \tnoserial)
		self.imserial:	serial number, number cast into a string ( 0002, 0001 ..... )
		self.serialtype = 'filename'

		self.fnyear:	year (date of file creation from filename)
		self.fnmonth:	month (date of file creation from filename)
		self.fnday:		day (date of file creation from filename)
		self.fnhour:	hour (date of file creation from filename)
		self.fnmin:		minutes (date of file creation from filename)
		self.fnsec:		seconds (date of file creation from filename)
		self.fnDateTimeOriginal: Creation date-time retrieved from filename)

		<related to metadata>

		self.ImageModel:	Camera model
		self.ImageMake:		Camera Vendor
		self.DateTimeOriginal:	Cration date-time  YYYY:MM:DD HH:mm:SS

		self.mtyear:	year (date retrieved from metadata)
		self.mtmonth:	month (date retrieved from metadata)
		self.mtday:		day (date retrieved from metadata)
		self.mthour: 	hour (date retrieved from metadata)
		self.mtmin:		min (date retrieved from metadata)
		self.mtsec:		seconds (date retrieved from metadata)
		self.camera:	camera model (retrieved from metadata)

		<related to the class>
		self.TimeOriginal:	media creation time
		self.TimeSinceEpoch:	media creation time (Since Epoch)


	"""

	def __init__(self, abspath):
		self.abspath = abspath
		self.filename, self.fileext = os.path.splitext (os.path.basename (self.abspath))
		self.fileext = self.fileext.lower()
		self.fileTepoch = os.path.getmtime (self.abspath)
		# Fetch file long in bytes
		self.filebytes = os.path.getsize(self.abspath)
		logging.info ('## item: '+ self.abspath)
		logging.info ('fileTepoch (from Stat): '.ljust( justif ) + str(self.fileTepoch))
		# Fetch serie and serial number if any
		self.__imageserie__(self.filename)
		# Fetch image metadata (if any) 
		self.__imagemetadata__()
		# Decide creation time
		self.__decidecreationtime__()

	def __imageserie__(self, i):
		""" Gets a serial number from the filename
		Try to retrieve the date of creation from file name / path

		"""
		self.imdateserial = False  # 
		self.imserie = ''
		self.imserial = ''
		self.serialtype = 'filename'
		self.fnDateTimeOriginal = None  # From start we asume that there is not a full date-time in file's name
		sf = False  # serial number flag, True if some serial number if found
		# Date
		# We are going to collect information about dates of creation. from the less to the most.
		# Try to find some date structure in folder paths. (abspath)
		''' Fetch dates from folder structure, this prevents losing information if exif metadata 
		doesn't exist. Metada can be lost if you modify files with software. It is also usefull 
		if you move video files (wich doesn't have exif metadata) among cloud services. 
		Pej. you can store a folder structure in your PC client dropbox, and you'll lose your "stat" date,
		 but you can always recover it from file name/path.
		Structures:
			Years:
				one of the path-folder starts as a year number with four numbers
					[12]\d{3}    YYYY

			Months:
				one of the path folders is a month numbers

			Combos:
				one of the path folders is YYYY-MM

			Full date:
				there is a full-date structure on the path.
				2015-01-04 | 2015_01_04 | 2015:01:04 | 2015 01 04

			The day, hour-minutes and seconds asigned are 01, 12:00:00 + image serial number (in seconds) for each image to preserve an order.
			'''
		# Getting paths in a list to evaluate dates.
		## Cutting main tree from fullpaths.
		if self.abspath.startswith (originlocation):
			branch = self.abspath[ len ( originlocation ):]
		else:
			branch = self.abspath[ len ( destination ):]
		pathlevels = os.path.dirname (branch).split ('/')
		# Removig not wanted slashes
		if '' in pathlevels:
			pathlevels.remove('')
		logging.info ('Found directories levels: '+str(pathlevels))
		# Starting variables. From start, we assume that there is no date at all.
		self.fnyear = None
		self.fnmonth = None
		self.fnday = '01'
		self.fnhour = '12'
		self.fnmin = '00'
		self.fnsec = '00'
		# C1 - /*Year*/ /month/ /day/ in pathlevels (year must be detected from an upper level first)
		for word in pathlevels:
				#possible year is a level path:
			expr = "(?P<year>[12]\d{3})"
			mo = re.search(expr, word)
			try:
				mo.group()
			except:
				pass
			else:
				self.fnyear = mo.group ('year')
				logging.info( 'found possible year in'+'/'+word+'/'+':'+self.fnyear)
				continue

					#possible month is a level path:
			if len (word) == 2 and word.isnumeric () and self.fnyear != None:
				if int(word) in range(1,13):
					self.fnmonth = word
					logging.info( 'found possible month in'+'/'+word+'/'+':'+self.fnmonth)
					continue

					#possible day is a level path:
			if len (word) == 2 and word.isnumeric () and (self.fnyear != None and self.fnmonth != None):
				if int(word) in range(1,32):
					self.fnday = word
					loggç.info( 'found possible day in'+'/'+word+'/'+':'+self.fnday)
					continue

		# C2 (Year-month)
		expr = "(?P<year>[12]\d{3})[-_ /]?(?P<month>[01]\d)"
		mo = re.search(expr, self.abspath)
		try:
			mo.group()
		except:
			pass
		else:
			if int (mo.group('month')) in range (1,13):
				self.fnyear = mo.group ('year')
				self.fnmonth = mo.group ('month')
				logging.info( 'found possible year-month in'+self.abspath+':'+self.fnyear+" "+self.fnmonth)

		# C3: (Year-month-day)
		expr = "(?P<year>[12]\d{3})[-_ /]?(?P<month>[01]\d)[-_ /]?(?P<day>[0-3]\d)"
		mo = re.search(expr, self.abspath)
		try:
			mo.group()
		except:
			pass
		else:
			if int (mo.group('month')) in range (1,13) and int (mo.group ('day')) in range (1,32):
				self.fnyear = mo.group ('year')
				self.fnmonth = mo.group ('month')
				self.fnday = mo.group ('day')
				logging.info( 'found possible year-month-day in' + self.abspath + ':' + self.fnyear + " " + self.fnmonth + " " + self.fnday)


		# C4: YYYYMMDD-HHMMSS  in filename
		expr = '(?P<year>[12]\d{3})(?P<month>[01]\d)(?P<day>[0-3]\d)[-_ ]?(?P<hour>[012]\d)(?P<min>[0-5]\d)(?P<sec>[0-5]\d)'
		mo = re.search (expr, i)
		try:
			mo.group()
		except:
			logging.debug ("expression %s Not found in %s" %(expr, i))
			pass
		else:			
			self.fnyear  = mo.group ('year')
			self.fnmonth = mo.group ('month')
			self.fnday   = mo.group ('day')
			self.fnhour  = mo.group ('hour')
			self.fnmin   = mo.group ('min')
			self.fnsec   = mo.group ('sec')
			logging.info ( 'found full date identifier in ' + i)
			logging.debug ( i + " : " + " ".join( [mo.group('year'), mo.group('month'), mo.group('day'), mo.group('hour'), mo.group('min'), mo.group('sec') ]))
			if forceassignfromfilename == True:
				assignfromfilename = True
			if mo.start() == 0 :
				logging.debug ('filename starts with a full date identifier: '+ i )
				self.imdateserial = True  #  True means that filename starts with full-date serial in its name (item will not add any date in his filename again)


		# setting creation date
		if self.fnyear != None and self.fnmonth != None:
			textdate = '%s:%s:%s %s:%s:%s'%(self.fnyear, self.fnmonth, self.fnday, self.fnhour, self.fnmin, self.fnsec)
			logging.info ('This date have been retrieved from the file-path-name: ' + textdate )
			self.fnDateTimeOriginal = textdate

		# Serial number
		seriallist = ['WA[-_ ]?[0-9]{4}',
						'IMG[-_ ]?[0-9]{4}',
						'PICT[-_ ]?[0-9]{4}',
						'MVI[-_ ]?[0-9]{4}'
						]
		serialdict = { seriallist[0]: '(?P<se>WA)[-_ ]?(?P<sn>[0-9]{4})',
						seriallist[1] : '(?P<se>IMG)[-_ ]?(?P<sn>[0-9]{4})',
						seriallist[2] : '(?P<se>PICT)[-_ ]?(?P<sn>[0-9]{4})',
						seriallist[3] : '(?P<se>MVI)[-_ ]?(?P<sn>[0-9]{4})'}
		sf = False
		for expr in seriallist :
			mo = re.search (expr, i)
			try:
				mo.group()
			except:
				logging.debug ("expression %s Not found in %s" %(expr, i))
				continue
			else:
				mo = re.search ( serialdict[expr], i)
				logging.info ("expression %s found in %s" %(expr, i))
				sf = True
				break

		# setting serie and serial number
		if sf == True:
			self.imserie  = mo.group ('se')
			self.imserial = mo.group ('sn')
		else:
			self.imserie  = '\tnoserial'
			self.imserial = ''	
		logging.info ( 'Item serie and serial number (' + i + '): '+ self.imserie + ' ' +  self.imserial)

	def __imagemetadata__(self):
		self.DateTimeOriginal = None
		if self.fileext not in ['.jpg', '.jpeg', '.raw', '.png']:
			return
		metadata = GExiv2.Metadata(self.abspath)
		#metadata.read() # delete this line
		
		self.ImageModel = self.__readmetadate__( metadata ,'Exif.Image.Model')
		self.ImageMake = self.__readmetadate__( metadata ,'Exif.Image.Make')
		self.DateTimeOriginal = self.__readmetadate__( metadata ,'Exif.Photo.DateTimeOriginal')
		if self.DateTimeOriginal == None:
			self.DateTimeOriginal = self.__readmetadate__( metadata ,'Exif.Photo.DateTimeDigitized')
			if self.DateTimeOriginal == None:
				self.DateTimeOriginal = self.__readmetadate__( metadata ,'Exif.Image.DateTime')
				if self.DateTimeOriginal == None: return

		mo = re.search ( '(?P<year>[12]\d{3}):(?P<month>[01]\d):(?P<day>[0-3]\d) (?P<hour>[012]\d):(?P<min>[0-5]\d):(?P<sec>[0-5]\d)', self.DateTimeOriginal)

		self.mtyear  = mo.group ('year')
		self.mtmonth = mo.group ('month')
		self.mtday   = mo.group ('day')
		self.mthour  = mo.group ('hour')
		self.mtmin   = mo.group ('min')
		self.mtsec   = mo.group ('sec')

	def __readmetadate__ (self, metadata, exif_key):
		metadate = metadata.get(exif_key)
		if metadate == None:
			logging.info ('No '+ exif_key + 'in item: '+ self.abspath)
		else:
			logging.info (exif_key + ' found in: '+ self.abspath +' ('+metadate+')')
			print (exif_key, ':', metadate)
		return metadate

	def __decidecreationtime__ (self):
		''' Decide and assign the right media cration time due to:

		its metadata
		<path/file name>
		from stat

		'''
		self.TimeOriginal = None # From start we assign None if no matches are found.

		# Set Creation Date from Metadata if it is found,
		if self.DateTimeOriginal != None :
			self.TimeOriginal = time.strptime (self.DateTimeOriginal, '%Y:%m:%d %H:%M:%S')
			self.TimeSinceEpoch = time.mktime (self.TimeOriginal)
			logging.info ('Image Creation date has been set from image metadata: ' + str(time.asctime(self.TimeOriginal)))
			if forceassignfromfilename == False :
				return

		# Set Creation Date extracted from filename/path
		if self.fnDateTimeOriginal != None :
			self.TimeOriginal = time.strptime (self.fnDateTimeOriginal, '%Y:%m:%d %H:%M:%S')
			self.TimeSinceEpoch = time.mktime (self.TimeOriginal)
			logging.info ('Image Creation date has been set from File path / name: '+ str(time.asctime(self.TimeOriginal)))
			return

		# Set Creation Date from stat file.
		'''
		(You only should use this if you have those pictures in the original media storage
		without modifications and you want to read it directly from the media. or
		The files have copied among filesystem that preserves the file creation date, usually ext3 ext4, NTFs, or MacOSx filesystems.
		See file properties first and ensure that you can trust this fact. Anyway, the file only will be processed
		if in its path is the word DCIM.)
			'''
		if self.abspath.find('DCIM') != -1:
			self.TimeOriginal = time.gmtime (self.fileTepoch)
			self.TimeSinceEpoch = time.mktime (self.TimeOriginal)
			logging.info ( "Image Creation date has been set from File stat" )
			return

		if self.TimeOriginal == None:
			self.TimeSinceEpoch = None
			logging.info ( "Can't guess Image date of Creation" )


def mediascan(location, filteryears=''):
	# 1.1) get items dir-tree
	listree = lsdirectorytree (location)

	# 1.2) get a list of media items and casting into a class
	itemlist = list()

	for d in listree:
		add = list ()
		for ext in wantedmedia:
			add += glob(os.path.join(d,'*.'+ ext.lower()))
			add += glob(os.path.join(d,'*.'+ ext.upper()))
		itemlist += add


	if len (itemlist) == 0:
		logging.warning ('Thereis nothing to import at ' + location)
		return '',''

	# casting items classes into a list.
	itemsclasslist = list()
	rangeyears = set()
	for i in itemlist:
		if ignoreTrash == True : 
			if i.find ('.Trash') != -1 :
				logging.info ('Item %s was not included (Trash folder)' %(i) )
				continue
			if i.find ('.thumbnails') != -1 :
				logging.info ('Item %s was not included (Thumbnails folder)' %(i) )
				continue
		if preservealbums == True :
			if i.find ('_/') != -1 :
				logging.info ('Item %s was not included (Preserving album folder)' %(i) )
				continue
		if filterboost == True :
			include = False	
			if len (filteryears) > 0 :
				for a in filteryears:
					if "/"+a+"/" in i:
						include = True
				if include == False:
					logging.info ('Item %s was not included. Out of filter-year range ' %(i) )
					continue
		item = mediafile(i)
		itemsclasslist.append (item)
		if item.TimeOriginal != None:
			rangeyears.add (time.strftime('%Y', item.TimeOriginal))
		print (i, rangeyears)
	return itemsclasslist, rangeyears

# ===========================================
# ========= Main module =====================
# ===========================================

assignfromfilename = False

# 1) Get items
# 1.1) Get origin location

itemscl = ''
if originlocation != '' :
	itemscl, originyears = mediascan (originlocation)
	if itemscl == '':
		print ('Nothing to scan at origin location (', originlocation)
		logging.info ('Thereis nothing to import at origin location: ' + originlocation)
		logging.warning ('Deactivating filterboost')
		originyears = ''
		filterboost = False


itemscle = ''
if considerdestinationitems == True:
	itemscle, destinationyears = mediascan (destination, originyears)
	if itemscle == '':
		print ('Nothing to scan at destination location (', destination, ')')
		logging.info ('Thereis nothing to import at destination location: ' + destination)

if len (itemscl) + len (itemscle) == 0:
	print ('Nothing to import / reagroup.')
	logging.info ('Thereis nothing to import or reagroup, exitting....')
	exit()

logging.info ('%s new files scanned.' %(len (itemscl)))
logging.info ('%s existent files scanned.' %(len (itemscle)))


# 1.3) ordering list items into a new list.
AllCreationtimes = list()
if itemscl != '' and  itemscle != '':
	Allitemscl = itemscl + itemscle
elif itemscl != '' :
	Allitemscl = itemscl
else:
	Allitemscl = itemscle

print ('len Allitemscl', len(Allitemscl))
for i in Allitemscl:
	print ('Time Since Epoch:', i.TimeSinceEpoch)
	if i.TimeSinceEpoch != None:
		AllCreationtimes.append ( i.TimeSinceEpoch )

# 2) Setting flags for each file.
AllCreationtimes.sort()  # All TimeSinceEpoch times sorted
itemdict = dict ()  # our dict for deliver paths. Corresponds TimeSinceEpoch <> earliest event
itemsdayflag = dict ()  # our group counter, if true

# groups shoots in "gaps" assigning the earliest day of the group.
# this will assign for each Epochtime an Epochtime wich is the earliest groups of shoots!
# float-event changes when next shoot is far away from our 'gap'.


# Initializing first element.
floatevent = AllCreationtimes [0]
itemdict[AllCreationtimes[0]] = floatevent
itemsdayflag [floatevent] = 1

ct = 0
for t in AllCreationtimes:
	ct += 1 # counter to fetch next element.
	if ct >= len (AllCreationtimes): # So we check the next element, we do not want to check out of the list range.
		break

	if AllCreationtimes [ct] - t > gap:
		# new event
		floatevent = AllCreationtimes [ct]
	
	itemdict[AllCreationtimes[ct]] = floatevent # we set an "floatevent" for every Epoch-item-Time

	if itemsdayflag.get (floatevent) == None:
		itemsdayflag [floatevent] = 0
	itemsdayflag [floatevent] = itemsdayflag.get (floatevent) + 1


#3) Deliver items
for i in Allitemscl:
	event = False
	eventname = ''
	a = i.abspath  # item's fullpath and filename
	if i.TimeOriginal == None:
		dest = os.path.join(destination, "nodate", os.path.basename(a))

	else:
		# Check origin dir Structure for an already event name
		expr = "/[12]\d{3}[-_ ]?[01]\d[-_ ]?[0-3]\d ?(?P<XeventnameX>.*)/"
		mo = re.search(expr, a)
		try:
			mo.group()
		except:
			pass
		else:
			# retrieve the name & set Even-Flag to True
			eventname = mo.group('XeventnameX')
			event = True
			logging.debug( 'found an origin event name in: %s (%s)' %(a, eventname))

		# Getting a possible event day
		itemcreation = i.TimeOriginal
			# deliver
		if event == True or (itemsdayflag [ itemdict[i.TimeSinceEpoch] ] >= eventminpictures ):
			#destination includes a day - event
			dest = os.path.join(destination, str(itemcreation.tm_year), '-'.join([str(itemcreation.tm_year), to2(itemcreation.tm_mon), to2(itemcreation.tm_mday)]), os.path.basename(a))
			event = True
		else:
			#destination only includes a month (go to a various month-box)
			dest = os.path.join(destination,str(itemcreation.tm_year), '-'.join([str(itemcreation.tm_year), to2(itemcreation.tm_mon)]), os.path.basename(a))
		# set date information in filename if it is a movie.
		if ((renamemovies == True and i.fileext.lower()[1:] in moviesmedia) or ( renamephotos == True and i.fileext.lower()[1:] in wantedmedia)) and i.imdateserial != True :
			dest = os.path.join(os.path.dirname(dest), time.strftime('%Y%m%d_%H%M%S', itemcreation ) + "-" + os.path.basename(dest) )

	# Reagroup existent items if necessary
	finalcopymode = copymode
	#if itemscle != '':
	if i.abspath.startswith(destination):
		# Existent items.
		if moveexistentfiles == True:
			finalcopymode = 'm'
		else:
			continue
	
	elif donotmovelastmedia == True and ((time.time () - i.TimeSinceEpoch) < latestmediagap) : 
		logging.info ('Doing nothing with this file, is inthe gap of the latest files and donotmovelastmedia is set to True.' + a)
		continue
		
	# 
	if event == True:
		destcheck = os.path.dirname(dest)  # Check destination dir structure ../../aaaa/aaaa-mm-dd*
		levents = glob(destcheck + '*')
		if len (levents) != 0 :
			# (Get event path as existing path for destination)
			dest = os.path.join(levents.pop(), os.path.basename(dest))
		else:
			if eventname != '':
				eventname = " "+ eventname
			dest = os.path.join(os.path.dirname(dest) + eventname, os.path.basename(dest) )
			# dest = os.path.join(___XXXX____ , os.path.basename(dest))
			# Conformar el nuevo destino con el nombre del evento.

	# Perform file operations
	if a == dest :
		print ('the file does not need to be moved:', a)
		logging.warning('this file remains at the same location:'+dest)
	else:		
		if itemcheck (os.path.dirname(dest)) == '':
			if dummy == False:
				os.makedirs (os.path.dirname(dest))
		if itemcheck (dest) == '':
			if finalcopymode == 'm' :
				if dummy == False:
					shutil.move (a, dest)
				print ('FILE MOVED:', a, dest)
				logging.info('file successfully moved: '+ dest)
				# Clening empty directories
				if cleaning == True:
					scandir = os.path.dirname (a)
					contents = glob (os.path.join(scandir,'*'))
					print (contents)
					if len (contents) == 0 and scandir != os.path.normpath(originlocation):
						if dummy == False:
							shutil.rmtree (scandir)
						print ('\n','deleting dir:', scandir,'\n')
						logging.info ('Directory %s has been deleted (was empty)'%(a,))
			else:
				if dummy == False:
					shutil.copy (a, dest)
				print ('FILE COPIED:', a, dest)
				logging.info('file successfully copied: '+ dest)
		else:
			print ('destination for this item already exists', a)
			logging.warning('destination item already exists:'+dest)

# 4) check empty directories, cleaning ones.
