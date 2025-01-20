import datetime
import json

import utils
from ok_api import OkApi

import config as cf
import requests

VIEWS = 'views'
LIKES = 'likes'
COMMENTS = 'comments'
REPOSTS = 'reshares'
CREATED_MS = 'created_ms'
ID = 'id'

OK_STAT_FIELDS = f'{LIKES}, {COMMENTS}, {REPOSTS}, {VIEWS}, {CREATED_MS}, {ID}'


class OKAnalyser:
    """class for working with OK REST API to receive wall stats of your account/group"""

    def __init__(self, access_token=None, application_key=None, application_secret_key=None):
        """
        initialize instance of OK API client
        :param access_token: TOKEN obtained at https://apiok.ru/
        :param application_key: APPLICATION_KEY obtained at https://apiok.ru/
        :param application_secret_key: APPLICATION_SECRET_KEY obtained at https://apiok.ru/
        """

        self._ok_inst = OkApi(
            access_token=access_token if access_token else cf.OK_ACCESS_TOKEN,
            application_key=application_key if application_key else cf.OK_APPLICATION_KEY,
            application_secret_key=application_secret_key if application_secret_key else cf.OK_APPLICATION_SECRET_KEY)

    def get_stat_by_topic_id(self, topic_id):
        """ function invokes APIMethod (https://api.ok.ru/fb.do?format=json&method=group.getStatTopic')
            and handles its result
            :param int topic_id: ID of topic (post on OK.ru-network wall)
            :return: number of views, comments, reposts, likes of topic
            :rtype: dict
        """
        response = self._ok_inst.group.getStatTopic(topic_id=topic_id, fields=OK_STAT_FIELDS)
        res = json.loads(response.content)['topic']
        return {VIEWS: res[VIEWS], LIKES: res[LIKES], COMMENTS: res[COMMENTS],
                REPOSTS: res[REPOSTS]}

    def get_stat_by_wall(self, gid=None, count=None):
        """ function invokes APIMethod getStatTopics
            (https://api.ok.ru/fb.do?format=json&method=group.getStatTopics')
            and handles its result
            :param count: max amount of last posted topics to be returned
            :param int gid: Ok group ID
            :return: list with number of views, comments, reposts, likes of each topic
            :rtype: dict
        """

        gid = cf.OK_GROUP_ID if not gid else gid
        count = cf.OK_MAXIMUM_TOPICS_PER_WEEK if not count else count

        # response = self._ok_inst.group.getStatTopics(gid=gid, count=count, fields=OK_STAT_FIELDS, sig='1a451a787067f00e71722a4bca3707a9', access_token='-s-8z2zWLWmGUWX0KVGKUSZ2MPFHzW2TLU-oS3aTtQiHvWz1u.gorX1UNQFHSS-VKPKnUXY5tPgJTT.SNSiFzS31L4')

        response = requests.get(url='https://api.ok.ru/fb.do',
                                params={
                                    'application_key': cf.OK_APPLICATION_KEY,
                                    'format': 'json',
                                    'method': 'auth.touchSession',
                                    'sig': 'aadcef6291489c6bcfc70d8fd846e930',
                                    'access_token': cf.OK_ACCESS_TOKEN
                                })
        print(response.content)
        response = requests.get(url='https://api.ok.ru/fb.do',
                                  params={
                                      'application_key': cf.OK_APPLICATION_KEY,
                                      'count': count,
                                      'fields': OK_STAT_FIELDS,
                                      'format': 'json',
                                      'gid': cf.OK_GROUP_ID,
                                      'method': 'group.getStatTopics',
                                      'sig': '8105c384369dce1d54b2c9fc994a584c',
                                      'access_token': cf.OK_ACCESS_TOKEN
                                  })

        response = json.loads(response.content)

        print(response)
        print(OK_STAT_FIELDS)
        exit()
        res = json.loads(response.content)['topics']

        for rec in res:
            date = float(rec[CREATED_MS])
            date = datetime.datetime.fromtimestamp(date / 1000.0)
            rec[CREATED_MS] = date
        return res

    def get_stat_by_last_week(self, gid=None, count=None):
        """ function invokes get_stat_by_wall and filters results selecting only last week posts
            :param count: max amount of last posted topics to be returned
            :param int gid: Ok group ID
            :return: list with number of views, comments, reposts, likes of each topic
            :rtype: list
        """
        gid = cf.OK_GROUP_ID if not gid else gid
        count = cf.OK_MAXIMUM_TOPICS_PER_WEEK if not count else count

        ok_list = []

        stat = self.get_stat_by_wall(gid, count)
        stat = stat[-1::-1]

        for stat_rec in stat:
            if not cf.LAST_MON <= stat_rec[CREATED_MS] < cf.CUR_MON:
                continue

            tpc_id = stat_rec[ID]
            text = self._ok_inst.mediatopic.getByIds(topic_ids=tpc_id, fields='media_topic.*')
            try:
                text = str(text.json()['media_topics'][0]['media'][0]['text']
                           [:50].encode('cp1251', 'ignore').decode('cp1251')
                           )
            except KeyError:
                text = ''
            text = utils.smart_cut(text)

            ok_list.append([
                stat_rec[CREATED_MS].strftime("%d.%m.%Y"), text, cf.OK_TOPIC_URL_PATTERN + tpc_id,
                stat_rec[LIKES], stat_rec[COMMENTS], stat_rec[REPOSTS], stat_rec[VIEWS]
            ])

        return ok_list
