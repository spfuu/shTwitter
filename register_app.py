import requests
from requests.packages.urllib3 import request
from twython import Twython


APP_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxx"
APP_SECRET = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"


twitter = Twython(APP_KEY, APP_SECRET)
auth = twitter.get_authentication_tokens()
OAUTH_TOKEN = auth['oauth_token']
OAUTH_TOKEN_SECRET = auth['oauth_token_secret']

print("Copy link and open it with your browser:\n\n%s\n\n" % auth['auth_url'])
oauth_verifier = int(input('Please enter the PIN displayed: '))

twitter = Twython(APP_KEY, APP_SECRET,
                  OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

final_step = twitter.get_authorized_tokens(oauth_verifier)
OAUTH_TOKEN = final_step['oauth_token']
OAUTH_TOKEN_SECERT = final_step['oauth_token_secret']


print("\nCopy OAUTH Token and OAUTH Secret to the twitter plugin")
print("-------------------------------------------------------\n")
print("oauth token       : %s" % OAUTH_TOKEN)
print("oauth token secret: %s" % OAUTH_TOKEN_SECERT)

