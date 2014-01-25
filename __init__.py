import threading
import logging
from time import gmtime, strftime
from twython import TwythonStreamer

logger = logging.getLogger('')


class Twitter:

    list_true = ['ein', 'ja', 'eins', '1', 'yes', 'yeah', 'jepp', 'on', 'jo']
    list_false = ['aus', 'off', 'null', 'no', 'nein', 'nope', '0']

    def __init__(self, smarthome, app_key, app_secret, oauth_token, oauth_token_secret, user):
        self._sh = smarthome
        self.app_key = app_key
        self.app_secret = app_secret
        self.oauth_token = oauth_token
        self.oauth_token_secret = oauth_token_secret
        self.user = user
        self._val = {}

    def run(self):
        self.alive = True
        self.twitter_thread = threading.Thread(target=self.init_twitter())
        self.twitter_thread.start()

    def stop(self):
        self.alive = False
        self.twitter_thread.join()

    def parse_item(self, item):
        if 'twitter_recv' in item.conf:

            logger.debug("parse item: {0}".format(item))
            cmd = item.conf['twitter_recv'].lower()

            if cmd is None:
                return None

            logger.debug("twitter: {} receives updates by {}".format(item, cmd))

            if not cmd in self._val:
                self._val[cmd] = {'items': [item], 'logics': []}
            else:
                if not item in self._val[cmd]['items']:
                    self._val[cmd]['items'].append(item)

            return self.update_item
        else:
            return None

    def parse_logic(self, logic):
            pass

    def update_item(self, item, caller=None, source=None, dest=None):
        if caller != 'Twitter':
            logger.info("update item: {0}".format(item.id()))

    def init_twitter(self):
        twitter = TwitterStreamer(self, self.app_key, self.app_secret, self.oauth_token, self.oauth_token_secret)
        twitter.user(user=self.user)

    def update_items_with_data(self, data):

        #trim the last occurence of '/': everything right-hand-side is our value
        cmd = data.rsplit(' ', 1)

        if len(cmd) < 2:
            logger.warning("unknown command '%s'" % data)
            return

        logger.debug(cmd[0])
        logger.debug(cmd[1])

        if cmd[0] in self._val:
            for item in self._val[cmd[0]]['items']:
                if isinstance(item(), bool):
                    if cmd[1] in self.list_true:
                        cmd[1] = 1
                    if cmd[1] in self.list_false:
                        cmd[1] = 0
                logger.debug("data: {}".format(cmd[1]))
                item(cmd[1], 'Twitter', '')

class TwitterStreamer(TwythonStreamer):
    def __init__(self, plugin, app_key, app_secret, oauth_token, oauth_token_secret):
        self.plugin = plugin
        self.app_key = app_key
        self.app_secret = app_secret
        self.oauth_token = oauth_token
        self.oauth_token_secret = oauth_token_secret

        TwythonStreamer.__init__(self, self.app_key, self.app_secret, self.oauth_token, self.oauth_token_secret)

    def on_success(self, data):
        if 'text' in data:
            data = "tweet %s" % data['text'].lower()
            logger.debug(data)
            self.plugin.update_items_with_data(data)

    def on_error(self, status_code, data):
        print(status_code)