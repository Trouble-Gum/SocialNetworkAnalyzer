import json
import requests
import datetime

import config as cf
from time import sleep


class VKAnalyser:
    """class for working with VK REST API to receive wall stats of your account/group"""

    def __init__(self, vk_user_token=None, vk_domain=None, vk_club_id=None, vk_oauth_token=None):

        self._vk_user_token = vk_user_token if vk_user_token else cf.VK_USER_TOKEN
        self._vk_domain = vk_domain if vk_domain else cf.VK_DOMAIN
        self._vk_club_id = vk_club_id if vk_club_id else cf.VK_CLUB_ID
        self._vk_oauth_token = vk_oauth_token if vk_user_token else cf.VK_OAUTH_TOKEN

    def refresh_from_config(self):
        self._vk_user_token = cf.VK_USER_TOKEN
        self._vk_domain = cf.VK_DOMAIN
        self._vk_club_id = cf.VK_CLUB_ID
        self._vk_oauth_token = cf.VK_OAUTH_TOKEN

    def get_stat_by_period(self, start_date, end_date):
        f""" function invokes VK API web methods: https://api.vk.com/method/wall.get, 
        https://api.vk.com/method/stats.getPostReach 
        :param start_date: start date of a period to be analyzed 
        :param end_date: end date of a period to be analyzed 
        :return: list of records containing VK-account/group stat. Record values: 'DATE', 'THEME', 'URL', 'LIKES', 
            'COMMENTS', 'REPOSTS', 'VIEWS', 'SUBSCRIPTIONS', 'TO_GROUP'
        :rtype: list 
        """
        self.refresh_from_config()
        response = requests.get('https://api.vk.com/method/wall.get',
                                params={'access_token': self._vk_user_token,
                                        'scope': 'wall, messages',
                                        'v': cf.VK_VERSION,
                                        # 'domain': self._vk_domain,
                                        'count': cf.VK_MAXIMUM_TOPICS_PER_WEEK,
                                        'owner_id': self._vk_club_id
                                        })

        posts = response.json()['response']['items']

        posts = posts[-1::-1]

        ids = [post['id'] for post in posts]
        ids_ = ','.join(str(s) for s in ids)

        post_reach = requests.get(url='https://api.vk.com/method/stats.getPostReach',
                                  params={
                                      'access_token': self._vk_oauth_token,
                                      'v': cf.VK_VERSION,
                                      'owner_id': self._vk_club_id,
                                      'post_ids': ids_
                                  })

        post_reach = json.loads(post_reach.content)['response']

        post_dict = {}
        for rec in post_reach:
            post_dict[rec['post_id']] = rec

        vk_list = []

        for rec in posts:
            sleep(0.1)
            post_id = rec["id"]

            posts_filter = f'{self._vk_club_id}_{post_id}'
            post = requests.get('https://api.vk.com/method/wall.getById',
                                params={'access_token': self._vk_user_token,
                                        'v': cf.VK_VERSION,
                                        'posts': posts_filter
                                        })

            post = post.json()['response'][0]

            date = post['date']
            date = datetime.datetime.fromtimestamp(date)
            if not start_date <= date < end_date:
                ids.remove(post_id)
                continue

            text = post['text'][:50].replace('\n', '').encode('cp1251', 'ignore').decode('cp1251')
            if not text:
                for text in [att['video']['description'] for att in post['attachments'] if att['type'] == 'video']:
                    if text:
                        break

            likes_count = post['likes']['count']
            comments_count = post['comments']['count']
            reposts_count = post['reposts']['count']
            views_count = post['views']['count']
            url = cf.VK_POST_URL_PATTERN + str(post_id)

            vk_list.append([date.strftime("%d.%m.%Y"), text, url,
                            likes_count, comments_count, reposts_count, views_count,
                            post_dict[post_id]['join_group'], post_dict[post_id]['to_group']])
        return vk_list

    def get_stat_by_last_week(self):
        """:return: result of get_stat_by_period by the last week"""
        return self.get_stat_by_period(start_date=cf.LAST_MON, end_date=cf.CUR_MON)
