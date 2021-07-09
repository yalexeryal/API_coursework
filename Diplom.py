import requests
import json
import datetime
import time
from datetime import datetime
from urllib.parse import urljoin
from TOKEN import token_vk, token_ya_disk, id_vk
from tqdm import tqdm

class Photo:
    name = ''

    def __init__(self, date, likes, sizes):
        self.date = date
        self.likes = likes
        self.sizes = sizes
        self.size_type = sizes['type']
        self.url = sizes['url']
        self.maxsize = max(sizes['width'], sizes['height'])

    def __repr__(self):
        return f'date: {self.date}, likes: {self.likes}, size: {self.maxsize}, url: {self.url}'


class VkAPI:
    URL = "https://api.vk.com/method/"
    token = token_vk

    @staticmethod
    def find_largest(sizes):
        sizes_chart = ['x', 'z', 'y', 'r', 'q', 'p', 'o', 'x', 'm', 's']
        for chart in sizes_chart:
            for size in sizes:
                if size['type'] == chart:
                    return size

    def __init__(self):
        self.token = self.token
        self.version = '5.131'

    def get_photos(self, user_id, qty=5):
        get_url = urljoin(self.URL, 'photos.getAll')
        resp = requests.get(get_url, params={
            'access_token': self.token,
            'v': self.version,
            'owner_id': user_id,
            'album_id': 'profile',
            'photo_sizes': 1,
            'extended': 1
        }).json().get('response').get('items')

        return sorted([Photo(photo.get('date'),
                             photo.get('likes')['count'],
                             self.find_largest(photo.get('sizes'))) for photo in resp],
                      key=lambda p: p.maxsize, reverse=True)[:qty]


class YaAPI:

    @staticmethod
    def create_file_names(photos):
        for photo in photos:
            photo.name = str(photo.likes)
            if [p.likes for p in photos].count(photo.likes) > 1:
                photo.name += '_' + str(photo.date)
            photo.name += '.jpg'

    @staticmethod
    def check_folder_name(n_folder, ex_folders):
        if n_folder not in ex_folders:
            return n_folder
        n = 1
        n_folder += '_' + str(n)
        while n_folder in ex_folders:
            n_folder = n_folder.replace('_' + str(n), '_' + str(n + 1))
            n += 1
        return n_folder

    def __init__(self, token: str):
        self.auth = f'OAuth {token}'

    def get_folders(self):
        return [p['name'] for p in (requests.get("https://cloud-api.yandex.net/v1/disk/resources",
                                                 params={"path": '/'},
                                                 headers={"Authorization": self.auth})
                                    .json().get('_embedded').get('items')) if p['type'] == 'dir']

    def create_folder(self, folder_name):
        resp = requests.put("https://cloud-api.yandex.net/v1/disk/resources",
                            params={"path": f'/{folder_name}'},
                            headers={"Authorization": self.auth})
        print(f'Creating folder "{folder_name}:{str(resp.status_code)}')
        return resp.ok

    def upload(self, user_id, photos):
        upload_folder = self.check_folder_name(id, self.get_folders())
        self.create_file_names(photos)
        if self.create_folder(upload_folder):
            log_result = []
            for photo in photos:
                response = requests.post("https://cloud-api.yandex.net/v1/disk/resources/upload",
                                         params={"path": f'/{upload_folder}/{photo.name}',
                                                 "url": photo.url},
                                         headers={"Authorization": self.auth})
                if response.status_code == 202:
                    log_result.append({"file_name": photo.name, "size": photo.size_type})
                else:
                    print(f'Error uploading photo "{photo.name}": '
                          f'{response.json().get("message")}. Status code: {response.status_code}')
            for _ in tqdm(photos):
                time.sleep(1)
            with open(f'{user_id}_{datetime.now().strftime("%m_%d_%Y_%H_%M_%S")}_files.json', "w") as f:
                json.dump(log_result, f, ensure_ascii=False, indent=2)


def make_copy():
    ya_token = token_ya_disk
    user_id = id_vk
    qty = 5
    vk_api = VkAPI()
    ya_api: YaAPI = YaAPI(ya_token)
    ya_api.upload(user_id, vk_api.get_photos(user_id, int(qty)))


if __name__ == '__main__':
    make_copy()
