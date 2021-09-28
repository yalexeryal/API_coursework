import requests
import json
import datetime
import time
from datetime import datetime
from tqdm import tqdm


class YaAPI:

    @staticmethod
    def create_file_names(photos):
        for photo in photos:
            photo.name = str(photo.likes)
            if [p.likes for p in photos].count(photo.likes) > 1:
                photo.name += '_' + str(photo.date)
            photo.name += '.jpg'

    @staticmethod
    def check_folder_name(name_folder, ex_folders):
        if name_folder not in ex_folders:
            return name_folder
        num = 1
        name_folder += '_' + str(num)
        while name_folder in ex_folders:
            name_folder = name_folder.replace('_' + str(num), '_' + str(num + 1))
            num += 1
        return name_folder

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
