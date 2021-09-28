import requests
from urllib.parse import urljoin


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
    token = '958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008'

    @staticmethod
    def find_largest(sizes):
        sizes_list = ['x', 'z', 'y', 'r', 'q', 'p', 'o', 'x', 'm', 's']
        for symbol in sizes_list:
            for size in sizes:
                if size['type'] == symbol:
                    return size

    def __init__(self):
        self.token = self.token
        self.version = '5.131'

    def get_photos(self, user_id, quantity_photos=5):
        url = urljoin(self.URL, 'photos.get')
        result = requests.get(url, params={
            'access_token': self.token,
            'v': self.version,
            'owner_id': user_id,
            'album_id': 'profile',
            'photo_sizes': 1,
            'extended': 1
        }).json().get('response').get('items')

        return sorted([Photo(photo.get('date'),
                             photo.get('likes')['count'],
                             self.find_largest(photo.get('sizes'))) for photo in result],
                      key=lambda p: p.maxsize, reverse=True)[:quantity_photos]
