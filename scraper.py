import os
import sys
from multiprocessing.dummy import Pool as ThreadPool

import requests
from bs4 import BeautifulSoup

output_path = 'output'
threads = 2  # site limits you after 2
content_url = 'https://cdromance.com/sony-psp-dlc-list-psp-downloadable-content/'


def get_file(res):
    """
    Expects a beautifulSoup tag object with the attribute data-filename and data-id
    Function will download and save the file passed to this function
    :param res: beautifulSoup tag object
    :return: None
    """
    url = f'http://dl4.cdromance.com/download.php' \
          f'?file={res["data-filename"]}' \
          f'&id={res["data-id"]}' \
          f'&platform=page' \
          f'&key=2744046125430717546496'

    r = requests.get(url, allow_redirects=True)
    print(f'{res["data-filename"]}, {len(r.content)} bytes')
    sys.stdout.flush()

    with open(f'{output_path}/{res["data-filename"]}', 'wb') as f:
        f.write(r.content)


if not os.path.exists(output_path):
    os.mkdir(output_path)

print(f'Scraping: {content_url}')
request = requests.get(content_url)

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
