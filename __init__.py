import threading
import logging
from time import gmtime, strftime
from twython import TwythonStreamer

logger = logging.getLogger('')


class Twitter:
    def __init__(self, smarthome, app_key, app_secret, oauth_token, oauth_token_secret, user):
        self._sh = smarthome
        self.app_key = app_key
        self.app_secret = app_secret
        self.oauth_token = oauth_token
        self.oauth_token_secret = oauth_token_secret
        self.user = user


    def run(self):
        self.alive = True
        self.twitter_thread = threading.Thread(target=self.init_twitter())
        self.twitter_thread.start()

    def stop(self):
        self.alive = False
        self.twitter_thread.join()

    def parse_item(self, item):
        if 'plugin_attr' in item.conf:
            logger.debug("parse item: {0}".format(item))
            return self.update_item
        else:
            return None

    def parse_logic(self, logic):
        if 'xxx' in logic.conf:
            # self.function(logic['name'])
            pass

    def update_item(self, item, caller=None, source=None, dest=None):
        if caller != 'plugin':
            logger.info("update item: {0}".format(item.id()))

    def init_twitter(self):
        twitter = TwitterStreamer(self, self.app_key, self.app_secret, self.oauth_token, self.oauth_token_secret)
        twitter.user(user=self.user)


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
            print((data['text'].encode('utf-8')))
            logger.debug(data['text'].encode('utf-8'))

    def on_error(self, status_code, data):
        print(status_code)