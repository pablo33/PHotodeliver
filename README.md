# PHotodeliver


Script for automatic image's metadatation of image files stored in an informed folder tree structure .

This script injects the date of the image by selecting the most appropriate image's date-taken on own EXIF metadata , text that involved in the path of the image, or the creation date of the file (STAT attribute of the filesystem). This data retrieved and is injected as EXIF metadata.

It also sets the files in a new hierarchic directory tree based on the metadata.

Ideal for reporting EXIF data on old family photographs.


Dependencies:
needs at least ubuntu 14.04
python3-pil  #  For image conversion
