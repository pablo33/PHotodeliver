# PHotodeliver


Script for automatic date image and .mp4 metadatation and grouping by day event.

- Group image files by date/events.
- Inserts image's date metadata by retrieving it from the path/filename, or by the file-creation date.
- Convert png, bmp, heic files into jpg.
- Keepit running in memory and configure hotfolders to retrieve images.

Use it to:  
- Metadate scanned photographs stored in folders whose date was stored as part of its path's names.
- Metadate .mp4 files retrieving date from its filename.
- Process images and insert its exif metadata before manage them on other software.
- Automatically convert .png into .jpg files.
- Sort and order images into a folder structure.
- Detect possible duplicates.
- Detect which images can't guess a valid date in the path.
- Force replacing actual image metadata with a date found in the path.
- Rename image files acordingly to it's date metadata. (YYYYMMDD_hhmmss filename.jpg)
- Automatically group a bunch of images a into a month and/or day-event structure.
- Process every image and set it into a destination.

Dependencies:
needs at least ubuntu 14.04  
pyexiv2  #  For metadata handling.  
pillow  #  For image conversion.  
tifig  # for heic image conversion.  
ffmpeg  # for adding metadata by remuxing videos.  

on modern linux releases, use with a virtual environment.  
Setup a virtual environment and installing dependencies:  
`    python -m venv myvenv`  
It will create a folder with the virtual environment.    
Activating the virtual env and installing dependencies:    
`   source myvenv/bin/activate`  
`    pip install --upgrade pip`  
`    pip install pyexiv2 pillow`  
Then you can run the script:  
`    python PhotodeliverII.py`  
Deactivating the virtual env:  
`    deactivate`  
Installing ffmpeg:  
`    sudo apt-get install ffmpeg`  
for HEIC conversion to jpg, download bynary from: https://github.com/monostream/tifig/ and put it besides your script.  
    
