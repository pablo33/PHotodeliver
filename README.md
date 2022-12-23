# PHotodeliver


Script for automatic date image metadatation and grouping by day event.

- Group image files by date/events.
- Inserts image's date metadata by retrieving it from the path/filename, or by the file-creation date.
- Convert png, bmp, heic files into jpg.
- Keepit running in memory and configure hotfolders to retrieve images.

Use it to:  
- Metadate scanned photographs stored in folders whose date was stored as part of its path's names.
- Process images and insert its exif metadata before manage them on other software.
- Automatically convert .png into .jpg files.
- Sort and order images into a folder structure.
- Detect possible duplicates.
- Detect which images can't guess a valid date in the path.
- Replace actual image metadata with a date found in the path.
- Rename image files acordingly to it's date metadata. (YYYYMMDD_hhmmss filename.jpg)
- Automatically group a bunch of images a into a month and/or day-event structure.
- Process every image and set it into a destination.

Dependencies:
needs at least ubuntu 14.04  
Gexiv2  #  For metadata handling.  
python3-pil  #  For image conversion.  
tifig  # for heic image conversion.  
  
You can install Gexiv2 typing: 

    sudo apt-get install gir1.2-gexiv2-0.10  