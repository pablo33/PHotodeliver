#!/usr/bin/python3

''' This script moves camera file-media to a folder on our hard disk.
	it will group files in foldes due to its date of creation 
	it also manages duplicated files (same name and bytes)'''

# Module import
import sys, os, shutil, logging, datetime, time, re
from glob import glob
import argparse  # for command line arguments
import sqlite3  # for sqlite3 Database management
 
import gi  # used to avoid Gi warning
gi.require_version('GExiv2', '0.10')  # user to avoid Gi warning
from gi.repository import GExiv2  # for metadata management. Dependencies: gir1.2-gexiv2   &   python-gobject
from PIL import Image  # for image conversion
from subprocess import check_output  # Checks if some process is accessing a file

# Internal variables.
os.stat_float_times (False)  #  So you won't get milliseconds retrieving Stat dates; this will raise in error parsing getmtime.
moviesmedia = ['mov','avi','m4v', 'mpg', '3gp', 'mp4']
photomedia = ['jpg','jpeg','raw','png','bmp']
wantedmedia =  photomedia + moviesmedia
justif = 20  #  number of characters to justify logging info.
dupfoldername = 'duplicates'

monthsdict = {
	"01" : ("enero", "ene", "juanuary", "jan"),
	"02" : ("febrero", "feb", "february"),
	"03" : ("marzo", "mar", "march"),
	"04" : ("abril", "abr", "april", "apr"),
	"05" : ("mayo", "may","may"),
	"06" : ("junio", "jun", "june"),
	"07" : ("julio", "jul", "july"),
	"08" : ("agosto", "ago", "agost"),
	"09" : ("septiembre", "sep", "set","september"),
	"10" : ("octubre", "oct", "october"),
	"11" : ("noviembre", "nov", "november"),
	"12" : ("diciembre", "dic", "december", "dec"),
	}

# ================================
# =========  Utils ===============
# ================================

# errors
class OutOfRangeError(ValueError):
	pass
class NotIntegerError(ValueError):
	pass
class NotStringError(ValueError):
	pass
class MalformedPathError(ValueError):
	pass
class EmptyStringError(ValueError):
	pass


def itemcheck(pointer):
	''' returns what kind of a pointer is '''
	if type(pointer) is not str:
		raise NotStringError ('Bad input, it must be a string')
	if pointer.find("//") != -1 :
		raise MalformedPathError ('Malformed Path, it has double slashes')
	
	if os.path.isfile(pointer):
		return 'file'
	if os.path.isdir(pointer):
		return 'folder'
	if os.path.islink(pointer):
		return 'link'
	return ""

def to2(month):
	''' Convert integers into a 2 digit  month string '''
	if type(month) is not int:
		raise NotIntegerError ('Only integers are addmited as input')
	if not (0 < month < 13):
		raise OutOfRangeError('Number out of range, must be a month')
	if month > 9:
		strmonth = str(month)
	else:
		strmonth = "0" + str(month)
	return strmonth

def addslash (text):
	''' Returns an ending slash in a path if it doesn't have one '''
	if type(text) is not str:
		raise NotStringError ('Bad input, it must be a string')

	if text == "":
		return text

	if text [-1] != '/':
		text += '/'
	return text

def readmetadate (metadata, exif_key):
	""" Gets a Metadata object and a tag name and returns its values
		Metadata object is retireved form GExiv2.Metadata('path/to/file')
		"""
	metadate = metadata.get(exif_key)
	if not (metadate == None or metadate.strip() == ''):
		logging.debug (exif_key + ' found:' + metadate)
	else:
		logging.debug ('No '+ exif_key + 'found.')
	return metadate

def addchilddirectory(directorio):
	""" Returns a list of child directories

	Usage: addchilddirectory(directory with absolute path)"""
	paraañadir = []
	ficheros = os.listdir(directorio)
	for a in ficheros:
		item = os.path.join(directorio, a)
		if os.path.isdir(item):
			paraañadir.append(item)
	return paraañadir

def lsdirectorytree( directory = os.getenv( 'HOME')):
	""" Returns a list of a directory and its child directories

	usage:
	lsdirectorytree ("start directory")
	By default, user's home directory

	Own start directory is also returned as result
	"""
	#init list to start, own start directory is included
	dirlist = [directory]
	#setting the first scan
	moredirectories = dirlist
	while len (moredirectories) != 0:
		newdirectories = moredirectories
		moredirectories = list ()
		for element in newdirectories:
			toadd = addchilddirectory(element)
			moredirectories += toadd
		dirlist += moredirectories
	return dirlist

def Nextfilenumber (dest):
	''' Returns the next filename counter as filename(nnn).ext
	input: /path/to/filename.ext
	output: /path/to/filename(n).ext
		'''
	if dest == "":
		raise EmptyStringError ('empty strings as input are not allowed')
	filename = os.path.basename (dest)
	extension = os.path.splitext (dest)[1]
	# extract secuence
	expr = '\(\d{1,}\)'+extension
	mo = re.search (expr, filename)
	try:
		grupo = mo.group()
	except:
		#  print ("No final counter expression was found in %s. Counter is set to 0" % dest)
		counter = 0
		cut = len (extension)
	else:
		#  print ("Filename has a final counter expression.  (n).extension ")
		cut = len (mo.group())
		countergroup = (re.search ('\d{1,}', grupo))
		counter = int (countergroup.group()) + 1
	if cut == 0 :
		newfilename = os.path.join( os.path.dirname(dest), filename + "(" + str(counter) + ")" + extension)
	else:
		newfilename = os.path.join( os.path.dirname(dest), filename [0:-cut] + "(" + str(counter) + ")" + extension)
	return newfilename

def enclosedyearfinder (string):
	""" searchs for a year string,
	it must return the year string if any or None if it doesn't
		"""
	if string.isnumeric():
		return string
	return None

def enclosedmonthfinder (string):
	""" Give a string, returns a string if it is a month number,
		otherwise it returns None,
		"""
	if len (string) == 2 and string.isnumeric ():
		if int(string) in range(1,13):
			logging.debug( 'found possible month in'+ string )
			return string
	for element in monthsdict:
		if string.lower() in monthsdict[element]:
			return element
	return None

def encloseddayfinder (string):
	""" Give a string, returns a string if it is a month number,
		otherwise it returns None,
		"""
	if len (string) == 2 and string.isnumeric ():
		if int(string) in range(1,32):
			logging.debug( 'found possible day in'+ string )
			return string
	return None

def yearmonthfinder (string):
	""" Given a string, returns a combo of numeric  year-month if it is found,
		otherwise returns None .
		"""
	expr = ".*(?P<year>[12]\d{3})[-_ /:.]?(?P<month>[01]?\d).*"
	mo = re.search(expr, string)
	try:
		mo.group()
	except:
		pass
	else:
		num_month = int(mo.group('month'))
		if num_month in range (1,13) :
			fnyear = mo.group ('year')
			fnmonth = '%02.0i'%num_month
			return fnyear, fnmonth
	return None, None

def yearmonthdayfinder (string):
	""" Given a string, returns a combo of numeric  year-month-day if it is found,
		otherwise returns None.
		"""

	expr = "(?P<year>[12]\d{3})[-_ /:.]?(?P<month>[01]?\d)[-_ /:.]?(?P<day>[0-3]?\d)"
	mo = re.search(expr, string)
	try:
		mo.group()
	except:
		pass
	else:
		num_month, num_day = int(mo.group('month')), int(mo.group('day'))
		if num_month < 13 and num_day < 32:
			print ( "num_month, num_day : ",num_month, num_day)
			fnyear = mo.group ('year')
			fnmonth = '%02.0i'%num_month
			fnday = '%02.0i'%num_day
			return fnyear, fnmonth, fnday
	return None, None, None

def fulldatefinder (string):
	""" Given a string, returns a combo of numeric YYYY-MM-DD-hh-mm-ss True if a full-date-identifier
		if found, otherwise returns None"""
	start = False
	sep = '[-_ :.]'
	expr = '(?P<year>[12]\d{3})%(sep)s?(?P<month>[01]?\d)%(sep)s?(?P<day>[0-3]?\d)%(sep)s?(?P<hour>[012]\d)%(sep)s?(?P<min>[0-5]\d)%(sep)s?(?P<sec>[0-5]\d)' %{'sep':'[-_ .:]'}
	mo = re.search (expr, string)
	try:
		mo.group()
	except:
		logging.debug ("expression %s Not found in %s" %(expr, string))
		pass
	else:
		num_month, num_day = int(mo.group ('month')), int(mo.group ('day'))
		year  = mo.group ('year')
		month = '%02.0i'%num_month
		day   = '%02.0i'%num_day
		hour  = mo.group ('hour')
		minute   = mo.group ('min')
		sec   = mo.group ('sec')
		if mo.start() == 0 :
			start = True
		return year, month, day, hour, minute, sec, start
	return None, None, None, None, None, None, None

def serieserial (string):
	''' given a filename string, it returns serie and serial number (tuple)
		otherwise it returns None'''

	sep = '[-_ ]'
	seriallist = ['WA','IMG','PICT','MVI','img']
	#seriallist = seriallist + seriallist.lower() for 
	for key in seriallist :
		expr = '(?P<se>%s%s?)(?P<sn>[0-9]{4})'%(key,sep)

		mo = re.search (expr, string)
		try:
			mo.group()
		except:
			logging.debug ("expression %s Not found in %s" %(expr, string))
			continue
		else:
			logging.debug ("expression %s found in %s" %(expr, string))
			imserie  = mo.group ('se')
			imserial = mo.group ('sn')
			logging.debug ( 'Item serie and serial number (' + string + '): '+ imserie + ' ' +  imserial)
			return imserie, imserial
	return None, None

def Fetchmetadata (imagepath):
	ImageModel, ImageMake, textdate = '','', None
	metadata = GExiv2.Metadata(imagepath)
	
	ImageMake = readmetadate( metadata ,'Exif.Image.Make')
	ImageModel = readmetadate( metadata ,'Exif.Image.Model')
	textdate = readmetadate( metadata ,'Exif.Photo.DateTimeOriginal')
	if textdate == None:
		textdate = readmetadate( metadata ,'Exif.Photo.DateTimeDigitized')
		if textdate == None:
			textdate = readmetadate( metadata ,'Exif.Image.DateTime')
	return ImageMake, ImageModel, textdate

def mediainfo (abspath, forceassignfromfilename):

	#1) Retrieve basic info from the file
	logging.debug ('## item: '+ abspath)
	filename, fileext = os.path.splitext(os.path.basename (abspath))
	Statdate = datetime.datetime.utcfromtimestamp(os.path.getmtime (abspath))
	filebytes = os.path.getsize(abspath)  # logging.debug ('fileTepoch (from Stat): '.ljust( justif ) + str(fileTepoch))
	fnDateTimeOriginal = None  # From start we assume a no date found on the file path

	#2) Fetch date identificators form imagepath, serie and serial number if any. 
	mintepoch = '1899'  # In order to discard low year values, this is the lowest year. 

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
			one of the path folders starts with YYYY-MM

		Full date:
			there is a full-date structure on the path.
			2015-01-04 | 2015_01_04 | 2015:01:04 | 2015 01 04

		The day, hour-minutes and seconds asigned are 01, 12:00:00 + image serial number (in seconds) for each image to preserve an order.
		'''
	## Cutting main tree from fullpaths.
	pathlevels = os.path.dirname (abspath).split ('/')
	# Removig not wanted slashes
	if '' in pathlevels:
		pathlevels.remove('')
	logging.debug ('Found directories levels: '+str(pathlevels))
	# Starting variables. From start, we assume that there is no date at all.
	fnyear = None
	fnmonth = None
	fnday = '01'
	fnhour = '12'
	fnmin = '00'
	fnsec = '00'
	for word in pathlevels:
		# C1.1 (/year/)
		yearfound = enclosedyearfinder (word)
		if yearfound != None:
			if mintepoch < yearfound < '2040':
				fnyear = yearfound
				continue

		# C1.2 (/month/)
		monthfound = enclosedmonthfinder (word)
		if monthfound != None:
			fnmonth = monthfound
			continue

		# C1.3 (/day/):
		dayfound = encloseddayfinder (word)
		if dayfound != None:
			fnday = dayfound
			continue

		# C2.1 (Year-month)
		yearfound, monthfound = yearmonthfinder (word)
		if yearfound != None:
			if mintepoch < yearfound < "2038":
				fnyear = yearfound
				fnmonth = monthfound

		# C3.1: (Year-month-day)
		yearfound, monthfound, dayfound = yearmonthdayfinder (word)
		if yearfound != None:
			if mintepoch < yearfound < "2038":
				fnyear = yearfound
				fnmonth = monthfound
				fnday = dayfound

		
	# C4: YYYY-MM-DD  in filename
	yearfound, monthfound, dayfound = yearmonthdayfinder (filename)
	if yearfound != None:
		if mintepoch < yearfound < "2038":
			fnyear = yearfound
			fnmonth = monthfound
			fnday = dayfound

	# C5: YYYYMMDD-HHMMSS  in filename and find a starting full-date identifier
	Imdatestart = False  # Flag to inform a starting full-date-identifier at the start of the file.
	foundtuple = fulldatefinder (filename)

	if foundtuple[0] != None:
		if mintepoch < foundtuple[0] < "2039":
			fnyear  = foundtuple[0]
			fnmonth = foundtuple[1]
			fnday   = foundtuple[2]
			fnhour  = foundtuple[3]
			fnmin   = foundtuple[4]
			fnsec   = foundtuple[5]
			logging.debug ( 'found full date identifier in ' + filename)
			#if mo.start() == 0 :
			if foundtuple[6] == True:
				logging.debug ('filename starts with a full date identifier: '+ filename )
				Imdatestart = True  #  True means that filename starts with full-date serial in its name (item will not add any date in his filename again)


	# setting creation date retrieved from filepath
	if fnyear != None and fnmonth != None:
		textdate = '%s:%s:%s %s:%s:%s'%(fnyear, fnmonth, fnday, fnhour, fnmin, fnsec)
		logging.debug ('This date have been retrieved from the file-path-name: ' + textdate )
		fnDateTimeOriginal = datetime.datetime.strptime (textdate, '%Y:%m:%d %H:%M:%S')


	# Fetch Serial number from filename
	imserie, imserial = serieserial (filename)


	# Fetch image metadata: ImageModel, ImageMake and Image date of creation
	textdate = None
	MetaDateTimeOriginal = None
	if fileext.lower() in ['.jpg', '.jpeg', '.raw', '.png']:
		ImageMake, ImageModel, textdate = Fetchmetadata (abspath)
		if textdate != None: 
			MetaDateTimeOriginal = datetime.datetime.strptime (textdate, '%Y:%m:%d %H:%M:%S')


	# Decide media date of creation
	''' Decide and assign the right media cration time due to:
	its metadata
	<path/file name>
	or from stat
	'''
	TimeOriginal = None  # From start we assign None if no matches are found.
	decideflag = None  # Flag to trace the decision.

	# Set Creation Date from Metadata if it is found
	if MetaDateTimeOriginal != None and ((forceassignfromfilename == False) or (forceassignfromfilename == True and fnDateTimeOriginal  == None )) :
		TimeOriginal = MetaDateTimeOriginal
		decideflag = 'Metadata'
		logging.debug ('Image Creation date has been set from image metadata: ' + str (TimeOriginal))

	else:
		# Set Creation Date extracted from filename/path
		if fnDateTimeOriginal != None :
			TimeOriginal = fnDateTimeOriginal
			decideflag = 'Filepath'
			logging.debug ('Image Creation date has been set from File path / name: '+ str(TimeOriginal))

		elif abspath.find('DCIM') != -1:
			# Set Creation Date from stat file.
			'''
			(You only should use this if you have those pictures in the original media storage
			without modifications and you want to read it directly from the media. or
			The files have been copied among filesystem that preserves the file creation date, usually ext3 ext4, NTFs, or MacOSx filesystems.
			See file properties first and ensure that you can trust its date of creation. Anyway, the file only will be processed
			if in its path is the word DCIM.)
				'''
			TimeOriginal = Statdate
			decideflag = 'Stat'
			logging.debug ( "Image Creation date has been set from File stat" )

	if TimeOriginal == None :
		logging.debug ( "Can't guess Image date of Creation" )
	return filename, fileext, filebytes, Imdatestart, fnDateTimeOriginal, MetaDateTimeOriginal, Statdate, TimeOriginal, decideflag, imserie, imserial

def mediaadd (abspath):
	if abspath.startswith (originlocation):
		branch = abspath[ len ( originlocation ):]
	else:
		branch = abspath[ len ( destlocation ):]

	filename, fileext, filebytes, Imdatestart, fnDateTimeOriginal, MetaDateTimeOriginal, Statdate, TimeOriginal, decideflag, imserie, imserial = mediainfo (abspath, forceassignfromfilename)

	con.execute ('INSERT INTO files (Fullfilepath, Filename, Fileext, Filebytes, Imdatestart, Pathdate, Exifdate, Statdate , Timeoriginal , Decideflag, Imgserie, Imgserial) \
		VALUES (?,?,?,?,?,?,?,?,?,?,?,?)', [ abspath, filename, fileext, filebytes, Imdatestart, fnDateTimeOriginal, MetaDateTimeOriginal, Statdate, TimeOriginal, decideflag, imserie, imserial ])

def mediascan(location):
	
	# 1.1) get items dir-tree
	listree = lsdirectorytree (location)
	nfilesscanned = 0

	# 1.2) get a list of media items

	for d in listree:
		for ext in wantedmedia:
			itemlist = list()
			itemlist += glob(os.path.join(d,'*.'+ ext.lower()))
			itemlist += glob(os.path.join(d,'*.'+ ext.upper()))
			if len (itemlist) > 0:
				for a in itemlist:
					if ignoreTrash == True : 
						if a.find ('.Trash') != -1 :
							logging.debug ('Item %s was not included (Trash folder)' %(a) )
							continue
						if a.find ('.thumbnails') != -1 :
							logging.debug ('Item %s was not included (Thumbnails folder)' %(a) )
							continue
					mediaadd (a)  # Add item's info to DB
					nfilesscanned += 1
	msg = str(nfilesscanned) + ' files where fetched at ' + location
	print (msg); logging.info (msg)
	return nfilesscanned

def showgeneralinfo():
	cursor.execute ("SELECT count (Fullfilepath) FROM files WHERE Decideflag = 'Metadata'")
	nfiles = ((cursor.fetchone())[0])
	msg = str(nfiles) + ' files already had metadata and will preserve it.'
	print (msg); logging.info (msg)

	cursor.execute ("SELECT count (Fullfilepath) FROM files WHERE Decideflag = 'Filepath' and Exifdate is NULL")
	nfiles = ((cursor.fetchone())[0])
	msg = str(nfiles) + ' files have not date metadata and a date have been retrieved from the filename or path.'
	print (msg); logging.info (msg)

	cursor.execute ("SELECT count (Fullfilepath) FROM files WHERE Decideflag = 'Filepath' and Exifdate is not NULL")
	nfiles = ((cursor.fetchone())[0])
	msg = str(nfiles) + ' files have a date metadata but a date have been retrieved from the filename or the path and it will rewritted (-faff option has been activated).'
	print (msg); logging.info (msg)

	cursor.execute ("SELECT count (Fullfilepath) FROM files WHERE Decideflag = 'Stat'")
	nfiles = ((cursor.fetchone())[0])
	msg = str(nfiles) + ' files does not have date metadata, is also was not possible to find a date on their paths or filenames, and their date of creation will be assigned from the file creation date (Stat).'
	print (msg); logging.info (msg)

	cursor.execute ("SELECT count (Fullfilepath) FROM files WHERE Decideflag is NULL ")
	nfiles = ((cursor.fetchone())[0])
	msg = str(nfiles) + ' files does not have date metadata, is also was not possible to find a date on their paths or filenames. Place "DCIM" as part of the folder or file name at any level if you want to assign the filesystem date as date of creation.'
	print (msg); logging.info (msg)
	return

def findeventname(Abranch):
	#  /YYYY-MM XeventnameX/
	exprlst = [
		"/[12]\d{3}[-_ ]?[01]\d ?(?P<XeventnameX>.*)/",
		"[12]\d{3}[-_ ]?[01]\d[-_ ]?[0-3]\d ?(?P<XeventnameX>.*)/",
		]

	#  /YYYY-MM-DD XeventnameX/
	eventname = ''
	for expr in exprlst: 
		mo = re.search(expr, Abranch)
		try:
			mo.group()
		except:
			pass
		else:
			eventname = mo.group('XeventnameX')
	return eventname

def fileinuse (entry):
	''' returns False if file is not beign used (opened), or
		returns True if file is beign used. 
		'''
	try:
		pids = check_output(["lsof", '-t', entry ])
	except:
		return False
	logging.debug('%s is beign accesed'%(entry))
	return True

# # # # # Main # # # #  #
if __name__ == "__main__": 
	# Load user config:
	# Getting user folder to place log files....
	userpath = os.path.join(os.getenv('HOME'),".Photodeliver")
	userfileconfig = os.path.join(userpath,"Photodelivercfg.py")
	dbpath = os.path.join(userpath,"tmpDB.sqlite3")

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

originlocations = '%(home)s/originlocation'  #  Path or list of paths from where retrieve new images.
destlocation = '%(home)s/destlocation'  # 'Path to where you want to store your photos'
renamemovies = True  # This option adds a creation date in movies file-names (wich doesn't have Exif Metadata)
renamephotos = True  # This option adds a creation date in media file-names (useful if you want to modify them)
eventminpictures = 8  # Minimum number of pictures to assign a day-event
gap = 60*60*5  # Number of seconds between shots to be considered both pictures to the same event.
copymode = 'm'  # 'c' for copy or 'm' to move new files
considerdestinationitems = True  # Consider destination items in order to group media files in events, files at destination location will remains as is.
moveexistentfiles = False  # True / False ...... True for move/reagroup or False to keep existent files at its place (Do nothing).
ignoreTrash = True  # True / False .... Ignore paths starting with '.Trash'
preservealbums = True  #  True / False  .... Do not include in fileScanning albums. An album is defined by a path that ends in _  pex.  /2015/2015 my album to preserve_/items.png 
forceassignfromfilename = False  # True / False   .... Force assign from a date found from filename if any. (This allows to override EXIF assignation if it is found).
cleaning = True  # True / False .....  Cleans empty folders (only folders that had contained photos)
storefilemetadata = True  # True means that guesed date of creation will be stored in the file-archive as EXIF metadata.
convert = True  # True / False ......  Try to convert image formats in JPG
centinelmode = False  # True / False ......  True means that the routine keeps resident in memory, it loops every centinelsecondssleep
centinelsecondssleep = 300  #  Number of seconds to sleep after doing an iteration.
'''%{'home':os.getenv('HOME')}
		)
		f.close()
		print ("An user config file has been created at:", userfileconfig)
		print ("Please customize by yourself before run this software again.")
		print ("This software is going to try to open with a text editor (gedit).")
		os.system ("gedit " + userfileconfig)
		exit()


	# Retrieve cmd line parameters >>>>>>>>

	parser = argparse.ArgumentParser()

	parser.add_argument("-ol", "--originlocations", nargs='+',
	                    help="Path or list of paths from where retrieve new images.")
	parser.add_argument("-dl", "--destlocation",
	                    help="Path to where you want to store your photos.")
	parser.add_argument("-rm", "--renamemovies", choices = [1,0], type = int,
	                    help="This option adds a creation date in movies file-names (wich doesn't have Exif Metadata).")
	parser.add_argument("-rp", "--renamephotos", choices = [1,0], type = int,
	                    help="This option adds a creation date in media file-names (useful if you want to modify them).")
	parser.add_argument("-minp", "--eventminpictures", type = int,
	                    help="Minimum number of pictures to assign a day-event.")
	parser.add_argument("-gap", "--gap", type = int,
	                    help="Number of seconds between shots to be considered both pictures to the same event.")
	parser.add_argument("-cpmode", "--copymode", choices = ['c','m'],
	                    help="'c' for copy or 'm' to move new files.")
	parser.add_argument("-cdi", "--considerdestinationitems", choices = [1,0], type = int,
	                    help="Consider destination items in order to group media files in events, files at destination location will remains as is.")
	parser.add_argument("-mef", "--moveexistentfiles", choices = [1,0], type = int,
	                    help="True for move/reagroup or False to keep existent files at its place (Do nothing)")
	parser.add_argument("-it", "--ignoreTrash", choices = [1,0], type = int,
	                    help="Ignore paths starting with '.Trash'")
	parser.add_argument("-pa", "--preservealbums", choices = [1,0], type = int,
	                    help="Do not include in fileScanning albums. An album is defined by a path that ends in _  pex.  /2015/2015 my album to preserve_/items.png ")
	parser.add_argument("-faff", "--forceassignfromfilename", choices = [1,0], type = int,
	                    help="Force assign from a date found in filename (if there is some). (This allows to overwrite EXIF assignation if it is found).")
	parser.add_argument("-clean", "--cleaning", choices = [1,0], type = int,
	                    help="Cleans empty folders (only folders that had contained photos)")
	parser.add_argument("-sfm", "--storefilemetadata", choices = [1,0], type = int,
	                    help="Store the guesed date in the filename as Exif data.")
	parser.add_argument("-conv", "--convert", choices = [1,0], type = int,
	                    help="Convert image format to JPG file")
	parser.add_argument("-sc", "--showconfig", action="store_true",
	                    help="Show running parameters, args parameters, config file parameters & exit")
	parser.add_argument("-sm", "--centinelmode", choices = [1,0], type = int,
	                    help="Activate the centinelmode, this mode keeps the program running and looping. You can define a number of seconds to sleep between loops.")
	parser.add_argument("-ssec", "--centinelsecondssleep", type = int,
	                    help="Number of seconds to sleep after iterating in centinel mode.")
	parser.add_argument("-test", "--dummy", action="store_true",
	                    help="Do not perform any file movements. Play on dummy mode.")


	args = parser.parse_args()
	parametersdyct = {}

	# Getting variables, override config file with args.
	if args.originlocations == None:
		originlocations =  Photodelivercfg.originlocations
	else:
		originlocations = args.originlocations
	parametersdyct["originlocations"] = originlocations


	if args.destlocation == None:
		destlocation =  Photodelivercfg.destlocation
	else:
		destlocation = args.destlocation
	parametersdyct["destlocation"] = destlocation


	if args.renamemovies == None:
		renamemovies = Photodelivercfg.renamemovies 
	else:
		renamemovies = [False,True][args.renamemovies]
	parametersdyct["renamemovies"] = renamemovies


	if args.renamephotos == None:
		renamephotos = Photodelivercfg.renamephotos
	else:
		renamephotos = [False,True][args.renamephotos]
	parametersdyct["renamephotos"] = renamephotos


	if args.eventminpictures == None:
		eventminpictures = Photodelivercfg.eventminpictures
	else:
		eventminpictures = args.eventminpictures
	parametersdyct["eventminpictures"] = eventminpictures


	if args.gap == None:
		gap = Photodelivercfg.gap
	else:
		gap = args.gap
	parametersdyct["gap"] = gap


	if args.copymode == None:
		copymode = Photodelivercfg.copymode
	else:
		copymode = args.copymode
	parametersdyct["copymode"] = copymode


	if args.considerdestinationitems == None:
		considerdestinationitems = Photodelivercfg.considerdestinationitems
	else:
		considerdestinationitems = [False,True][args.considerdestinationitems]
	parametersdyct["considerdestinationitems"] = considerdestinationitems


	if args.moveexistentfiles == None:
		moveexistentfiles = Photodelivercfg.moveexistentfiles
	else:
		moveexistentfiles = [False,True][args.moveexistentfiles]
	parametersdyct["moveexistentfiles"] = moveexistentfiles


	if args.ignoreTrash == None:
		ignoreTrash = Photodelivercfg.ignoreTrash
	else:
		ignoreTrash = [False,True][args.ignoreTrash]
	parametersdyct["ignoreTrash"] = ignoreTrash


	if args.preservealbums == None:
		preservealbums = Photodelivercfg.preservealbums 
	else:
		preservealbums = [False,True][args.preservealbums]
	parametersdyct["preservealbums"] = preservealbums


	if args.forceassignfromfilename == None:
		forceassignfromfilename = Photodelivercfg.forceassignfromfilename
	else:
		forceassignfromfilename = [False,True][args.forceassignfromfilename]
	parametersdyct["forceassignfromfilename"] = forceassignfromfilename


	if args.cleaning == None:
		cleaning = Photodelivercfg.cleaning
	else:
		cleaning = [False,True][args.cleaning]
	parametersdyct["cleaning"] = cleaning


	if args.storefilemetadata == None:
		storefilemetadata = Photodelivercfg.storefilemetadata
	else:
		storefilemetadata = [False,True][args.storefilemetadata]
	parametersdyct["storefilemetadata"] = storefilemetadata


	if args.convert == None:
		convert = Photodelivercfg.convert
	else:
		convert = [False,True][args.convert]
	parametersdyct["convert"] = convert


	if args.centinelmode == None:
		centinelmode = Photodelivercfg.centinelmode
	else:
		centinelmode = [False,True][args.centinelmode]
	parametersdyct["centinelmode"] = centinelmode


	if args.centinelsecondssleep == None:
		centinelsecondssleep = Photodelivercfg.centinelsecondssleep
	else:
		centinelsecondssleep = args.centinelsecondssleep
	parametersdyct["centinelsecondssleep"] = centinelsecondssleep



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
	logging.info("================ Starting a new run===================")
	logging.info("======================================================")

	# Check inconsistences
	errmsgs = []

	#-ol
	if originlocations != '':
		if type (originlocations) == str:
			originlocations = [originlocations,]

	else:
		if moveexistentfiles == True :
			print ('Origin location have not been entered, this will reagroup destlocation items.')
			logging.info ('No origin location entered: Reagrouping existent pictures')
			if centinelmode:
				print ('Centinelmode is active, this will keep reagrouping the same dest folder every %s seconds'%centinelsecondssleep)
				logging.info ('Centinelmode is active and Moveexistentfiles is also Active: Reagrouping existent destination pictures forever.')
		else:
			errmsgs.append ('No origin location was introduced, and you do not want to reagroup existent items.')
			logging.critical ('No origin location was introduced, and no interaction was selected.')
			
	#-dl
	if itemcheck(destlocation) != 'folder':
		errmsgs.append ('\nDestination folder does not exist:\n-dl\t' + str(destlocation))
		logging.critical('Source folder does not exist')
	destlocation = addslash (destlocation)
	 
	#-rm
	if type (renamemovies) is not bool :
		errmsgs.append ('\nRenamemovies parameter can only be True or False:\n-rm\t' + str(renamemovies))
		logging.critical('renamemovies parameter is not True nor False')

	#-rp
	if type (renamephotos) is not bool :
		errmsgs.append ('\nRenamephotos parameter can only be True or False:\n-rp\t' + str(renamephotos))
		logging.critical('renamephotos parameter is not True nor False')

	#-minp
	if type(eventminpictures) is not int :
		errmsgs.append ('\neventminpictures parameter can only be an integer:\n-minp\t' + str(eventminpictures))
		logging.critical('eventminpictures parameter is not an integer')

	#-gap
	if type(gap) is not int :
		errmsgs.append ('\ngap parameter can only be an integer:\n-gap\t' + str(gap))
		logging.critical('gap parameter is not an integer')

	#-cpmode
	if copymode not in ['c','m'] :
		errmsgs.append ('\ncopymode parameter can only be c or m:\n-copymode\t' + str(copymode))
		logging.critical('copymode parameter is not c nor m')

	#-cdi
	if type (considerdestinationitems) is not bool :
		errmsgs.append ('\nconsiderdestinationitems parameter can only be True or False:\n-cdi\t' + str(considerdestinationitems))
		logging.critical('considerdestinationitems parameter is not True nor False')

	#-mef
	if type (moveexistentfiles) is not bool :
		errmsgs.append ('\nmoveexistentfiles parameter can only be True or False:\n-mef\t' + str(moveexistentfiles))
		logging.critical('moveexistentfiles parameter is not True nor False')

	#-it
	if type (ignoreTrash) is not bool :
		errmsgs.append ('\nignoreTrash parameter can only be True or False:\n-it\t' + str(ignoreTrash))
		logging.critical('ignoreTrash parameter is not True nor False')

	#-pa
	if type (preservealbums) is not bool :
		errmsgs.append ('\npreservealbums parameter can only be True or False:\n-pa\t' + str(preservealbums))
		logging.critical('preservealbums parameter is not True nor False')

	#-faff
	if type (forceassignfromfilename) is not bool :
		errmsgs.append ('\nforceassignfromfilename parameter can only be True or False:\n-faff\t' + str(forceassignfromfilename))
		logging.critical('forceassignfromfilename parameter is not True nor False')

	#-clean
	if type (cleaning) is not bool :
		errmsgs.append ('\ncleaning parameter can only be True or False:\n-clean\t' + str(cleaning))
		logging.critical('cleaning parameter is not True nor False')

	#-sfm
	if type (storefilemetadata) is not bool :
		errmsgs.append ('\nstorefilemetadata parameter can only be True or False:\n-fb\t' + str(storefilemetadata))
		logging.critical('storefilemetadata parameter is not True nor False')

	#-conv
	if type (convert) is not bool :
		errmsgs.append ('\nconvert parameter can only be True or False:\n-conv\t' + str(convert))
		logging.critical('convert parameter is not True nor False')

	#-sm
	if type (centinelmode) is not bool :
		errmsgs.append ('\ncentinelmode parameter can only be True or False:\n-sm\t' + str(centinelmode))
		logging.critical('centinelmode parameter is not True nor False')

	#-ssec
	if type(centinelsecondssleep) is not int :
		errmsgs.append ('\ncentinelsecondssleep parameter can only be an integer:\n-ssec\t' + str(centinelsecondssleep))
		logging.critical('centinelsecondssleep parameter is not an integer')


	# exitting if errors econuntered
	if len (errmsgs) != 0 :
		for a in errmsgs:
			print (a)
		print ('\nplease revise your config file or your command line arguments.','Use --help or -h for some help.','\n ....exitting',sep='\n')
		exit()


	# adding to log file Running parameters
	for a in parametersdyct:
		text = a + " = "+ str(parametersdyct[a]) + " \t (from args:"+ str(eval ("args." + a)) + ") \t (At config file: "+ str(eval ("Photodelivercfg." + a))+ ")"
		logging.info (text)
		if args.showconfig :
			print (text+ "\n")

	if args.dummy:
		logging.info("-------------- Running in Dummy mode ------------")

	# exitting if show config was enabled.
	if args.showconfig :
		print ("exitting...")
		exit()


	# ===========================================
	# ========= Main module =====================
	# ===========================================

	while True:
		for originlocation in originlocations:
			if originlocation != '':
				if itemcheck(originlocation) != 'folder':
					msg = 'Source folder does not exist: ' + originlocation
					print ("\nWARNING:"+msg+"\n"); logging.critical(msg)
					continue				
				originlocation = addslash (originlocation)


			logging.info('')
			logging.info('='*50)
			logging.info('From:' + originlocation)
			logging.info('  To:' + destlocation)
			print ('='*50,'Processing files at'+ originlocation, sep='\n')
			# 0) Start tmp Database

			if itemcheck (dbpath) == 'file':
				os.remove (dbpath)
				logging.info("Older tmp database found, it has been deleted.")

			con = sqlite3.connect (dbpath) # it creates one if it doesn't exists
			cursor = con.cursor() # object to manage queries

			# 0.1) Setup DB
			cursor.execute ('CREATE TABLE files (\
				Fullfilepath char NOT NULL ,\
				Filename char NOT NULL ,\
				Fileext char  ,\
				Targetfilepath char  ,\
				Filebytes int NOT NULL ,\
				Imdatestart Boolean, \
				Exifdate date  ,\
				Pathdate date  ,\
				Statdate date NOT NULL,\
				Timeoriginal date, \
				Decideflag char, \
				Convertfileflag Boolean, \
				Imgserie char, \
				Imgserial char, \
				EventID int, \
				Eventdate date \
				)')
			con.commit()

			# 1) Get items
			# 1.1) Retrieving items to process

			Totalfiles = 0
			if not (originlocation == '' or originlocation == destlocation):
				Totalfiles += mediascan (originlocation)
				con.commit()

			Totalfiles += mediascan (destlocation)
			con.commit()

			msg = '-'*20+'\n'+ str(Totalfiles) + ' Total files scanned'
			print (msg); logging.info (msg)
			if Totalfiles == 0 :
				print ('Nothing to import / reagroup.')
				logging.warning ('Thereis nothing to import or reagroup, please revise your configuration, exitting....')
				continue

			# 1.2) Show general info
			showgeneralinfo ()

			# 2) Processing items 
			# 2.1) Grouping in events, máx distance is gap seconds

			if gap > 0:
				if considerdestinationitems == True:
					#considering all items
					cursor.execute ('SELECT Fullfilepath, Timeoriginal FROM files where Timeoriginal is not NULL ORDER BY Timeoriginal')
				else:
					#considering only items at origin folder
					cursor.execute ("SELECT Fullfilepath, Timeoriginal FROM files where Timeoriginal is not NULL and Fullfilepath LIKE '%s'  ORDER BY Timeoriginal" %(originlocation+"%"))

				regcounter = 0
				eventID = 0
				timegap = datetime.timedelta(days=0, seconds=gap, microseconds=0, milliseconds=0, minutes=0, hours=0)
				msg = "Group option is activated (-gap option). This will group Pictures closer in time than " + str(timegap) + " in an event day."
				print (msg); logging.info (msg)

				for i in cursor:
					regcounter += 1
					Fullfilepath1, Timestr = i
					TimeOriginal1 = datetime.datetime.strptime (Timestr, '%Y-%m-%d %H:%M:%S')
					if regcounter == 1 :
						TimeOriginal0 = TimeOriginal1
						Fullfilepath0 = Fullfilepath1
						con.execute ("UPDATE files set EventID=0 where Fullfilepath = '%s'" %(Fullfilepath1))
						continue
					diff = TimeOriginal1-TimeOriginal0
					if diff <= timegap :
						logging.debug  ('this picture is part of an event with the preceding one')
					else:
						logging.debug ('this picture is not part of an event with the preceding one')
						eventID += 1
					con.execute ("UPDATE files set EventID=%s where Fullfilepath = '%s'" %(eventID, Fullfilepath1))

					TimeOriginal0 = TimeOriginal1
					Fullfilepath0 = Fullfilepath1
					# print (regcounter, eventID, i[1])
				con.commit()

				#2.2) Inform de date of the event. (The minimun date)
				for i in range (0,eventID+1):
					# count number of files in that event: 
					cursor.execute ('SELECT count (Fullfilepath), MIN (Timeoriginal) FROM files where EventID = %s' %(i))
					nfiles, eventdate = cursor.fetchone()
					#print (i, nfiles, eventdate)
					# Set event date if it has the minimun number required.
					if nfiles >= eventminpictures:
						print ('')
						con.execute ("UPDATE files set Eventdate='%s' where EventID = %s" %(eventdate ,i))
				con.commit()


			# 3) Set Target files for items
			cursor.execute ('SELECT Fullfilepath, Timeoriginal, Eventdate, Filename, Fileext, Filebytes,Imdatestart FROM files ORDER BY Timeoriginal')
			for i in cursor:
				a, Timeoriginal, Eventdate, Filename, fileext, filebytes,Imdatestart = i
				if a.startswith(destlocation):
					Abranch = a.replace(destlocation,'')
				else:
					Abranch = a.replace(originlocation,'')

				# eventname = None
				eventnameflag = False

				# 3.1) Skipping processing a new path to files into destination folder if moveexistentfiles is False
				if a.startswith(destlocation) and moveexistentfiles == False:
					logging.debug ('Item %s was not included (moveexistentfiles option is False)' %(a) )
					continue

				# 3.2) item's fullpath and filename
				if preservealbums == True and a.find ('_/') != -1 :
					if a.startswith (destlocation) :
						logging.debug ('Item %s was not included (Preserving album folder at destination location).' %(a) )
					else:
						logging.debug ('Moving item %s to destination preserving its path (is part of an album).' %(a) )
						dest = os.path.join(destlocation, a.replace(originlocation,''))
					continue

				else:
					if Timeoriginal == None:
						logging.debug ('Moving item %s to nodate folder (it has no date).' %(a) )			
						if a.startswith(os.path.join(destlocation,"nodate")):
							dest = a
						else:
							dest = os.path.join(destlocation, "nodate", Abranch)

					else:
						itemcreation = datetime.datetime.strptime (Timeoriginal, '%Y-%m-%d %H:%M:%S')  # Item has a valid date, casting it to a datetime object.

						# Check origin dir Structure for an already event name
						eventname = findeventname (Abranch)
						if eventname != '':
							eventnameflag = True
							logging.debug( 'found an origin event name in: %s (%s)' %(a, eventname))

						# Getting a possible event day
						# deliver
						if eventnameflag == True or Eventdate is not None:
							#destination includes a day - event
							if Eventdate == None:
								Eventdate = itemcreation
							else:
								Eventdate = datetime.datetime.strptime (Eventdate, '%Y-%m-%d %H:%M:%S')
							dest = os.path.join(destlocation, Eventdate.strftime('%Y'), Eventdate.strftime('%Y-%m-%d'), os.path.basename(a))
							eventnameflag = True
						else:
							#destination only includes a month (go to a various month-box)
							dest = os.path.join(destlocation, itemcreation.strftime('%Y'), itemcreation.strftime('%Y-%m'), os.path.basename(a))
						# set date information in filename.
						if ((renamemovies == True and fileext.lower()[1:] in moviesmedia) or ( renamephotos == True and fileext.lower()[1:] in photomedia)) and Imdatestart != True :
							dest = os.path.join(os.path.dirname(dest), itemcreation.strftime('%Y%m%d_%H%M%S') + "-" + os.path.basename(dest) )
				
				# 3.3) Adding event name in the path
				if eventnameflag == True:
					destcheck = os.path.dirname(dest)  # Check destination dir structure ../../aaaa/aaaa-mm-dd*
					levents = glob(destcheck + '*')
					if len (levents) != 0 :
						# (Get event path as existing path for destination)
						dest = os.path.join(levents.pop(), os.path.basename(dest))
					else:
						if eventname != '':
							eventname = " "+ eventname
						dest = os.path.join(os.path.dirname(dest) + eventname, os.path.basename(dest) )
				# 3.4) Set convert flag
				convertfileflag = False
				if convert == True and fileext.lower() in ['.png','.bmp',]:
					dest = os.path.splitext(dest)[0]+".jpg"
					convertfileflag = True
					logging.info ('Convertfileflag =' + str(convertfileflag))
				
				# 3.5) Checkig if it is a duplicated file.
				while True:
					if itemcheck (dest) == '':
						break
					else:
						if filebytes != os.path.getsize(dest):
							dest = Nextfilenumber (dest)
							continue
						else:
							if a.startswith (os.path.join(originlocation,dupfoldername)) or dest.startswith (os.path.join(originlocation,dupfoldername)) or a.startswith (destlocation) :
								logging.warning('destination item already exists')
								dest = a
								break
							else:
								dest = os.path.join (originlocation,dupfoldername, a.replace(originlocation,''))
								continue

				con.execute ("UPDATE files set Targetfilepath = '%s', Convertfileflag = '%s' where Fullfilepath = '%s'" %(dest ,convertfileflag, a))
			con.commit()

			# 4) Perform file operations
			foldercollection = set ()
			cursor.execute ('SELECT Fullfilepath, Targetfilepath, Fileext, Timeoriginal, Decideflag, Convertfileflag FROM files WHERE Targetfilepath IS NOT NULL')
			for i in cursor:
				a, dest, fileext, Timeoriginal, decideflag, convertfileflag = i
				convertfileflag = eval (convertfileflag)
				logging.info ('')
				logging.info ('Processing:')
				logging.info (a)
				if fileinuse (a):
					logging.warning ('File is beign accesed, Skipping')
					continue
				if itemcheck (os.path.dirname(dest)) == '':
						if args.dummy != True:
							os.makedirs (os.path.dirname(dest))
				# Convert to JPG Option
				if convertfileflag == True:
					logging.info ("\t Converting to .jpg")
					picture = Image.open (a)
					if args.dummy != True:
						picture.save (dest)
					#picture.close()  # commented for ubuntu 14.10 comtabilitiy
					if copymode == 'm':
						if args.dummy != True:
							os.remove (a)
						logging.info ('\t origin file successfully deleted after conversion.')
				elif a != dest:
					if copymode == 'm':
						if args.dummy != True:
							shutil.move (a, dest)
						logging.info ('\t file successfully moved into destination.')
					else:	
						if args.dummy != True:
							shutil.copy (a, dest)
						logging.info ('\t file successfully copied into destination.')

				if cleaning == True and copymode == 'm':
					foldercollection.add (os.path.dirname(a))

				# Write metadata into the file-archive
				if storefilemetadata == True and fileext.lower()[1:] not in moviesmedia and decideflag in ['Filepath','Stat']:
					if args.dummy != True:
						metadata = GExiv2.Metadata(dest)
						itemcreation = datetime.datetime.strptime (Timeoriginal, '%Y-%m-%d %H:%M:%S')  # Item has a valid date, casting it to a datetime object.
						metadata.set_date_time(itemcreation)
						metadata.save_file()
					logging.info ('\t' + 'writed metadata to image file.')
				logging.info ('\t' + dest)

			#4) Cleaning empty directories
			if cleaning == True:
				logging.info ('='*10)
				logging.info ('Checking empty folders to delete them')
				foldercollectionnext = set()
				while len(foldercollection) > 0:
					for i in foldercollection:
						logging.info ('checking: %s' %i)
						if itemcheck(i) != 'folder':
							logging.warning ('\tDoes not exists or is not a folder. Skipping')
							continue			
						if len (os.listdir(i)) == 0 and i not in {originlocation[:-1], destlocation[:-1]}:
							if args.dummy != True:
								shutil.rmtree (i)
							logging.info ('\tfolder has been removed. (was empty)')
							foldercollectionnext.add (os.path.dirname(i))
							logging.debug ('\tadded next level to re-scan')
					foldercollection = foldercollectionnext
					foldercollectionnext = set()

			#5) Done
			print ('Done!')
			''' print a little resumen '''

		##) Sleeping and iterating in case of centinelmode
		if centinelmode:
			print ('\nsleeping %s seconds\n'%centinelsecondssleep)
			time.sleep(centinelsecondssleep)
		else:
			break

