import os
import requests
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
import sys

def download_image(post):
    image_url = post['file_url']
    response = requests.get(image_url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024  # 1 Kibibyte
    t = tqdm(total=total_size, unit='iB', unit_scale=True, desc=f"Downloading image {post['id']}")
    with open(f'images/{post["id"]}.jpg', 'wb') as f:
        for data in response.iter_content(block_size):
            t.update(len(data))
            f.write(data)
    t.close()

    if total_size != 0 and t.n != total_size:
        print("ERROR, something went wrong")

try:
    tags = input("Enter tags: ")
    total_pages = 3000
    os.makedirs('images', exist_ok=True)
    with ThreadPoolExecutor(max_workers=8) as executor:
        for page in range(1, total_pages + 1):
            response = requests.get(f'https://yande.re/post.json?api_version=2&page={page}&tags={tags}')
            data = response.json()
            if isinstance(data, dict) and 'posts' in data:
                posts = data['posts']
                list(tqdm(executor.map(download_image, posts), total=len(posts)))
            elif isinstance(data, list):
                list(tqdm(executor.map(download_image, data), total=len(data)))

except KeyboardInterrupt:
    print('\nInterrupted by user. Exiting...')
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)
