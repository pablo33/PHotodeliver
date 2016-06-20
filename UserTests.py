#!/usr/bin/python3

''' This script moves camera file-media to a folder on our hard disk.
	it will group files in foldes due to its date of creation 
	it also manages duplicated files (same name and bytes)'''

# Module import
import unittest
import os, shutil  #sys, logging, datetime, time, re
from glob import glob

from PhotodeliverII import addchilddirectory, lsdirectorytree

dyntestfolder = 'Test_examples_container/UserTests'


def SetTestPack (namepack):
	namepack = os.path.join(dyntestfolder, namepack)
	# delete old contents
	if os.path.isdir (namepack):
		shutil.rmtree (namepack)

	# decompress pack
	os.system ('unzip %s.zip -d %s'%(namepack, dyntestfolder))

def FetchFileSet (path):
	''' Fetchs a file set of files and folders'''
	listree = lsdirectorytree (path)
	fileset = set()
	for x in listree:
		contentlist = (glob( os.path.join (x,'*')))
		for a in contentlist:
			fileset.add (a)
	return fileset



class TestPack1 (unittest.TestCase):
	''' Single photo input and processing TestPack1 '''

	reftest = 'Test1'
	testfolder = os.path.join (dyntestfolder,reftest)


	def test_simplecopy (self):
		''' Simple copy for processing files,
			clear is no active
			files in .Trash folder are not processed
			preserve albums is active:
				tested with 1 folder and picture at originlocation
			consider destination files is not active

			'''

		SetTestPack (self.reftest)
		os.system ('python3 PhotodeliverII.py \
			 -ol %(testfolder)s/originlocation \
			 -dl %(testfolder)s/destlocation \
			 -rm 0 \
			 -rp 0 \
			 -minp 0 \
			 -gap 0 \
			 -cpmode c \
			 -cdi 0 \
			 -mef 0 \
			 -it 1 \
			 -pa 1 \
			 -faff 0 \
			 -clean 0 \
			 -sfm 0 \
			 -conv 0 \
			 '%{'testfolder':self.testfolder}
			 )

		known_values = set ([
			'Test_examples_container/UserTests/Test1/originlocation',
			'Test_examples_container/UserTests/Test1/originlocation/my inmutable album_',
			'Test_examples_container/UserTests/Test1/originlocation/my inmutable album_/picture from my inmutable album 2016-06-12 19-47-56.png',
			'Test_examples_container/UserTests/Test1/originlocation/.Trash/My trashed file.jpg',
			'Test_examples_container/UserTests/Test1/originlocation/2004-03',
			'Test_examples_container/UserTests/Test1/originlocation/2004-03/Pathdate2-Screenshot.png',
			'Test_examples_container/UserTests/Test1/originlocation/2006',
			'Test_examples_container/UserTests/Test1/originlocation/2006/07',
			'Test_examples_container/UserTests/Test1/originlocation/2006/07/Pathdate-Screenshot.png',
			'Test_examples_container/UserTests/Test1/originlocation/2010-05-07 namedatedrop.avi',
			'Test_examples_container/UserTests/Test1/originlocation/img_1771.jpg',
			'Test_examples_container/UserTests/Test1/originlocation/20160606_195355.jpg',
			'Test_examples_container/UserTests/Test1/originlocation/Screenshot from 2016-06-07 23-45-47.png',
			'Test_examples_container/UserTests/Test1/originlocation/drop.avi',
			'Test_examples_container/UserTests/Test1/destlocation',
			'Test_examples_container/UserTests/Test1/destlocation/existent folder',
			'Test_examples_container/UserTests/Test1/destlocation/existent folder/file at dest location 2016-06-12 20-06-29.png',
			'Test_examples_container/UserTests/Test1/destlocation/2002-03',
			'Test_examples_container/UserTests/Test1/destlocation/2002-03/file already at dest folder.png',
			'Test_examples_container/UserTests/Test1/destlocation/2004',
			'Test_examples_container/UserTests/Test1/destlocation/2004/2004-03',
			'Test_examples_container/UserTests/Test1/destlocation/2004/2004-03/Pathdate2-Screenshot.png',
			'Test_examples_container/UserTests/Test1/destlocation/2006',
			'Test_examples_container/UserTests/Test1/destlocation/2006/2006-07',
			'Test_examples_container/UserTests/Test1/destlocation/2006/2006-07/Pathdate-Screenshot.png',
			'Test_examples_container/UserTests/Test1/destlocation/2010',
			'Test_examples_container/UserTests/Test1/destlocation/2010/2010-05',
			'Test_examples_container/UserTests/Test1/destlocation/2010/2010-05/2010-05-07 namedatedrop.avi',
			'Test_examples_container/UserTests/Test1/destlocation/nodate',
			'Test_examples_container/UserTests/Test1/destlocation/nodate/drop.avi',
			'Test_examples_container/UserTests/Test1/destlocation/2003',
			'Test_examples_container/UserTests/Test1/destlocation/2003/2003-12',
			'Test_examples_container/UserTests/Test1/destlocation/2003/2003-12/img_1771.jpg',
			'Test_examples_container/UserTests/Test1/destlocation/2016',
			'Test_examples_container/UserTests/Test1/destlocation/2016/2016-06',
			'Test_examples_container/UserTests/Test1/destlocation/2016/2016-06/20160606_195355.jpg',
			'Test_examples_container/UserTests/Test1/destlocation/2016/2016-06/Screenshot from 2016-06-07 23-45-47.png',
			])

		result = FetchFileSet (self.testfolder)
		self.assertEqual(known_values, result)


	def test_movemodeactive (self):
		''' Move option is active
			clear is no active
			files in .Trash folder are not processed
			preserve albums is active:
				tested with 1 folder and picture at originlocation
			consider destination files is active
			'''

		SetTestPack (self.reftest)
		os.system ('python3 PhotodeliverII.py \
			 -ol %(testfolder)s/originlocation \
			 -dl %(testfolder)s/destlocation \
			 -rm 0 \
			 -rp 0 \
			 -minp 0 \
			 -gap 0 \
			 -cpmode m \
			 -cdi 1 \
			 -mef 0 \
			 -it 1 \
			 -pa 1 \
			 -faff 0 \
			 -clean 0 \
			 -sfm 0 \
			 -conv 0 \
			 '%{'testfolder':self.testfolder}
			 )

		known_values = set ([

			'Test_examples_container/UserTests/Test1/originlocation',
			'Test_examples_container/UserTests/Test1/originlocation/my inmutable album_',
			'Test_examples_container/UserTests/Test1/originlocation/my inmutable album_/picture from my inmutable album 2016-06-12 19-47-56.png',
			'Test_examples_container/UserTests/Test1/originlocation/.Trash/My trashed file.jpg',
			'Test_examples_container/UserTests/Test1/originlocation/2004-03',
			'Test_examples_container/UserTests/Test1/originlocation/2006/07',
			'Test_examples_container/UserTests/Test1/originlocation/2006',
			'Test_examples_container/UserTests/Test1/destlocation',
			'Test_examples_container/UserTests/Test1/destlocation/existent folder',
			'Test_examples_container/UserTests/Test1/destlocation/existent folder/file at dest location 2016-06-12 20-06-29.png',
			'Test_examples_container/UserTests/Test1/destlocation/2002-03',
			'Test_examples_container/UserTests/Test1/destlocation/2002-03/file already at dest folder.png',
			'Test_examples_container/UserTests/Test1/destlocation/2004',
			'Test_examples_container/UserTests/Test1/destlocation/2004/2004-03',
			'Test_examples_container/UserTests/Test1/destlocation/2004/2004-03/Pathdate2-Screenshot.png',
			'Test_examples_container/UserTests/Test1/destlocation/2006',
			'Test_examples_container/UserTests/Test1/destlocation/2006/2006-07',
			'Test_examples_container/UserTests/Test1/destlocation/2006/2006-07/Pathdate-Screenshot.png',
			'Test_examples_container/UserTests/Test1/destlocation/2010',
			'Test_examples_container/UserTests/Test1/destlocation/2010/2010-05',
			'Test_examples_container/UserTests/Test1/destlocation/2010/2010-05/2010-05-07 namedatedrop.avi',
			'Test_examples_container/UserTests/Test1/destlocation/nodate',
			'Test_examples_container/UserTests/Test1/destlocation/nodate/drop.avi',
			'Test_examples_container/UserTests/Test1/destlocation/2003',
			'Test_examples_container/UserTests/Test1/destlocation/2003/2003-12',
			'Test_examples_container/UserTests/Test1/destlocation/2003/2003-12/img_1771.jpg',
			'Test_examples_container/UserTests/Test1/destlocation/2016',
			'Test_examples_container/UserTests/Test1/destlocation/2016/2016-06',
			'Test_examples_container/UserTests/Test1/destlocation/2016/2016-06/20160606_195355.jpg',
			'Test_examples_container/UserTests/Test1/destlocation/2016/2016-06/Screenshot from 2016-06-07 23-45-47.png',
			])

		result = FetchFileSet (self.testfolder)
		self.assertEqual(known_values, result)


	def test_movemodeactive_clearfolders (self):
		''' Move option is active,
			clear folders 0
			files in .Trash folder are processed
			preserve albums is not active:
				tested with 1 folder and picture at originlocation
			consider destination files is active, but there is not enough files to be cosidered.

			'''

		SetTestPack (self.reftest)
		os.system ('python3 PhotodeliverII.py \
			 -ol %(testfolder)s/originlocation \
			 -dl %(testfolder)s/destlocation \
			 -rm 0 \
			 -rp 0 \
			 -minp 0 \
			 -gap 0 \
			 -cpmode m \
			 -cdi 1 \
			 -mef 0 \
			 -it 0 \
			 -pa 0 \
			 -faff 0 \
			 -clean 1 \
			 -sfm 0 \
			 -conv 0 \
			 '%{'testfolder':self.testfolder}
			 )

		known_values = set ([

			'Test_examples_container/UserTests/Test1/originlocation',
			'Test_examples_container/UserTests/Test1/destlocation',
			'Test_examples_container/UserTests/Test1/destlocation/existent folder',
			'Test_examples_container/UserTests/Test1/destlocation/existent folder/file at dest location 2016-06-12 20-06-29.png',
			'Test_examples_container/UserTests/Test1/destlocation/2002-03',
			'Test_examples_container/UserTests/Test1/destlocation/2002-03/file already at dest folder.png',			
			'Test_examples_container/UserTests/Test1/destlocation/2004',
			'Test_examples_container/UserTests/Test1/destlocation/2004/2004-03',
			'Test_examples_container/UserTests/Test1/destlocation/2004/2004-03/Pathdate2-Screenshot.png',
			'Test_examples_container/UserTests/Test1/destlocation/2006',
			'Test_examples_container/UserTests/Test1/destlocation/2006/2006-07',
			'Test_examples_container/UserTests/Test1/destlocation/2006/2006-07/Pathdate-Screenshot.png',
			'Test_examples_container/UserTests/Test1/destlocation/2010',
			'Test_examples_container/UserTests/Test1/destlocation/2010/2010-05',
			'Test_examples_container/UserTests/Test1/destlocation/2010/2010-05/2010-05-07 namedatedrop.avi',
			'Test_examples_container/UserTests/Test1/destlocation/nodate',
			'Test_examples_container/UserTests/Test1/destlocation/nodate/drop.avi',
			'Test_examples_container/UserTests/Test1/destlocation/2003',
			'Test_examples_container/UserTests/Test1/destlocation/2003/2003-12',
			'Test_examples_container/UserTests/Test1/destlocation/2003/2003-12/img_1771.jpg',
			'Test_examples_container/UserTests/Test1/destlocation/2003/2003-12/My trashed file.jpg',
			'Test_examples_container/UserTests/Test1/destlocation/2016',
			'Test_examples_container/UserTests/Test1/destlocation/2016/2016-06',
			'Test_examples_container/UserTests/Test1/destlocation/2016/2016-06/picture from my inmutable album 2016-06-12 19-47-56.png',
			'Test_examples_container/UserTests/Test1/destlocation/2016/2016-06/20160606_195355.jpg',
			'Test_examples_container/UserTests/Test1/destlocation/2016/2016-06/Screenshot from 2016-06-07 23-45-47.png',
			])

		result = FetchFileSet (self.testfolder)
		self.assertEqual(known_values, result)

class TestPack2 (unittest.TestCase):
	''' Multiple photo handling and processing, TestPack2 '''

	reftest = 'Test2'
	testfolder = os.path.join (dyntestfolder,reftest)


	def test_simplegroup (self):
		''' Simple grouping in events, (5 minimun pictures in this test)
			clear folders is active
			consider destination files is active and
			moveexistent files is also active. this will move the files on destination folder.
			'''

		SetTestPack (self.reftest)
		os.system ('python3 PhotodeliverII.py \
			 -ol %(testfolder)s/originlocation \
			 -dl %(testfolder)s/destlocation \
			 -rm 0 \
			 -rp 0 \
			 -minp 5 \
			 -gap 28800 \
			 -cpmode m \
			 -cdi 1 \
			 -mef 1 \
			 -it 1 \
			 -pa 1 \
			 -faff 0 \
			 -clean 1 \
			 -sfm 0 \
			 -conv 0 \
			 '%{'testfolder':self.testfolder}
			 )

		known_values = set ([
			'Test_examples_container/UserTests/Test2/originlocation',
			'Test_examples_container/UserTests/Test2/destlocation',
			'Test_examples_container/UserTests/Test2/destlocation/2015',
			'Test_examples_container/UserTests/Test2/destlocation/2015/2015-12',
			'Test_examples_container/UserTests/Test2/destlocation/2015/2015-12/Screenshot from 2015-12-13 23-20-58.png',
			'Test_examples_container/UserTests/Test2/destlocation/2015/2015-12/Screenshot from 2015-12-13 23-20-33.png',
			'Test_examples_container/UserTests/Test2/destlocation/2015/2015-12/Screenshot from 2015-12-13 23-20-49.png',
			'Test_examples_container/UserTests/Test2/destlocation/2016',
			'Test_examples_container/UserTests/Test2/destlocation/2016/2016-06-13',
			'Test_examples_container/UserTests/Test2/destlocation/2016/2016-06-13/Screenshot from 2016-06-13 23-17-06.png',
			'Test_examples_container/UserTests/Test2/destlocation/2016/2016-06-13/Screenshot from 2016-06-13 23-17-20.png',
			'Test_examples_container/UserTests/Test2/destlocation/2016/2016-06-13/Screenshot from 2016-06-13 23-17-13.png',
			'Test_examples_container/UserTests/Test2/destlocation/2016/2016-06-13/Screenshot from 2016-06-13 23-17-26.png',
			'Test_examples_container/UserTests/Test2/destlocation/2016/2016-06-13/Screenshot from 2016-06-13 23-16-48.png',
			'Test_examples_container/UserTests/Test2/destlocation/2016/2016-06-13/Screenshot from 2016-06-13 23-17-00.png',
			'Test_examples_container/UserTests/Test2/destlocation/2014',
			'Test_examples_container/UserTests/Test2/destlocation/2014/2014-05-10',
			'Test_examples_container/UserTests/Test2/destlocation/2014/2014-05-10/Screenshot from 2014-05-10_1.png',
			'Test_examples_container/UserTests/Test2/destlocation/2014/2014-05-10/Screenshot from 2014-05-10_4.png',
			'Test_examples_container/UserTests/Test2/destlocation/2014/2014-05-10/Screenshot from 2014-05-10_3.png',
			'Test_examples_container/UserTests/Test2/destlocation/2014/2014-05-10/Screenshot from 2014-05-10_2.png',
			'Test_examples_container/UserTests/Test2/destlocation/2014/2014-05-10/Screenshot from 2014-05-10_5.png',
			'Test_examples_container/UserTests/Test2/destlocation/2003/2003-03-21/Screenshot from 2003-03-21_1.png',
			'Test_examples_container/UserTests/Test2/destlocation/2003',
			'Test_examples_container/UserTests/Test2/destlocation/2003/2003-03-21',
			'Test_examples_container/UserTests/Test2/destlocation/2003/2003-03-21/Screenshot from 2003-03-21_2.png',
			'Test_examples_container/UserTests/Test2/destlocation/2003/2003-03-21/Screenshot from 2003-03-21_3.png',
			'Test_examples_container/UserTests/Test2/destlocation/2003/2003-03-21/Screenshot from 2003-03-21_4 already on dest folder.png',
			'Test_examples_container/UserTests/Test2/destlocation/2003/2003-03-21/Screenshot from 2003-03-21_5 already on destination.png',
			])

		result = FetchFileSet (self.testfolder)
		self.assertEqual(known_values, result)

	def test_simplegroup2 (self):
		''' Simple grouping in events, (5 minimun pictures in this test)
			clear folders is active
			consider destination files is active and
			moveexistent files not active. this will Preserve files on destination folder.
			'''

		SetTestPack (self.reftest)
		os.system ('python3 PhotodeliverII.py \
			 -ol %(testfolder)s/originlocation \
			 -dl %(testfolder)s/destlocation \
			 -rm 0 \
			 -rp 0 \
			 -minp 5 \
			 -gap 28800 \
			 -cpmode m \
			 -cdi 1 \
			 -mef 0 \
			 -it 1 \
			 -pa 1 \
			 -faff 0 \
			 -clean 1 \
			 -sfm 0 \
			 -conv 0 \
			 '%{'testfolder':self.testfolder}
			 )

		known_values = set ([
			'Test_examples_container/UserTests/Test2/originlocation',
			'Test_examples_container/UserTests/Test2/destlocation',
			'Test_examples_container/UserTests/Test2/destlocation/2015',
			'Test_examples_container/UserTests/Test2/destlocation/2015/2015-12',
			'Test_examples_container/UserTests/Test2/destlocation/2015/2015-12/Screenshot from 2015-12-13 23-20-58.png',
			'Test_examples_container/UserTests/Test2/destlocation/2015/2015-12/Screenshot from 2015-12-13 23-20-33.png',
			'Test_examples_container/UserTests/Test2/destlocation/2015/2015-12/Screenshot from 2015-12-13 23-20-49.png',
			'Test_examples_container/UserTests/Test2/destlocation/2016',
			'Test_examples_container/UserTests/Test2/destlocation/2016/2016-06-13',
			'Test_examples_container/UserTests/Test2/destlocation/2016/2016-06-13/Screenshot from 2016-06-13 23-17-06.png',
			'Test_examples_container/UserTests/Test2/destlocation/2016/2016-06-13/Screenshot from 2016-06-13 23-17-20.png',
			'Test_examples_container/UserTests/Test2/destlocation/2016/2016-06-13/Screenshot from 2016-06-13 23-17-13.png',
			'Test_examples_container/UserTests/Test2/destlocation/2016/2016-06-13/Screenshot from 2016-06-13 23-17-26.png',
			'Test_examples_container/UserTests/Test2/destlocation/2016/2016-06-13/Screenshot from 2016-06-13 23-16-48.png',
			'Test_examples_container/UserTests/Test2/destlocation/2016/2016-06-13/Screenshot from 2016-06-13 23-17-00.png',
			'Test_examples_container/UserTests/Test2/destlocation/2014',
			'Test_examples_container/UserTests/Test2/destlocation/2014/2014-05-10',
			'Test_examples_container/UserTests/Test2/destlocation/2014/2014-05-10/Screenshot from 2014-05-10_1.png',
			'Test_examples_container/UserTests/Test2/destlocation/2014/2014-05-10/Screenshot from 2014-05-10_4.png',
			'Test_examples_container/UserTests/Test2/destlocation/2014/2014-05-10/Screenshot from 2014-05-10_3.png',
			'Test_examples_container/UserTests/Test2/destlocation/2014/2014-05-10/Screenshot from 2014-05-10_2.png',
			'Test_examples_container/UserTests/Test2/destlocation/2014/2014-05-10/Screenshot from 2014-05-10_5.png',
			'Test_examples_container/UserTests/Test2/destlocation/2003/2003-03-21/Screenshot from 2003-03-21_1.png',
			'Test_examples_container/UserTests/Test2/destlocation/2003',
			'Test_examples_container/UserTests/Test2/destlocation/2003/2003-03-21',
			'Test_examples_container/UserTests/Test2/destlocation/2003/2003-03-21/Screenshot from 2003-03-21_2.png',
			'Test_examples_container/UserTests/Test2/destlocation/2003/2003-03-21/Screenshot from 2003-03-21_3.png',
			'Test_examples_container/UserTests/Test2/destlocation/Screenshot from 2003-03-21_4 already on dest folder.png',
			'Test_examples_container/UserTests/Test2/destlocation/Screenshot from 2003-03-21_5 already on destination.png',
			])

		result = FetchFileSet (self.testfolder)
		self.assertEqual(known_values, result)


class TestPack3 (unittest.TestCase):
	''' Converting files and adding metadata to JPEG files, RenameFiles, TestPack3 '''

	reftest = 'Test3'
	testfolder = os.path.join (dyntestfolder,reftest)

	
	def test_faff (self):
		''' No grouping
			clear folders is active
			storefilemetadata is active
			--forceassignfromfilename 0
			convert files is active
			'''

		SetTestPack (self.reftest)
		os.system ('python3 PhotodeliverII.py \
			 -ol %(testfolder)s/originlocation \
			 -dl %(testfolder)s/destlocation \
			 -rm 0 \
			 -rp 0 \
			 -minp 0 \
			 -gap 0 \
			 -cpmode m \
			 -cdi 0 \
			 -mef 0 \
			 -it 1 \
			 -pa 1 \
			 -faff 0 \
			 -clean 1 \
			 -sfm 1 \
			 -conv 1 \
			 '%{'testfolder':self.testfolder}
			 )

		known_values = set ([
			'Test_examples_container/UserTests/Test3/originlocation',
			'Test_examples_container/UserTests/Test3/destlocation',
			'Test_examples_container/UserTests/Test3/destlocation/2003',
			'Test_examples_container/UserTests/Test3/destlocation/2003/2003-12',
			'Test_examples_container/UserTests/Test3/destlocation/2003/2003-12/img_1771.jpg',
			'Test_examples_container/UserTests/Test3/destlocation/2004',
			'Test_examples_container/UserTests/Test3/destlocation/2004/2004-03',
			'Test_examples_container/UserTests/Test3/destlocation/2004/2004-03/Nooriginalmetadate.jpg',
			'Test_examples_container/UserTests/Test3/destlocation/2016',
			'Test_examples_container/UserTests/Test3/destlocation/2016/2016-06',
			'Test_examples_container/UserTests/Test3/destlocation/2016/2016-06/Screenshot from 2016-06-07 23-45-47.jpg',
			'Test_examples_container/UserTests/Test3/destlocation/2016/2016-06/20160606_195355.jpg',
			'Test_examples_container/UserTests/Test3/destlocation/nodate',
			'Test_examples_container/UserTests/Test3/destlocation/nodate/Nodatenormetadate.jpg',
			'Test_examples_container/UserTests/Test3/destlocation/nodate/drop.avi',
			])

		result = FetchFileSet (self.testfolder)
		self.assertEqual(known_values, result)
		# assert that exif metadata is really stored in resulting pictures.


	def test_faff (self):
		''' No grouping
			clear folders is active
			storefilemetadata is active
			--forceassignfromfilename 1
			convert files is active
			'''

		SetTestPack (self.reftest)
		os.system ('python3 PhotodeliverII.py \
			 -ol %(testfolder)s/originlocation \
			 -dl %(testfolder)s/destlocation \
			 -rm 0 \
			 -rp 0 \
			 -minp 0 \
			 -gap 0 \
			 -cpmode m \
			 -cdi 0 \
			 -mef 0 \
			 -it 1 \
			 -pa 1 \
			 -faff 1 \
			 -clean 1 \
			 -sfm 1 \
			 -conv 1 \
			 '%{'testfolder':self.testfolder}
			 )

		known_values = set ([
			'Test_examples_container/UserTests/Test3/originlocation',
			'Test_examples_container/UserTests/Test3/destlocation',
			'Test_examples_container/UserTests/Test3/destlocation/2003',
			'Test_examples_container/UserTests/Test3/destlocation/2003/2003-12',
			'Test_examples_container/UserTests/Test3/destlocation/2003/2003-12/img_1771.jpg',
			'Test_examples_container/UserTests/Test3/destlocation/2004',
			'Test_examples_container/UserTests/Test3/destlocation/2004/2004-03',
			'Test_examples_container/UserTests/Test3/destlocation/2004/2004-03/Nooriginalmetadate.jpg',
			'Test_examples_container/UserTests/Test3/destlocation/2016',
			'Test_examples_container/UserTests/Test3/destlocation/2016/2016-06',
			'Test_examples_container/UserTests/Test3/destlocation/2016/2016-06/Screenshot from 2016-06-07 23-45-47.jpg',
			'Test_examples_container/UserTests/Test3/destlocation/2016/2016-06/20160606_195355.jpg',
			'Test_examples_container/UserTests/Test3/destlocation/nodate',
			'Test_examples_container/UserTests/Test3/destlocation/nodate/Nodatenormetadate.jpg',
			'Test_examples_container/UserTests/Test3/destlocation/nodate/drop.avi',
			])

		result = FetchFileSet (self.testfolder)
		self.assertEqual(known_values, result)


	def test_renamephotos (self):
		''' No grouping
			clear folders is active
			storefilemetadata is active
			--forceassignfromfilename 0
			--renamephotos is active
			--renamevideos is active
			convert files is active
			'''

		SetTestPack (self.reftest)
		os.system ('python3 PhotodeliverII.py \
			 -ol %(testfolder)s/originlocation \
			 -dl %(testfolder)s/destlocation \
			 -rm 1 \
			 -rp 1 \
			 -minp 0 \
			 -gap 0 \
			 -cpmode m \
			 -cdi 0 \
			 -mef 0 \
			 -it 1 \
			 -pa 1 \
			 -faff 0 \
			 -clean 1 \
			 -sfm 1 \
			 -conv 1 \
			 '%{'testfolder':self.testfolder}
			 )

		known_values = set ([
			'Test_examples_container/UserTests/Test3/originlocation',
			'Test_examples_container/UserTests/Test3/destlocation',
			'Test_examples_container/UserTests/Test3/destlocation/2003',
			'Test_examples_container/UserTests/Test3/destlocation/2003/2003-12',
			'Test_examples_container/UserTests/Test3/destlocation/2003/2003-12/20031214_120144-img_1771.jpg',
			'Test_examples_container/UserTests/Test3/destlocation/2004',
			'Test_examples_container/UserTests/Test3/destlocation/2004/2004-03',
			'Test_examples_container/UserTests/Test3/destlocation/2004/2004-03/20040301_120000-Nooriginalmetadate.jpg',
			'Test_examples_container/UserTests/Test3/destlocation/2016',
			'Test_examples_container/UserTests/Test3/destlocation/2016/2016-06',
			'Test_examples_container/UserTests/Test3/destlocation/2016/2016-06/20160606_195355.jpg',
			'Test_examples_container/UserTests/Test3/destlocation/2016/2016-06/20160607_234547-Screenshot from 2016-06-07 23-45-47.jpg',
			'Test_examples_container/UserTests/Test3/destlocation/nodate',
			'Test_examples_container/UserTests/Test3/destlocation/nodate/drop.avi',
			'Test_examples_container/UserTests/Test3/destlocation/nodate/Nodatenormetadate.jpg',
			])

		result = FetchFileSet (self.testfolder)
		self.assertEqual(known_values, result)
		# assert that exif metadata is really stored in resulting pictures.


class TestPack4 (unittest.TestCase):
	''' Retrieving event names, RenameFiles, TestPack4 '''

	reftest = 'Test4'
	testfolder = os.path.join (dyntestfolder,reftest)

	
	def test_faff (self):
		''' No grouping
			clear folders is active
			storefilemetadata is active
			--forceassignfromfilename 1
			convert files is active
			'''

		SetTestPack (self.reftest)
		os.system ('python3 PhotodeliverII.py \
			 -ol %(testfolder)s/originlocation \
			 -dl %(testfolder)s/destlocation \
			 -rm 1 \
			 -rp 1 \
			 -minp 5 \
			 -gap 28800 \
			 -cpmode m \
			 -cdi 1 \
			 -mef 1 \
			 -it 1 \
			 -pa 1 \
			 -faff 1 \
			 -clean 1 \
			 -sfm 1 \
			 -conv 1 \
			 '%{'testfolder':self.testfolder}
			 )

		known_values = set ([
			'Test_examples_container/UserTests/Test4/originlocation',
			'Test_examples_container/UserTests/Test4/destlocation',
			'Test_examples_container/UserTests/Test4/destlocation/2003',
			'Test_examples_container/UserTests/Test4/destlocation/2003/2003-03-21 Same day but another event',
			'Test_examples_container/UserTests/Test4/destlocation/2003/2003-03-21 Same day but another event/20030321_120000-Screenshot from 2003-03-21_1.jpg',
			'Test_examples_container/UserTests/Test4/destlocation/2003/2003-03-21 Same day but another event/20030321_120000-Screenshot from 2003-03-21_2.jpg',
			'Test_examples_container/UserTests/Test4/destlocation/2003/2003-03-21 Same day but another event/20030321_120000-Screenshot from 2003-03-21_3.jpg',
			'Test_examples_container/UserTests/Test4/destlocation/2003/2003-03-21 already an event named',
			'Test_examples_container/UserTests/Test4/destlocation/2003/2003-03-21 already an event named/20030321_120000-Screenshot from 2003-03-21_5 already on destination.jpg',
			'Test_examples_container/UserTests/Test4/destlocation/2003/2003-03-21 already an event named/20030321_120000-Screenshot from 2003-03-21_4 already on dest folder.jpg',
			'Test_examples_container/UserTests/Test4/destlocation/2014',
			'Test_examples_container/UserTests/Test4/destlocation/2014/2014-05-10',
			'Test_examples_container/UserTests/Test4/destlocation/2014/2014-05-10/20140510_120000-Screenshot from 2014-05-10_5.jpg',
			'Test_examples_container/UserTests/Test4/destlocation/2014/2014-05-10/20140510_120000-Screenshot from 2014-05-10_4.jpg',
			'Test_examples_container/UserTests/Test4/destlocation/2014/2014-05-10/20140510_120000-Screenshot from 2014-05-10_2.jpg',
			'Test_examples_container/UserTests/Test4/destlocation/2014/2014-05-10/20140510_120000-Screenshot from 2014-05-10_3.jpg',
			'Test_examples_container/UserTests/Test4/destlocation/2015',
			'Test_examples_container/UserTests/Test4/destlocation/2014/2014-05-10/20140510_120000-Screenshot from 2014-05-10_1.jpg',
			'Test_examples_container/UserTests/Test4/destlocation/2015/2015-12/20151213_232033-Screenshot from 2015-12-13 23-20-33.jpg',
			'Test_examples_container/UserTests/Test4/destlocation/2015/2015-12',
			'Test_examples_container/UserTests/Test4/destlocation/2015/2015-12/20151213_232049-Screenshot from 2015-12-13 23-20-49.jpg',
			'Test_examples_container/UserTests/Test4/destlocation/2015/2015-12/20151213_232058-Screenshot from 2015-12-13 23-20-58.jpg',
			'Test_examples_container/UserTests/Test4/destlocation/2016',
			'Test_examples_container/UserTests/Test4/destlocation/2016/2016-06-13 Event name 01',
			'Test_examples_container/UserTests/Test4/destlocation/2016/2016-06-13 Event name 01/20160613_231713-Screenshot from 2016-06-13 23-17-13.jpg',
			'Test_examples_container/UserTests/Test4/destlocation/2016/2016-06-13 Event name 01/20160613_231648-Screenshot from 2016-06-13 23-16-48.jpg',
			'Test_examples_container/UserTests/Test4/destlocation/2016/2016-06-13 Event name 01/20160613_231706-Screenshot from 2016-06-13 23-17-06.jpg',
			'Test_examples_container/UserTests/Test4/destlocation/2016/2016-06-13 Event name 01/20160613_231720-Screenshot from 2016-06-13 23-17-20.jpg',
			'Test_examples_container/UserTests/Test4/destlocation/2016/2016-06-13 Event name 01/20160613_231726-Screenshot from 2016-06-13 23-17-26.jpg',
			'Test_examples_container/UserTests/Test4/destlocation/2016/2016-06-13 Event name 01/20160613_231700-Screenshot from 2016-06-13 23-17-00.jpg',
			])

		result = FetchFileSet (self.testfolder)
		self.assertEqual(known_values, result)
		# assert that exif metadata is really stored in resulting pictures.


class TestPack5 (unittest.TestCase):
	''' The duplicated files test, TestPack5 '''

	reftest = 'Test5'
	testfolder = os.path.join (dyntestfolder,reftest)

	
	def test_simpleduplicates (self):
		''' No grouping
			clear folders is active
			'''

		SetTestPack (self.reftest)
		os.system ('python3 PhotodeliverII.py \
			 -ol %(testfolder)s/originlocation \
			 -dl %(testfolder)s/destlocation \
			 -rm 0 \
			 -rp 0 \
			 -minp 0 \
			 -gap 0 \
			 -cpmode m \
			 -cdi 1 \
			 -mef 1 \
			 -it 1 \
			 -pa 1 \
			 -faff 0 \
			 -clean 1 \
			 -sfm 0 \
			 -conv 1 \
			 '%{'testfolder':self.testfolder}
			 )

		known_values = set ([
			'Test_examples_container/UserTests/Test5/destlocation',
			'Test_examples_container/UserTests/Test5/destlocation/2003',
			'Test_examples_container/UserTests/Test5/destlocation/2003/2003-03',
			'Test_examples_container/UserTests/Test5/destlocation/2003/2003-03/Screenshot from 2003-03-21_1.jpg',
			'Test_examples_container/UserTests/Test5/destlocation/2003/2003-12',
			'Test_examples_container/UserTests/Test5/destlocation/2003/2003-12/single file dup at dest - img_1771.jpg',
			'Test_examples_container/UserTests/Test5/destlocation/2014',
			'Test_examples_container/UserTests/Test5/destlocation/2014/2014-03',
			'Test_examples_container/UserTests/Test5/destlocation/2014/2014-03/2014-03-02 To be converted and already in jpg(0).jpg',
			'Test_examples_container/UserTests/Test5/destlocation/2014/2014-03/2014-03-02 To be converted and already in jpg.jpg',
			'Test_examples_container/UserTests/Test5/destlocation/2015',
			'Test_examples_container/UserTests/Test5/destlocation/2015/2015-12',
			'Test_examples_container/UserTests/Test5/destlocation/2015/2015-12/Screenshot from 2015-12-13 23-20-33.jpg',
			'Test_examples_container/UserTests/Test5/destlocation/2015/2015-12/Screenshot from 2015-12-13 23-20-49.jpg',
			'Test_examples_container/UserTests/Test5/destlocation/2015/2015-12/Screenshot from 2015-12-13 23-20-58.jpg',
			'Test_examples_container/UserTests/Test5/originlocation',
			'Test_examples_container/UserTests/Test5/originlocation/do not touch this album_',
			'Test_examples_container/UserTests/Test5/originlocation/do not touch this album_/Screenshot from 2016-06-13 23-16-48.png',
			'Test_examples_container/UserTests/Test5/originlocation/do not touch this album_/Screenshot from 2016-06-13 23-17-00.png',
			'Test_examples_container/UserTests/Test5/originlocation/do not touch this album_/Screenshot from 2016-06-13 23-17-06.png',
			'Test_examples_container/UserTests/Test5/originlocation/do not touch this album_/Screenshot from 2016-06-13 23-17-13.png',
			'Test_examples_container/UserTests/Test5/originlocation/do not touch this album_/Screenshot from 2016-06-13 23-17-20.png',
			'Test_examples_container/UserTests/Test5/originlocation/do not touch this album_/Screenshot from 2016-06-13 23-17-26.png',
			'Test_examples_container/UserTests/Test5/originlocation/duplicates',
			'Test_examples_container/UserTests/Test5/originlocation/duplicates/3 files duplicated',
			'Test_examples_container/UserTests/Test5/originlocation/duplicates/3 files duplicated/Screenshot from 2015-12-13 23-20-33.jpg',
			'Test_examples_container/UserTests/Test5/originlocation/duplicates/3 files duplicated/Screenshot from 2015-12-13 23-20-49.jpg',
			'Test_examples_container/UserTests/Test5/originlocation/duplicates/3 files duplicated/Screenshot from 2015-12-13 23-20-58.jpg',
			'Test_examples_container/UserTests/Test5/destlocation/nodate/Nodatenormetadate(0).jpg',
			'Test_examples_container/UserTests/Test5/destlocation/nodate',
			'Test_examples_container/UserTests/Test5/destlocation/nodate/Nodatenormetadate.jpg',
			])

		result = FetchFileSet (self.testfolder)
		self.assertEqual(known_values, result)
		# assert that exif metadata is really stored in resulting pictures.


if __name__ == '__main__':
	unittest.main()