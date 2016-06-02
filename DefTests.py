#!/usr/bin/python3
# Test Configuration
import unittest
import PhotodeliverII




#####TESTS########


class itemcheck_text_values (unittest.TestCase):
	'''testing itemcheck function'''
	def test_emptystring (self):
		''' an empty string returns another empty string'''
		self.assertEqual (PhotodeliverII.itemcheck(""),"")

	def test_itemcheck (self):
		''' only text are addmitted as input '''
		sample_bad_values = (True, False, None, 33, 3.5)
		for values in sample_bad_values:
			self.assertRaises (PhotodeliverII.NotStringError, PhotodeliverII.itemcheck, values)

	def test_malformed_paths (self):
		''' malformed path as inputs are ommited and raises an error '''
		malformed_values = ("///","/home//")
		for inputstring in malformed_values:
			self.assertRaises (PhotodeliverII.MalformedPathError, PhotodeliverII.itemcheck, inputstring)

class to2_function (unittest.TestCase):
	known_values = ( (1, "01"),
					(2, "02"),
					(3, "03"),
					(4, "04"),
					(5, "05"),
					(6, "06"),
					(7, "07"),
					(8, "08"),
					(9, "09"),
					(10, "10"),
					(11, "11"),
					(12, "12"))
	def test_to2 (self):
		'''Testing all digits 1 to 12), should return a string with two characters'''
		for integer, string in self.known_values:
			result = PhotodeliverII.to2 (integer)
			self.assertEqual(string, result)

class to2_bad_input_function (unittest.TestCase):
	mad_values = (0,13,15,-3)
	
	def test_too_large (self):
		''' to2 should fail with large input'''
		for integer in self.mad_values:
			self.assertRaises(PhotodeliverII.OutOfRangeError, PhotodeliverII.to2, integer)


	mad_inputs = ("0", None, False, True)
	
	def test_bad_input (self):
		''' to2 should only accept integers as input'''
		for data in self.mad_inputs:
			self.assertRaises (PhotodeliverII.NotIntegerError, PhotodeliverII.to2, data)

class addslash_tests (unittest.TestCase):
	""" Testing addslash function """
	known_values = (
		("path", "path/"),
		("/path", "/path/"),
		("path/", "path/"),
		("/home/path/to/somewhere", "/home/path/to/somewhere/"),
		("","")
		)
	def test_some_strings (self):
		''' any string must end in a slash if it hasn't any '''
		for string, string2 in self.known_values:
			result = PhotodeliverII.addslash(string)
			self.assertEqual (string2, result)

	mad_inputs = (0, 33, None, False, True)
	
	def test_bad_input (self):
		''' addslash should only accept strings as input'''
		for data in self.mad_inputs:
			self.assertRaises (PhotodeliverII.NotStringError, PhotodeliverII.addslash, data)

class readmetadate_test (unittest.TestCase):
	""" tests for readmetadate function
	it must read some metadate values """
	metadateobject = PhotodeliverII.GExiv2.Metadata('Test_examples_container/Single_image/img_1771.jpg')
	known_values = (
		("Exif.Image.Make", "Canon"),
		("Exif.Image.Model", "Canon PowerShot S40"),
		("Exif.Image.DateTime","2003:12:14 12:01:44"),
		("Exif.Photo.DateTimeOriginal", "2003:12:14 12:01:44"),
		("Exif.Photo.DateTimeDigitized", "2003:12:14 12:01:44"),
		("Exif.Photo.ExposureTime","1/500"),
		("Exif.INEXISTENT.label", None),
		("", None),
		)

	def test_some_inputs (self):
		for label, MTstring in self.known_values:
			result = self.metadateobject.get(label)
			self.assertEqual (MTstring, result)

class addchilddirectory_test (unittest.TestCase):
	"""Tests for addchilddirectory_test """
	known_values = (("Test_examples_container/FolderStructure",
		[
		'Test_examples_container/FolderStructure/child 3',
		'Test_examples_container/FolderStructure/child1',
		'Test_examples_container/FolderStructure/_child2',
		])
		,
		(("Test_examples_container/FolderStructure/child1/emptydirectory"),
		list())
		)
	
	def test_known_input(self):
		for dirpath, childlist in self.known_values:
			result = PhotodeliverII.addchilddirectory(dirpath)
			self.assertEqual (set(childlist), set(result))

class lsdirectorytree_test (unittest.TestCase):
	""" It returns a list of subdirectories, works o absolute and relative paths.
	the result includes its own directory """
	known_values = (("Test_examples_container/FolderStructure",
		[
		'Test_examples_container/FolderStructure/child 3',
		'Test_examples_container/FolderStructure/child1',
		'Test_examples_container/FolderStructure/_child2',
		'Test_examples_container/FolderStructure/child1/child 1.2',
		'Test_examples_container/FolderStructure/child1/Child1.1',
		'Test_examples_container/FolderStructure/child1/emptydirectory',
		'Test_examples_container/FolderStructure/_child2/child2.2',
		'Test_examples_container/FolderStructure'
		])
		,
		(('Test_examples_container/FolderStructure/child1/emptydirectory'),
		('Test_examples_container/FolderStructure/child1/emptydirectory',))
		)

	def test_known_input(self):
		for dirpath, childlist in self.known_values:
			result = PhotodeliverII.lsdirectorytree (dirpath)
			self.assertEqual (set(childlist), set(result))
	
class Nextfilenumber_test (unittest.TestCase):
	""" test for Nextfilenumber function """
	known_values = (
		("file.jpg", "file(0).jpg"),
		("file1.jpg", "file1(0).jpg"),
		("file(0).jpg", "file(1).jpg"),
		("file(222).jpg", "file(223).jpg"),
		("file33", "file33(0)"),
		("file(33)", "file(34)"),
		("file(-1)", "file(-1)(0)"),
		("file.","file(0)."),
		("file(10).", "file(11)."),
		("file(X).jpg", "file(X)(0).jpg"),
		)
	def test_known_input (self):
		for inputfile, outputfile in self.known_values:
			result = PhotodeliverII.Nextfilenumber (inputfile)
			self.assertEqual (outputfile, result)
	def test_mad_values (self):
		self.assertRaises (PhotodeliverII.EmptyStringError, PhotodeliverII.Nextfilenumber, "")
		pass	

class enclosedyearfinder (unittest.TestCase):
	""" searchs for a year in an slash enclosed string,
	it must return the year string if any or None if it doesn't
	"""
	known_values = (
		("1992", "1992"),
		("any string",None),
		("19_90", None),
		("2000", "2000"),
		("/",None ),
		("",None )
		)
	def test_known_values (self):
		for string1, match in self.known_values:
			result = PhotodeliverII.enclosedyearfinder (string1)
			self.assertEqual (match, result)

class enclosedmonthfinder (unittest.TestCase):
	""" Give a string, it returns a string if it is a month number with 2 digits,
		otherwise it returns None, it also returns a digit mont if it is a text month
		"""
	known_values = (
		("01", "01"),
		("2" , None),
		("10" ,"10"),
		("", None),
		("jkjkj",None),
		("enero", "01"),
		("Febrero", "02"),
		("MaR", "03"),
		("dic", "12"),
		)
	def test_known_values (self):
		for string1, match in self.known_values:
			result = PhotodeliverII.enclosedmonthfinder (string1)
			self.assertEqual (match, result)


class encloseddayfinder (unittest.TestCase):
	""" Give a string, it returns a string if it is a month number with 2 digits,
		otherwise it returns None, it also returns a digit mont if it is a text month
		"""
	known_values = (
		("01", "01"),
		("2" , None),
		("10" ,"10"),
		("", None),
		("jkjkj",None),
		)
	def test_known_values (self):
		for string1, match in self.known_values:
			result = PhotodeliverII.encloseddayfinder (string1)
			self.assertEqual (match, result)


if __name__ == '__main__':
	unittest.main()

