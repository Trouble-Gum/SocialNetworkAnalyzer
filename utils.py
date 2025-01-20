import datetime
import os
import sys
import inspect

from dotenv import load_dotenv

env = os.environ.get
SETTINGS = 'settings.env'


def to_list(params):
    """
    Function converts string which contains params delimited with coma to list
    :param params: string with parameters
    :type: str
    :return: list of separated parameters
    :trype: list
    """
    return list(map(str.lstrip, env(params).split(',')))


def smart_cut(text):
    """
    Removes part of string after the last dot or space
    :param text: text to be handled
    :return: handled text
    :rtype: str
    """
    t = text.replace('\n', '.')
    end_ = ''
    try:
        ind = t.rindex('.')
        end_ = '..'
    except ValueError:
        ind = 0

    if ind == 0:
        try:
            ind = t.rindex(' ')
            end_ = '...'
        except ValueError:
            ind = 100
    return t[:ind] + end_


def load_env(file_):
    """
    Loads settings from env-file to the environment
    :param file_: file which contains settings
    :return: None
    """
    dotenv_path = os.path.join(os.path.dirname(__file__), file_)
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path, override=True)


def init_profile_settings(file):
    """
    Initializes profile settings specified in file
    :param file: file which contains settings
    :return: None
    """
    load_env(SETTINGS)
    load_env(file)

    mod = sys.modules['config']

    constants = (obj.items() for name, obj in inspect.getmembers(mod)
                 if name == '__annotations__')
    constants = (list(*constants))

    for rec in constants:
        setattr(mod, rec[0], int(env(rec[0])) if env(rec[0]) and rec[1] is int else env(rec[0]))

    val = getattr(mod, 'OK_GROUP_ID')
    setattr(mod, 'OK_TOPIC_URL_PATTERN', f'https://ok.ru/group/{val}/topic/')

    vk_domain = getattr(mod, 'VK_DOMAIN')
    vk_club_id = getattr(mod, 'VK_CLUB_ID')
    setattr(mod, 'VK_POST_URL_PATTERN', f'{vk_domain}?w=wall{vk_club_id}_')

    val = env('TG_CHANNEL_ID')
    val = int(val) if val else None
    setattr(mod, 'TG_CHANNEL_ID', val)

    val = getattr(mod, 'TG_CHANNEL_NAME')
    setattr(mod, 'TG_POST_URL_PATTERN', f'https://t.me/{val}/')

    setattr(mod, 'OK_COLUMNS', to_list('OK_COLUMNS'))
    setattr(mod, 'VK_COLUMNS', to_list('VK_COLUMNS'))
    setattr(mod, 'TG_COLUMNS', to_list('TG_COLUMNS'))

    last_mon = datetime.date.today()
    last_mon = datetime.datetime(last_mon.year, last_mon.month, last_mon.day, 0, 0, 0)
    last_mon += datetime.timedelta(days=-last_mon.weekday(), weeks=-1)
    cur_mon = last_mon + datetime.timedelta(weeks=1)

    # datetime_str = '09/09/2024 00:00:00'
    # last_mon = datetime.datetime.strptime(datetime_str, '%d/%m/%Y %H:%M:%S')
    # datetime_str = '16/09/2024 00:00:00'
    # cur_mon = datetime.datetime.strptime(datetime_str, '%d/%m/%Y %H:%M:%S')
    # print(last_mon, cur_mon)
    # exit()

    setattr(mod, 'LAST_MON', last_mon)
    setattr(mod, 'CUR_MON', cur_mon)



def show_menu_and_get_choice():
    """
    Shows main menu
    :return: information about all env-files and number of chosen file
    :rtype: tuple
    """
    print('Available configuration files:')
    files = [file for file in os.listdir(os.curdir) if file.endswith('.env') and file != SETTINGS]
    env_dict = {}
    length = len(files)
    for i in range(length):
        file = files[i]
        env_dict[i+1] = file
        print(i+1, file, sep=' - ')
    print(length + 1, 'choose all', sep=' - ')
    try:
        file_num = int(input("Enter point number: "))
    except ValueError:
        raise ValueError("Incorrect input value for choosing .env file")

    if file_num not in (range(1, length + 2)):
        print("Specified point doesn't match any file from .env-files list")
        exit()

    return env_dict, file_num


init_profile_settings(SETTINGS)
