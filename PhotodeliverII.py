#!/usr/bin/python3

''' This script moves camera file-media to a folder on our hard disk.
	it will group files in foldes due to its date of creation 
	it also deltes duplicated files (same name and bytes)'''

# Module import
import sys, os, shutil, logging, datetime, time, re
from glob import glob
from gi.repository import GExiv2  # Dependencies: gir1.2-gexiv2   &   python-gobject
from PIL import Image
import argparse  # for command line arguments
import sqlite3; 
os.stat_float_times (False)  #  So you won't get milliseconds retrieving Stat dates; this will raise in error parsing getmtime.


# Internal variables.
moviesmedia = ['mov','avi','m4v', 'mpg', '3gp', 'mp4']
wantedmedia = ['jpg','jpeg','raw','png','bmp'] + moviesmedia
justif = 20  #  number of characters to justify logging info.


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

originlocation = '%(home)s/originlocation'  #  Path from where retrieve new images.
destination = '%(home)s/destlocation'  # 'Path to where you want to store your photos'
renamemovies = True  # This option adds a creation date in movies file-names (wich doesn't have Exif Metadata)
renamephotos = True  # This option adds a creation date in media file-names (useful if you want to modify them)
eventminpictures = 8  # Minimum number of pictures to assign a day-event
gap = 60*60*5  # Number of seconds between shots to be considered both pictures to the same event.
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
storefilemetadata = True  # True means that guesed date of creation will be stored in the file-archive as EXIF metadata.
convert = True  # True / False ......  Try to convert image formats in JPG
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
parser.add_argument("-ol", "--originlocation",
                    help="Path from where retrieve new images.")
parser.add_argument("-dl", "--destination",
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
                    help="Consider destination items in order to group media files in events.")
parser.add_argument("-mef", "--moveexistentfiles", choices = [1,0], type = int,
                    help="True for move/reagroup or False to keep existent files at its place (Do nothing)")
parser.add_argument("-it", "--ignoreTrash", choices = [1,0], type = int,
                    help="Ignore paths starting with '.Trash'")
parser.add_argument("-pa", "--preservealbums", choices = [1,0], type = int,
                    help="Do not include in fileScanning albums. An album is defined by a path that ends in _  pex.  /2015/2015 my album to preserve_/items.png ")
parser.add_argument("-faff", "--forceassignfromfilename", choices = [1,0], type = int,
                    help="Force assign from a date found from filename if any. (This allows to override EXIF assignation if it is found).")
parser.add_argument("-clean", "--cleaning", choices = [1,0], type = int,
                    help="Cleans empty folders (only folders that had contained photos)")
'''
parser.add_argument("-lmg", "--latestmediagap", type = int,
                    help="Seconds from now to consider that item is one of the lattest media. You can override interact with this media.")
parser.add_argument("-nmlm", "--donotmovelastmedia", choices = [1,0], type = int,
                    help="True means that the new lattest media will not be moved from its place.")
parser.add_argument("-fb", "--filterboost", choices = [1,0], type = int,
                    help="True means that only consider destination folders that contains in its paths one of the years that have been retrieved from origin files. So it boost destination media scanning by filtering it.")
'''
parser.add_argument("-sfm", "--storefilemetadata", choices = [1,0], type = int,
                    help="Store the guesed date in the filename as Exif data.")
parser.add_argument("-conv", "--convert", choices = [1,0], type = int,
                    help="Convert image format to JPG file")
parser.add_argument("-sc", "--showconfig", action="store_true",
                    help="Show running parameters, args parameters, config file parameters & exit")
parser.add_argument("-test", "--dummy", action="store_true",
                    help="Do not perform any file movements. Play on dummy mode.")


args = parser.parse_args()
parametersdyct = {}

# Getting variables.
if args.originlocation == None:
	originlocation =  Photodelivercfg.originlocation  #  Place to store files once procesed
else:
	originlocation = args.originlocation
parametersdyct["originlocation"] = originlocation


if args.destination == None:
	destination =  Photodelivercfg.destination  #  Place to store files once procesed
else:
	destination = args.destination
parametersdyct["destination"] = destination


if args.renamemovies == None:
	renamemovies = Photodelivercfg.renamemovies  # This option adds a creation date in movies file-names (wich doesn't have Exif Metadata)
else:
	renamemovies = [False,True][args.renamemovies]
parametersdyct["renamemovies"] = renamemovies


if args.renamephotos == None:
	renamephotos = Photodelivercfg.renamephotos  # This option adds a creation date in media file-names
else:
	renamephotos = [False,True][args.renamephotos]
parametersdyct["renamephotos"] = renamephotos


if args.eventminpictures == None:
	eventminpictures = Photodelivercfg.eventminpictures  # minimun number of pictures to assign a day-event
else:
	eventminpictures = args.eventminpictures
parametersdyct["eventminpictures"] = eventminpictures


if args.gap == None:
	gap = Photodelivercfg.gap  # number of seconds between shots to be considered both pictures to the same event.
else:
	gap = args.gap
parametersdyct["gap"] = gap


if args.copymode == None:
	copymode = Photodelivercfg.copymode  # 'c' for copy or 'm' to move new files
else:
	copymode = args.copymode
parametersdyct["copymode"] = copymode


if args.considerdestinationitems == None:
	considerdestinationitems = Photodelivercfg.considerdestinationitems  # Consider destination items in order to group media files in events.
else:
	considerdestinationitems = [False,True][args.considerdestinationitems]
parametersdyct["considerdestinationitems"] = considerdestinationitems


if args.moveexistentfiles == None:
	moveexistentfiles = Photodelivercfg.moveexistentfiles  # True for move/reagroup or False to keep existent files at its place (Do nothing).
else:
	moveexistentfiles = [False,True][args.moveexistentfiles]
parametersdyct["moveexistentfiles"] = moveexistentfiles


if args.ignoreTrash == None:
	ignoreTrash = Photodelivercfg.ignoreTrash  # Ignore paths starting with '.Trash'
else:
	ignoreTrash = [False,True][args.ignoreTrash]
parametersdyct["ignoreTrash"] = ignoreTrash


if args.preservealbums == None:
	preservealbums = Photodelivercfg.preservealbums  #  True / False  .... Do not include in fileScanning albums. An album is defined by a path that ends in _  pex.  /2015/2015 my album to preserve_/items.png 
else:
	preservealbums = [False,True][args.preservealbums]
parametersdyct["preservealbums"] = preservealbums


if args.forceassignfromfilename == None:
	forceassignfromfilename = Photodelivercfg.forceassignfromfilename  #  True / False   .... Force assign from a date found from filename if any. (This allows to override EXIF assignation if it is found).
else:
	forceassignfromfilename = [False,True][args.forceassignfromfilename]
parametersdyct["forceassignfromfilename"] = forceassignfromfilename


if args.cleaning == None:
	cleaning = Photodelivercfg.cleaning  # Cleans empty folders (only folders that had contained photos)
else:
	cleaning = [False,True][args.cleaning]
parametersdyct["cleaning"] = cleaning


'''
if args.latestmediagap == None:
	latestmediagap = Photodelivercfg.latestmediagap  # Amount in seconds since 'now' to consider a media-file is one of the latest 
else:
	latestmediagap = args.latestmediagap
parametersdyct["latestmediagap"] = latestmediagap


if args.donotmovelastmedia  == None:
	donotmovelastmedia = Photodelivercfg.donotmovelastmedia  # Flag to move or not move the latest media bunch.
else:
	donotmovelastmedia = [False,True][args.donotmovelastmedia]
parametersdyct["donotmovelastmedia"] = donotmovelastmedia


if args.filterboost == None:
	filterboost = Photodelivercfg.filterboost
else:
	filterboost = [False,True][args.filterboost]
parametersdyct["filterboost"] = filterboost
'''

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
errmsgs = []

#-ol
if originlocation != '':
	if itemcheck(originlocation) != 'folder':
		errmsgs.append ('\nSource folder does not exist:\n-ol\t'+originlocation)
		logging.critical('Source folder does not exist: ' + originlocation)

else:
	if moveexistentfiles == True :
		print ('Origin location have been not entered, this will reagroup destination items.')
		logging.info ('No origin location entered: Reagrouping existent pictures')
	else:
		errmsgs.append ('No origin location was introduced, and you do not want to reagroup existent items.')
		logging.critical ('No origin location was introduced, and no interaction was selected.')
		
#-dl
if itemcheck(destination) != 'folder':
	errmsgs.append ('\nDestination folder does not exist:\n-dl\t' + str(destination))
	logging.critical('Source folder does not exist')
 
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
'''
#-lmg
if type(latestmediagap) is not int :
	errmsgs.append ('\nlatestmediagap parameter can only be an integer:\n-lmg\t' + str(latestmediagap))
	logging.critical('latestmediagap parameter is not an integer')

#-nmlm
if type (donotmovelastmedia) is not bool :
	errmsgs.append ('\ndonotmovelastmedia parameter can only be True or False:\n-nmlm\t' + str(donotmovelastmedia))
	logging.critical('donotmovelastmedia parameter is not True nor False')

#-fb
if type (filterboost) is not bool :
	errmsgs.append ('\nfilterboost parameter can only be True or False:\n-fb\t' + str(filterboost))
	logging.critical('filterboost parameter is not True nor False')
'''
#-sfm
if type (storefilemetadata) is not bool :
	errmsgs.append ('\nstorefilemetadata parameter can only be True or False:\n-fb\t' + str(storefilemetadata))
	logging.critical('storefilemetadata parameter is not True nor False')

#-conv
if type (convert) is not bool :
	errmsgs.append ('\nconvert parameter can only be True or False:\n-conv\t' + str(convert))
	logging.critical('convert parameter is not True nor False')

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
if args.showconfig :
	print ("exitting...")
	exit()

if args.dummy:
	logging.info("-------------- Running in Dummy mode ------------")

def readmetadate (metadata, exif_key):
	metadate = metadata.get(exif_key)
	if not (metadate == None or metadate.strip() == ''):
		logging.debug (exif_key + ' found:' + metadate)
	else:
		logging.debug ('No '+ exif_key + 'found.')
	return metadate

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

def mediaadd(item):
	#1) Retrieve basic info from the file
	logging.debug ('## item: '+ item)
	abspath = item
	filename, fileext = os.path.splitext(os.path.basename (abspath))
	Statdate = datetime.datetime.utcfromtimestamp(os.path.getmtime (abspath))
	filebytes = os.path.getsize(abspath)  # logging.debug ('fileTepoch (from Stat): '.ljust( justif ) + str(fileTepoch))
	fnDateTimeOriginal = None  # From start we assume a no date found on the file path

	#2) Fetch date identificators form imagepath, serie and serial number if any. 
	mintepoch = 1900  # In order to discard low year values, this is the lowest year. 

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
	if abspath.startswith (originlocation):
		branch = abspath[ len ( originlocation ):]
	else:
		branch = abspath[ len ( destination ):]
	pathlevels = os.path.dirname (branch).split ('/')
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
	# C1 - /*Year*/ /month/ /day/ in pathlevels (year must be detected from an upper level first)
	for word in pathlevels:
		wordslash = "/"+word+"/"
			#possible year is a level path:
		expr = "/(?P<year>[12]\d{3})/"
		mo = re.search(expr, wordslash)
		try:
			mo.group()
		except:
			pass
		else:
			if int(mo.group('year')) in range (mintepoch, 2038):
				fnyear = mo.group ('year')
				logging.debug( 'found possible year in '+ wordslash +':'+fnyear)
				continue

				#possible month is a level path:
		if len (word) == 2 and word.isnumeric ():
			if int(word) in range(1,13):
				fnmonth = word
				logging.debug( 'found possible month in'+ word +':'+fnmonth)
				continue

				#possible day is a level path:
		if len (word) == 2 and word.isnumeric ():
			if int(word) in range(1,32):
				fnday = word
				logging.info( 'found possible day in'+ word +':'+fnday)
				continue

		# C2 (Year-month)
		expr = ".*(?P<year>[12]\d{3})[-_ /]?(?P<month>[01]\d).*"
		mo = re.search(expr, wordslash)
		try:
			mo.group()
		except:
			pass
		else:
			if int (mo.group('month')) in range (1,13) and int(mo.group('year')) in range (mintepoch, 2038):
				fnyear = mo.group ('year')
				fnmonth = mo.group ('month')
				logging.debug( 'found possible year-month in'+ wordslash +':'+fnyear+" "+fnmonth)

		# C3: (Year-month-day)
		expr = "(?P<year>[12]\d{3})[-_ /]?(?P<month>[01]\d)[-_ /]?(?P<day>[0-3]\d)"
		mo = re.search(expr, wordslash)
		try:
			mo.group()
		except:
			pass
		else:
			if int(mo.group('year')) in range (mintepoch, 2038) and int (mo.group('month')) in range (1,13) and int (mo.group ('day')) in range (1,32):
				fnyear = mo.group ('year')
				fnmonth = mo.group ('month')
				fnday = mo.group ('day')
				logging.debug( 'found possible year-month-day in' + wordslash + ':' + fnyear + " " + fnmonth + " " + fnday)


	# C4: YYYYMMDD-HHMMSS  in filename
	Imdatestart = False  # Flag to inform a starting full-date-identifier at the start of the file.
	expr = '(?P<year>[12]\d{3})[-_ .:]?(?P<month>[01]\d)[-_ .:]?(?P<day>[0-3]\d)[-_ .:]?(?P<hour>[012]\d)[-_ .:]?(?P<min>[0-5]\d)[-_ .:]?(?P<sec>[0-5]\d)'
	mo = re.search (expr, filename)
	try:
		mo.group()
	except:
		logging.debug ("expression %s Not found in %s" %(expr, filename))
		pass
	else:			
		if int(mo.group('year')) in range (mintepoch, 2038):
			fnyear  = mo.group ('year')
			fnmonth = mo.group ('month')
			fnday   = mo.group ('day')
			fnhour  = mo.group ('hour')
			fnmin   = mo.group ('min')
			fnsec   = mo.group ('sec')
			logging.debug ( 'found full date identifier in ' + filename)
			if mo.start() == 0 :
				logging.debug ('filename starts with a full date identifier: '+ filename )
				Imdatestart = True  #  True means that filename starts with full-date serial in its name (item will not add any date in his filename again)


	# setting creation date retrieved from filepath
	if fnyear != None and fnmonth != None:
		textdate = '%s:%s:%s %s:%s:%s'%(fnyear, fnmonth, fnday, fnhour, fnmin, fnsec)
		logging.debug ('This date have been retrieved from the file-path-name: ' + textdate )
		fnDateTimeOriginal = datetime.datetime.strptime (textdate, '%Y:%m:%d %H:%M:%S')



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
		mo = re.search (expr, filename)
		try:
			mo.group()
		except:
			logging.debug ("expression %s Not found in %s" %(expr, filename))
			continue
		else:
			mo = re.search ( serialdict[expr], filename)
			logging.debug ("expression %s found in %s" %(expr, filename))
			sf = True
			break
	# setting serie and serial number
	if sf == True:
		imserie  = mo.group ('se')
		imserial = mo.group ('sn')
		logging.debug ( 'Item serie and serial number (' + filename + '): '+ imserie + ' ' +  imserial)
	else:
		imserie  = None
		imserial = None	
	

	# Fetch image metadata (if any) 
	textdate = None
	MetaDateTimeOriginal = None
	if fileext.lower() in ['.jpg', '.jpeg', '.raw', '.png']:
		metadata = GExiv2.Metadata(abspath)
		
		ImageModel = readmetadate( metadata ,'Exif.Image.Model')
		ImageMake = readmetadate( metadata ,'Exif.Image.Make')
		textdate = readmetadate( metadata ,'Exif.Photo.DateTimeOriginal')
		if textdate == None:
			textdate = readmetadate( metadata ,'Exif.Photo.DateTimeDigitized')
			if textdate == None:
				textdate = readmetadate( metadata ,'Exif.Image.DateTime')
		
		if textdate != None: 
			MetaDateTimeOriginal = datetime.datetime.strptime (textdate, '%Y:%m:%d %H:%M:%S')


	# Decide media date of creation
	''' Decide and assign the right media cration time due to:
	its metadata
	<path/file name>
	or from stat
	'''
	TimeOriginal = None  # From start we assign None if no matches are found.
	Decideflag = None  # Flag storing the decision.

	# Set Creation Date from Metadata if it is found,
	if MetaDateTimeOriginal != None and forceassignfromfilename == False:
		TimeOriginal = MetaDateTimeOriginal
		Decideflag = 'Metadata'
		logging.debug ('Image Creation date has been set from image metadata: ' + str(TimeOriginal))
	else:
		# Set Creation Date extracted from filename/path
		if fnDateTimeOriginal != None :
			TimeOriginal = fnDateTimeOriginal
			Decideflag = 'Filepath'
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
			Decideflag = 'Stat'
			logging.debug ( "Image Creation date has been set from File stat" )

	if TimeOriginal == None :
		logging.debug ( "Can't guess Image date of Creation" )


	con.execute ('INSERT INTO files (Fullfilepath, Filename, Fileext, Filebytes, Imdatestart,Pathdate, Exifdate, Statdate , Timeoriginal , Decideflag, Imgserie, Imgserial) \
		VALUES (?,?,?,?,?,?,?,?,?,?,?,?)', [ item, filename, fileext, filebytes, Imdatestart,fnDateTimeOriginal, MetaDateTimeOriginal, Statdate, TimeOriginal, Decideflag, imserie, imserial ])

def mediascan(location):
	
	# 1.1) get items dir-tree
	listree = lsdirectorytree (location)

	# 1.2) get a list of media items and casting into a class

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
					mediaadd (a)  # Add item info to DB
	return

# ===========================================
# ========= Main module =====================
# ===========================================


# 0) Start tmp Database

if itemcheck (dbpath) == "file":
	os.remove (dbpath)
	logging.info("Older tmp database found, it has been deleted.")

con = sqlite3.connect (dbpath) # it creates one if it doesn't exists
cursor = con.cursor() # object to manage queries

# 0.1) Setup DB
cursor.execute ('CREATE TABLE files (\
	Scanpath char ,\
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
	Imgserie char, \
	Imgserial char, \
	Event char \
	)')
con.commit()

# 1) Get items
# 1.1) Retrieving items to process

if not (originlocation == '' or originlocation == destination):
	mediascan (originlocation)
	con.commit()

mediascan (destination)
con.commit()


Totalfiles = 0
# Number of files at originlocation
cursor.execute ("SELECT count (Fullfilepath) FROM files WHERE Fullfilepath LIKE '%s'" %(originlocation+"%"))
nfilesscanned = ((cursor.fetchone())[0])
Totalfiles += nfilesscanned
msg = str(nfilesscanned) + ' files where scanned at originlocation'
print (msg); logging.info (msg)

# Number of files at destlocation
cursor.execute ("SELECT count (Fullfilepath) FROM files WHERE Fullfilepath LIKE '%s'" %(destination+"%"))
nfilesscanned = ((cursor.fetchone())[0])
Totalfiles += nfilesscanned
msg = str(nfilesscanned) + ' files where scanned at destination location'
print (msg); logging.info (msg)

msg = '-'*20+'\n'+ str(Totalfiles) + ' Total files scanned'
print (msg); logging.info (msg)
if Totalfiles == 0 :
	print ('Nothing to import / reagroup.')
	logging.warning ('Thereis nothing to import or reagroup, please revise your configuration, exitting....')
	exit()


# 1.2) Show general info
cursor.execute ("SELECT count (Fullfilepath) FROM files WHERE Decideflag = 'Metadata'")
nfiles = ((cursor.fetchone())[0])
msg = str(nfiles) + ' files already had metadata and will preserve it.'
print (msg); logging.info (msg)

cursor.execute ("SELECT count (Fullfilepath) FROM files WHERE Decideflag = 'Filepath' and Exifdate is NULL")
nfiles = ((cursor.fetchone())[0])
msg = str(nfiles) + ' files have not date metadata and a date have been retrieved from the filename or the path.'
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
msg = str(nfiles) + ' files does not have date metadata, is also was not possible to find a date on their paths or filenames. Place "DCIM" as part of the folder or file name at any level if you want to assign the filesystem date of creation.'
print (msg); logging.info (msg)




# 2) Processing items 
# 2.1) Grouping in events, máx distance is gap seconds

if gap >= 1:
	if considerdestinationitems == True:
		#considering all items
		cursor.execute ('SELECT Fullfilepath, Timeoriginal FROM files where Timeoriginal is not NULL ORDER BY Timeoriginal')
	else:
		#considering only items at origin folder
		cursor.execute ("SELECT Fullfilepath, Timeoriginal FROM files where Timeoriginal is not NULL and Fullfilepath LIKE '%s'  ORDER BY Timeoriginal" %(originlocation+"%"))


	event = False
	evnumber = 0
	timegap = datetime.timedelta(days=0, seconds=gap, microseconds=0, milliseconds=0, minutes=0, hours=0)
	msg = "Group option is activated (-gap option). I will group Pictures closer than " + str(timegap) + " in an event day."
	print (msg); logging.info (msg)


	for i in cursor:
		evnumber += 1
		Fullfilepath1, Timestr = i
		TimeOriginal1 = datetime.datetime.strptime (Timestr, '%Y-%m-%d %H:%M:%S')
		if evnumber == 1 :
			TimeOriginal0 = TimeOriginal1
			Fullfilepath0 = Fullfilepath1
			continue
		diff = TimeOriginal1-TimeOriginal0
		if diff <= timegap :
			logging.debug ('this picture is part of an event with the preceding one')
			con.execute ("UPDATE files set Event='EVENT' where Fullfilepath = '%s' " %(Fullfilepath0))
			con.execute ("UPDATE files set Event='EVENT' where Fullfilepath = '%s' " %(Fullfilepath1))		
		else:
			logging.debug ('this picture is not part of an event with the preceding one')
		#rolling one position to compare
		TimeOriginal0 = TimeOriginal1
		Fullfilepath0 = Fullfilepath1
	con.commit()


exit()



#3) Deliver items
for i in Allitemscl:
	event = False
	eventname = ''
	a = i.abspath  # item's fullpath and filename

	if preservealbums == True and a.find ('_/') != -1 :
		if a.startswith (destination) :
			logging.debug ('Item %s was not included (Preserving album folder at destination location)' %(a) )
			continue
		else:
			dest = os.path.join(destination, a[len(originlocation)+1:]) # Just to moving to destination preserving path

	else:
		if i.TimeOriginal == None:
			dest = os.path.join(destination, "nodate", os.path.basename(a))

		else:
			# Check origin dir Structure for an already event name
			expr = "/[12]\d{3}[-_ ]?[01]\d?(?P<XeventnameX>.*)/"
			mo = re.search(expr, a)
			try:
				mo.group()
			except:
				pass
			else:
				event = True
				eventname = mo.group('XeventnameX')

			expr = "/[12]\d{3}[-_ ]?[01]\d[-_ ]?[0-3]\d ?(?P<XeventnameX>.*)/"
			mo = re.search(expr, a)
			try:
				mo.group()
			except:
				pass
			else:
				event = True
				eventname = mo.group('XeventnameX')


			# retrieve the name & set Even-Flag to True
			if event == True:
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
		logging.debug ('Doing nothing with this file, is inthe gap of the latest files and donotmovelastmedia is set to True.' + a)
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

	# Perform file operations
	if a == dest :
		#print ('the file does not need to be moved:', a)
		logging.warning('this file remains at the same location:'+dest)
	else:
		if itemcheck (dest) != '':
			#print ('destination for this item already exists', a)
			logging.warning('destination item already exists:' + dest)
			if i.filebytes == os.path.getsize(dest): #___bytes are equal ___:
				finalcopymode = 'd'
				#print ('Duplicated file has been deleted. (same name and size)', a)
				logging.warning ('Duplicated file has been deleted. (same name and size):' + a )
				if args.dummy != True:
					os.remove (a)
			else:
				dest = os.path.join (originlocation,'Duplicates', dest [len(originlocation)+2:])
				finalcopymode = 'm'
		if finalcopymode != 'd' :
			if itemcheck (os.path.dirname(dest)) == '':
					if args.dummy != True:
						os.makedirs (os.path.dirname(dest))
			if finalcopymode == 'c':
				if args.dummy != True:
					shutil.copy (a, dest)
				#print ('FILE COPIED:', a, dest)
				logging.debug('file successfully copied: '+ dest)
				continue
			else:
				if args.dummy != True:
					shutil.move (a, dest)
				#print ('FILE MOVED:', a, dest)
				logging.debug('file successfully moved: '+ dest)

		# Clening empty directories
		if cleaning == True:
			scandir = os.path.dirname (a)
			contents = glob (os.path.join(scandir,'*'))
			#print (contents)
			if len (contents) == 0 and scandir != os.path.normpath(originlocation):
				if args.dummy != True:
					shutil.rmtree (scandir)
				#print ('\n','deleting dir:', scandir,'\n')
				logging.debug ('Directory %s has been deleted (was empty)'%(a,))
#4) Done
print ('Done!')
''' print a little resumen '''