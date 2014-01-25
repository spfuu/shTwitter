import threading
import logging
from time import gmtime, strftime
from twython import TwythonStreamer, Twython

#import sys
#sys.path.append('/usr/smarthome/plugins/twitter/pycharm-debug-py3k.egg')
#import pydevd

logger = logging.getLogger('')


class Twitter:

    list_mode = ['_toggle_', '_strict_', '_default_value_']
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

    def add_cmd(self, cmd, mode, default_value, item):
        cmd = cmd.lower()
        mode = mode.lower()

        if not cmd in self._val:
            self._val[cmd] = {'items': [item, mode, default_value], 'logics': [] }
        else:
            if not item in self._val[cmd]['items']:
                self._val[cmd]['items'].append(item, mode, default_value)

    def parse_item(self, item):
        if 'twitter_recv' in item.conf:
            logger.debug("parse item: {0}".format(item))
            line = item.conf['twitter_recv']
            line = line.split(',')

            if line:
                for cmd_dict in line:
                    cmd = cmd_dict.split(':')
                    if cmd:
                        if len(cmd) > 1:
                            if cmd[1] in self.list_mode:
                                self.add_cmd(cmd[0], cmd[1], None, item)
                            else:
                                if cmd[1]:
                                    self.add_cmd(cmd[0], '_default_value_', cmd[1], item)
                                else:
                                    self.add_cmd(cmd[0], '_strict_', None, item)
                        else:
                            self.add_cmd(cmd[0], '_strict_', None, item)

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
        for cmd, values in self._val.items():
            if data.startswith(cmd):
                item = values['items'][0]
                mode = values['items'][1]
                default_value = values['items'][2]

                #passed values in command?
                value = data.lstrip(cmd)

                if not value:
                    #no value passed, choose value by mode
                    if mode == '_strict_':
                        #no value in strict mode --> do nothing
                        pass
                    if mode == '_default_value_':
                        #default_value mide --> use default value
                        if default_value:
                            value = default_value
                    if mode == '_toggle_':
                        #toggle mode, toggle current item value (if bool value)
                        if isinstance(item(), bool):
                            value = not item()
                else:
                    value = value.strip()

                if value is not None:
                    if isinstance(item(), bool):
                        if value in self.list_true:
                            value = 1
                        if value in self.list_false:
                            value = 0
                    item(value, 'Twitter', '')

class TwitterStreamer(TwythonStreamer):
    def __init__(self, plugin, app_key, app_secret, oauth_token, oauth_token_secret):
        self.plugin = plugin
        self.app_key = app_key
        self.app_secret = app_secret
        self.oauth_token = oauth_token
        self.oauth_token_secret = oauth_token_secret
        TwythonStreamer.__init__(self, self.app_key, self.app_secret, self.oauth_token, self.oauth_token_secret)
        self.twitter_api = Twython(self.app_key, self.app_secret, self.oauth_token, self.oauth_token_secret)

    def on_success(self, data):
        if 'text' in data:
            item_data = data['text'].lower()
            self.plugin.update_items_with_data(item_data)
            self.twitter_api.destroy_status(id=data['id'])

    def on_error(self, status_code, data):
        print(status_code)