from .objects import *
import requests
from . import exceptions

# Тут главное

class Client:
    def __init__(self, token: str):
        self.token = token
        self.url = 'https://api.fruitspace.one/v2/'
        self.headers = {
            "Authorization": token
        }
    def fetch_gdps(self, gdpsid, expiry_date=None):
        req = requests.get(self.url+'fetch/gd/info/'+gdpsid)
        json = req.json()
        json['expire_date'] = expiry_date
        return Server(json)

    def get_user_servers(self):
        req = requests.get(self.url+'servers', headers=self.headers)
        if req.json()['status'] == 'error':
            if req.json()['message'] == 'Unauthorized':
                raise exceptions.UnauthorizedError('You\'re unauthorized')
        servers = []
        for srv in req.json()['gd']:
            servers.append(self.fetch_gdps(srv['srvid'], srv['expire_date']))
        return servers

    def get_gdps_config(self, gdps):
        req = requests.get(self.url+f'servers/gd/{gdps}', headers=self.headers)
        if 'status' in req.json():
            if req.json()['status'] == 'error':
                if req.json()['message'] == 'You have no permission to manage this server':
                    raise exceptions.NoPermissionError('You have no permission to manage this server')
                elif req.json()['message'] == 'Unauthorized':
                    raise exceptions.UnauthorizedError('You\'re unauthorized')
        return req.json()

    def delete_gdps(self, gdps):
        req = requests.delete(self.url+f'servers/gd/{gdps}', headers=self.headers)
        if req.json()['status'] == 'error':
            if req.json()['message'] == 'You have no permission to manage this server':
                raise exceptions.NoPermissionError('You have no permission to manage this server')
            elif req.json()['message'] == 'Unauthorized':
                raise exceptions.UnauthorizedError('You\'re unauthorized')
        return req.json()

    def get_gdps_logs(self, gdps: str, type: int, page: int):
        req = requests.post(self.url+f'servers/gd/{gdps}/logs', headers=self.headers, data={'type': type, 'page': page})
        if req.json()['status'] == 'error':
            if req.json()['message'] == 'You have no permission to manage this server':
                raise exceptions.NoPermissionError('You have no permission to manage this server')
            elif req.json()['message'] == 'Unauthorized':
                raise exceptions.UnauthorizedError('You\'re unauthorized')
        return req.json()

    def upload_music(self, gdps: str, type: str, url: str):
        req = requests.put(self.url+f'servers/gd/{gdps}/music', headers=self.headers, data={'type': type, 'url': url})
        if req.json()['status'] == 'error':
            if req.json()['message'] == 'You have no permission to manage this server':
                raise exceptions.NoPermissionError('You have no permission to manage this server')
            elif req.json()['message'] == 'Unauthorized':
                raise exceptions.UnauthorizedError('You\'re unauthorized')
        return req.json()

class GDPS:
    def __init__(self, gdps: str):
        self.url = f'https://rugd.gofruit.space/{gdps}/db/'

    def get_user(self, accid: int):
        req = requests.post(self.url+'getGJUserInfo20.php', data={"secret": "Wmfd2893gb7", "targetAccountID": accid})
        return User(req.text)

    def download_level(self, levelid: int):
        req = requests.post(self.url+'downloadGJLevel22.php', data={"secret": "Wmfd2893gb7", "levelID": levelid})
        return Level(req.text)

    def get_comments(self, levelid):
        req = requests.post(self.url + 'getGJComments.php', data={"secret": "Wmfd2893gb7", "levelID": levelid})
        comments = []
        for comment in req.text.split('|'):
            comments.append(Comment(comment))
        return comments

    def get_acc_comments(self, userid: int, page: int):
        req = requests.post(self.url + 'getGJAccountComments20.php', data={"secret": "Wmfd2893gb7", "accountID": userid, "page": page})
        acs = []
        for ac in req.text.split('#')[0].split('|'):
            acs.append(AccComment(ac))
        return acs

    def register_account(self, username: str, password: str, email: str):
        req = requests.post(self.url+'accounts/registerGJAccount.php', data = {
            "userName": username,
            "password": password,
            "email": email,
            "secret": "Wmfv3899gc9"
        })
        return req.text

    def get_song(self, song_id):
        req = requests.post(self.url+'getGJSongInfo.php', data={"songID": song_id})
        return Song(req.text)

    def get_daily(self):
        req = requests.post(self.url+'getGJDailyLevel.php', data={"secret": "Wmfd2893gb7"})
        return {'remaining_time': req.text.split('|')[1], 'level': self.download_level(int(req.text.split('|')[0]))}

    def get_weekly(self):
        req = requests.post(self.url+'getGJDailyLevel.php', data={"secret": "Wmfd2893gb7", "weekly": 1})
        return {'remaining_time': req.text.split('|')[1], 'level': self.download_level(int(req.text.split('|')[0]))}