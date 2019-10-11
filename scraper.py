import os
import sys
from multiprocessing.dummy import Pool as ThreadPool

import requests
from bs4 import BeautifulSoup

threads = 2  # site limits you after 2
output_path = 'output'
content_url = 'https://cdromance.com/sony-psp-dlc-list-psp-downloadable-content/'

# To retrieve the key, Open chrome developer tool, Perform a download manually and look a the network tab
# find the link starting with download.php? i.e. http://dl4.cdromance.com/download.php?file=ULJS00385.7z&id=144240&platform=page&key=3015679560829197352960&test=4
# Copy the numbers that appear after key= and before the next & symbol, enter that key below this line, failure to do so will result in errors
key = '3015679560829197352960'  

def get_file(res):
    """
    Expects a beautifulSoup tag object with the attribute data-filename and data-id
    Function will download and save the file passed to this function
    :param res: beautifulSoup tag object
    :return: None
    """
    if not os.path.exists(f'{output_path}/{res["data-filename"]}'):
        try:
            url = f'http://dl4.cdromance.com/download.php' \
                  f'?file={res["data-filename"]}' \
                  f'&id={res["data-id"]}' \
                  f'&platform=page' \
                  f'&key={key}'

            r = requests.get(url, allow_redirects=True)

            if len(r.content) < 128:
                print(f'{res["data-filename"]} failed, Reason: Key Expired')
                sys.stdout.flush()
            else:
                print(f'{res["data-filename"]}, {len(r.content)} bytes')
                sys.stdout.flush()

                with open(f'{output_path}/{res["data-filename"]}', 'wb') as f:
                    f.write(r.content)
        except Exception as ex:
            print(f'{res["data-filename"]} failed, Reason: {ex}')

    else:
        print(f'{res["data-filename"]} skipped, already exists')
        sys.stdout.flush()


if not os.path.exists(output_path):
    os.mkdir(output_path)

print(f'Scraping: {content_url}')
request = requests.get(content_url)

print(request.status_code)

if request.status_code == 404:
    exit(1)

results = BeautifulSoup(request.content, 'html.parser').find_all('div', {'id': 'acf-content-wrapper'})

print(f'Queued {len(results)} files for download')

pool = ThreadPool(threads)

print('Starting')
results = pool.map(get_file, results)

pool.close()
pool.join()

print('Finished')
