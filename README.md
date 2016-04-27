# PHotodeliver


Script for automatic image metadatation and grouping by day event.

- Group image files by date.
- Inserts image's date metadata by retrieving it from the path/filename, or by the file-creation date.
- Convert png files into jpg.

Use it to:  
- Metadate scanned photographs stored in folders whose date was stored as part of its path.
- Process whatsapp images and inform its exif metadata before manage it on Shotwell.
- Automatically convert .png into .jpg files.
- Sort and order images into a folder structure.
- Detect possible duplicates.
- Detect which images can't guess a valid date in the path.
- Replace actual image metadata with a date found in the path.
- Rename image files acordingly to it's date metadata. (YYYYMMDD_hhmmss filename.jpg)
- Automatically group a buch of images a into a month and/or day-event structure.

Dependencies:
needs at least ubuntu 14.04
python3-pil  #  For image conversion
