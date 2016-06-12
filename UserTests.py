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
	""" Single photo input and processing
	copymode is copy, no renaming files, but rename movies is active. """

	reftest = 'Test1'
	testfolder = os.path.join (dyntestfolder,reftest)
	SetTestPack (reftest)

	os.system ('python3 PhotodeliverII.py \
	 -ol Test_examples_container/UserTests/Test1/originlocation \
	 -dl Test_examples_container/UserTests/Test1/destlocation \
	 -rm 0 \
	 -rp 0 \
	 -minp 0 \
	 -gap 0 \
	 -cpmode c \
	 -mef 0 \
	 -it 1 \
	 -pa 1 \
	 -faff 0 \
	 -clean 1 \
	 -sfm 0 \
	 -conv 0 \
	 '
	 )

	known_values = set ([

		'Test_examples_container/UserTests/Test1/originlocation',
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


	def test_mycase (self):
		result = FetchFileSet (self.testfolder)
		self.assertEqual(self.known_values, result)

if __name__ == '__main__':
	unittest.main()