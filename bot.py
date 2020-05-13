from requests_oauthlib import OAuth1Session
import time


class Twitter(object):

    def __init__(self, key, secret_key):
        self.key = key
        self.secret_key = secret_key
        self.oauth = self.authenticate()

    def authenticate(self):
        # Get request token
        request_token_url = "https://api.twitter.com/oauth/request_token"
        oauth = OAuth1Session(self.key, client_secret=self.secret_key)
        fetch_response = oauth.fetch_request_token(request_token_url)
        resource_owner_key = fetch_response.get('oauth_token')
        resource_owner_secret = fetch_response.get('oauth_token_secret')
        print("Got OAuth token: %s" % resource_owner_key)

        # # Get authorization
        base_authorization_url = 'https://api.twitter.com/oauth/authorize'
        authorization_url = oauth.authorization_url(base_authorization_url)
        print('Please go here and authorize: %s' % authorization_url)
        verifier = input('Paste the PIN here: ')

        # # Get the access token
        access_token_url = 'https://api.twitter.com/oauth/access_token'
        oauth = OAuth1Session(self.key,
                              client_secret=self.secret_key,
                              resource_owner_key=resource_owner_key,
                              resource_owner_secret=resource_owner_secret,
                              verifier=verifier)
        oauth_tokens = oauth.fetch_access_token(access_token_url)

        access_token = oauth_tokens['oauth_token']
        access_token_secret = oauth_tokens['oauth_token_secret']

        return OAuth1Session(self.key,
                             client_secret=self.secret_key,
                             resource_owner_key=access_token,
                             resource_owner_secret=access_token_secret)

    def find_reply_to(self, screen_name_of_reply, author_of_tweet):
        response = self.oauth.get(
            f"https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name={screen_name_of_reply}&count=50")
        if response.status_code == 200:
            resp_dict = response.json()
            for tweet in resp_dict:
                if tweet['in_reply_to_screen_name'] == author_of_tweet:
                    return tweet

    def reply_to_reply(self, status_id, status, media=''):

        url = "https://api.twitter.com/1.1/statuses/update.json"
        data = {
            'status': f"{status}",
            'in_reply_to_status_id': status_id,
            'auto_populate_reply_metadata': True
        }
        if media:
            uploaded_media = self.upload_an_image(media)
            if uploaded_media.status_code == 200:
                data['media_ids'] = uploaded_media.json()['media_id_string']
        return self.oauth.post(url, params=data)

    def upload_an_image(self, media_path):
        url = 'https://upload.twitter.com/1.1/media/upload.json'
        data = {
            'media': open(media_path, 'rb').read()
        }
        resp = self.oauth.post(url, files=data)
        return resp


if __name__ == '__main__':

    # configure Twitter object
    API_key = 'Nope'  # use ur key
    API_secret_key = 'Maybe next time'  # use ur key
    Twitter_obj = Twitter(API_key, API_secret_key)

    # get latest reply to Trump from the user - 'itsJeffTiedrich'
    from_user = 'itsJeffTiedrich'
    to_user = 'realDonaldTrump'
    latest_reply = Twitter_obj.find_reply_to(from_user, to_user)
    print(latest_reply)
    while True:
        reply = Twitter_obj.find_reply_to(from_user, to_user)
        if reply['id'] != latest_reply['id']:
            Twitter_obj.reply_to_reply(reply['id_str'], 'U R A BOT', 'media/trump_tweeted_starter_kit.jpg')
            print('replied :)')
            latest_reply = reply
        time.sleep(5)
