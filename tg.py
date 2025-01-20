from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from telethon import functions, types
from telethon.errors.rpcerrorlist import ChatAdminRequiredError
from telethon.tl.types import MessageMediaPoll

import config as cf
import utils


class TGAnalyser:
    """class for working with TG API to receive wall stats of your account/group"""

    def __init__(self, phone=None, api_id=None, api_hash=None):
        """
        initialize TG API client using telethon
        :param phone: your phone number or bot name
        :param api_id: api_id obtained at https://my.telegram.org/auth
        :param api_hash: api_hash obtained at https://my.telegram.org/auth
        """
        # Create the client and connect
        self._client = TelegramClient(phone if phone else cf.TG_PHONE, api_id if api_id else cf.TG_AM_API_ID,
                                      api_hash if api_hash else cf.TG_AM_API_HASH)

        self._client.start()

    def get_stat_by_period(self, start_date, end_date):
        f""" function invokes GetHistoryRequest, GetMessagePublicForwardsRequest using TG API and telethon 
        :param start_date: start date of a period to be analyzed 
        :param end_date: end date of a period to be analyzed 
        :return: list of records containing TG-account/group stat. Record values: DATE, THEME, URL, LIKES, DISLIKES, 
            COMMENTS, PUBLIC_REPOSTS, REPOSTS, VIEWS, POLL_RESULTS 
        :rtype: list 
        """

        history = self._client(GetHistoryRequest(
            peer=cf.TG_CHANNEL_NAME,
            offset_id=0,
            offset_date=None,
            add_offset=0,
            limit=cf.TG_MAXIMUM_TOPICS_PER_WEEK,
            max_id=0,
            min_id=0,
            hash=0
        ))

        tg_list = []

        for m in history.messages[-1::-1]:

            if m.message != '' or type(m.media) is MessageMediaPoll:

                if not start_date.timestamp() <= m.date.timestamp() < end_date.timestamp():
                    continue

                likes = m.reactions
                if likes:
                    likes = likes.to_dict()['results']

                    dislikes = sum([rec['count'] for rec in likes
                                    if list(dict(rec['reaction']).keys()).count('emoticon') > 0 and
                                    rec['reaction']['emoticon'] in ('👎', '🤬')]
                                   )

                    likes = sum([rec['count'] for rec in likes]) - dislikes
                else:
                    likes, dislikes = 0, 0

                post_date = m.date.strftime("%d.%m.%Y")

                try:
                    pub_fwd = self._client(functions.stats.GetMessagePublicForwardsRequest(
                        channel=cf.TG_CHANNEL_ID,
                        msg_id=m.id,
                        offset_rate=0,
                        offset_peer=types.InputPeerEmpty(),
                        offset_id=0,
                        limit=1000
                    ))
                    pub_fwd = len(pub_fwd.messages)
                except ChatAdminRequiredError:
                    pub_fwd = 0

                if type(m.media) is MessageMediaPoll:
                    theme = m.media.poll.question
                    poll_voters = m.media.results.total_voters
                else:
                    theme = m.message
                    poll_voters = 0
                theme = theme[:50].replace('\n', '').encode('cp1251', 'ignore').decode('cp1251')
                theme = utils.smart_cut(theme)

                replies = m.replies.replies if m.replies else 0

                tg_list.append([
                    post_date, theme,
                    f'{cf.TG_POST_URL_PATTERN}{m.id}', likes, dislikes,
                    replies, pub_fwd, m.forwards,
                    m.views, poll_voters
                ])

        return tg_list

    def get_stat_by_last_week(self):
        """:return: result of get_stat_by_period by the last week"""
        return self.get_stat_by_period(cf.LAST_MON, cf.CUR_MON)
