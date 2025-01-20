import requests
import datetime
import shutil

# URL = 'https://disk.yandex.ru/d/oDjLvjJtnIsmtA'
URL = 'https://cloud-api.yandex.net/v1/disk/resources'
TOKEN = 'y0_AgAAAAAJycDIAAnIqgAAAADhYzbZRuTZT8kwQ4O6C6FJt_jJAvqDImk'
# TOKEN = 'b26e2720b192440886ab32c581b8c695'


TOKEN = 'y0_AgAEA7qkQZ9QAAnIzgAAAADhZKjoZiYYhIuuSUeA82kCvgX78_2WdQw'

headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': f'OAuth {TOKEN}'}


def create_folder(path):
    """Создание папки. \n path: Путь к создаваемой папке."""
    print(requests.put(f'{URL}?path={path}', headers=headers).text)


def upload_file(loadfile, savefile, replace=False):
    """Загрузка файла.
    savefile: Путь к файлу на Диске
    loadfile: Путь к загружаемому файлу
    replace: true or false Замена файла на Диске"""
    res = requests.get(f'{URL}/upload?path={savefile}&overwrite={replace}', headers=headers).json()
    with open(loadfile, 'rb') as f:
        try:
            requests.put(res['href'], files={'file': f})
        except KeyError:
            print(res)


# create_folder('/api')
td = str.replace(str(datetime.date.today()), '-', '')
upload_file(r'C:\Projects\SocialNetworkAnalyzer\Analytics.xlsx', 'Новые активности.xlsx', True)
shutil.copyfile(r'C:\Projects\SocialNetworkAnalyzer\Analytics.xlsx', fr'C:\Projects\SocialNetworkAnalyzer\backup\Analytics - {td}.xlsx')