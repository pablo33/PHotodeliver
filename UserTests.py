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


class single_input (unittest.TestCase):
	""" Single photo input and processing TestPack1 """

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
			 -ol Test_examples_container/UserTests/Test1/originlocation \
			 -dl Test_examples_container/UserTests/Test1/destlocation \
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
			 '
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
			 -ol Test_examples_container/UserTests/Test1/originlocation \
			 -dl Test_examples_container/UserTests/Test1/destlocation \
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
			 '
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
			consider destination files is active

			'''

		SetTestPack (self.reftest)
		os.system ('python3 PhotodeliverII.py \
			 -ol Test_examples_container/UserTests/Test1/originlocation \
			 -dl Test_examples_container/UserTests/Test1/destlocation \
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
			 '
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



if __name__ == '__main__':
	unittest.main()