import os
import sys
from multiprocessing.dummy import Pool as ThreadPool
from collections import defaultdict
import re
import cfscrape
from datetime import datetime

import requests
from bs4 import BeautifulSoup

scraper = cfscrape.create_scraper()


regex = r"'(.*?)'"
regex_key = r".+key=(.+)'.+"
threads = 2  # site limits you after 2
output_path = 'output'
content_url = 'https://cdromance.com/sony-psp-dlc-list-psp-downloadable-content'

counts = defaultdict(int)

def get_file(res):
    """
    Expects a beautifulSoup tag object with the attribute data-filename and data-id
    Function will download and save the file passed to this function
    :param res: beautifulSoup tag object
    :return: None
    """
    if not os.path.exists(f'{output_path}/{res["data-filename"]}'):
        key_url = f'https://cdromance.com/wp-content/plugins/cdromance/public/direct.php'

        headers = {
            "Host": "cdromance.com",
            "Connection": "keep-alive",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.52 Safari/536.5",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "*/*",
        }

        r = scraper.post(key_url, headers= headers, data = {
            "file_name": res["data-filename"],
            "post_id": res["data-id"], # post_id required but stops us getting a key back to feed into the download_url
            "server_id": res["data-server"]
        }, allow_redirects=True, stream=True)

        # key = re.search(regex_key, str(r_key.text)).group(1)
        # print(key)
        #
        # print({"file_name": res["data-filename"], "post_id": res["data-id"], "server_id": res["data-server"]})
        #
        # r = scraper.post(download_url, params = {"file": res["data-filename"], "id": res["data-id"], "platform": "psp", "key": key}, allow_redirects=True, stream=True)
        #
        #print(r.content)

        if b'window.location' in r.content:
            reg_data = re.search(regex, str(r.content))
            download_url = reg_data.group(1)+f"&platform=psp&id={res['data-id']}"
            #print(download_url)

            try:
                r = scraper.get(download_url, allow_redirects=True, stream=True)

                if len(r.content) == 21:
                    counts['error_file_not_found'] += 1
                    print(f'{res["data-filename"]} failed, URL: {download_url}, Reason: File Doesnt Exist')
                    sys.stdout.flush()
                elif len(r.content) == 89:
                    counts['error_key_expired'] += 1
                    print(f'{res["data-filename"]} failed, URL: {download_url}, Reason: Key Expired')
                    sys.stdout.flush()
                elif len(r.content) < 128:
                    counts['error_other'] += 1
                    print(f'{res["data-filename"]} failed, URL: {download_url}, Reason: {str(r.content)}')
                    sys.stdout.flush()
                else:
                    counts['success'] += 1
                    print(f'{res["data-filename"]}, {len(r.content)} bytes')
                    sys.stdout.flush()

                    with open(f'{output_path}/{res["data-filename"]}', 'wb') as f:
                        for chunk in r.iter_content(chunk_size=1024):
                            if chunk:
                                f.write(chunk)

            except Exception as ex:
                print(f'{res["data-filename"]} failed, URL: {download_url}, Reason: {str(ex)}')

    else:
        counts['skipped'] += 1
        print(f'{res["data-filename"]} skipped, already exists')
        sys.stdout.flush()


if not os.path.exists(output_path):
    os.mkdir(output_path)

print(f'Scraping: {content_url}')

request = scraper.get(content_url)

print(request.status_code)

if request.status_code == 404:
    print("Site Unreachable (404)")
    exit(1)

results = BeautifulSoup(request.content, 'html.parser').find_all('div', {'id': 'acf-content-wrapper'})

print(f'Queued {len(results)} files for download')

pool = ThreadPool(threads)

print('Starting')
results = pool.map(get_file, results)

pool.close()
pool.join()

print('\n***************************')
[print(f'{x}: {y}') for x,y in counts.items()]

print('\nDone')
