import requests
import os
from bs4 import BeautifulSoup

output_path = 'output'

if not os.path.exists(output_path):
    os.mkdir(output_path)

content_url = 'https://cdromance.com/sony-psp-dlc-list-psp-downloadable-content/'

request = requests.get(content_url)

if request.status_code == 404:
    exit(1)

results = BeautifulSoup(request.content, 'html.parser').find_all('div', {'id': 'acf-content-wrapper'})

for result in results:
    print(result['data-filename'], result['data-id'])

    url = f'http://dl4.cdromance.com/download.php?file={result["data-filename"]}&id={result["data-id"]}&platform=page&key=2744046125430717546496'
    r = requests.get(url, allow_redirects=True)

    with open(f'{output_path}/{result["data-filename"]}', 'wb') as f:
        f.write(r.content)