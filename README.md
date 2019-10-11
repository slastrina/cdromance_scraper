# cdromance psp dlc scraper
Simple scraper for cloning the contents of https://cdromance.com/sony-psp-dlc-list-psp-downloadable-content/ for gaming preservation purposes

Requires python 3.7

### Setup:
Clone Repo
pip install -r requirements.txt
Set key in scraper.py (see key retrieval)

### Key Retrieval:
To retrieve the key, Open chrome developer tool, Perform a download manually and look a the network tab
find the link starting with download.php? i.e. http://dl4.cdromance.com/download.php?file=ULJS00385.7z&id=144240&platform=page&key=3015679560829197352960&test=4
Copy the numbers that appear after key= and before the next & symbol, enter that key below this line, failure to do so will result in errors

### Usage:
python scraper.py

### Notes:
The tool may look like its hung after the "Starting" statement, but it just outputs the next line after the file has been downloaded