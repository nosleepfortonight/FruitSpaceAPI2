from .objects import *
import requests
from . import exceptions
import aiohttp

# Тут главное

class Client:
    def __init__(self, token: str):
        self.token = token
        self.url = 'https://api.fruitspace.one/v2/'
        self.headers = {
            "Authorization": token
        }
        self.session = aiohttp.ClientSession()

    async def fetch_gdps(self, gdpsid, expiry_date=None):
        req = await self.session.post(self.url+'fetch/gd/info/'+gdpsid)
        json = await req.json()
        json['expire_date'] = expiry_date
        return Server(json)

    async def get_user_servers(self):
        req = await self.session.get(self.url+'servers', headers=self.headers)
        json = await req.json()
        if json['status'] == 'error':
            if json['message'] == 'Unauthorized':
                raise exceptions.UnauthorizedError('You\'re unauthorized')
        servers = []
        for srv in json['gd']:
            servers.append(self.fetch_gdps(srv['srvid'], srv['expire_date']))
        return servers

    async def get_gdps_config(self, gdps):
        req = await self.session.get(self.url+f'servers/gd/{gdps}', headers=self.headers)
        json = await req.json()
        if 'status' in json:
            if json['status'] == 'error':
                if json['message'] == 'You have no permission to manage this server':
                    raise exceptions.NoPermissionError('You have no permission to manage this server')
                elif json['message'] == 'Unauthorized':
                    raise exceptions.UnauthorizedError('You\'re unauthorized')
        return json

    async def delete_gdps(self, gdps):
        req = await self.session.delete(self.url+f'servers/gd/{gdps}', headers=self.headers)
        json = await req.json()
        if json['status'] == 'error':
            if json['message'] == 'You have no permission to manage this server':
                raise exceptions.NoPermissionError('You have no permission to manage this server')
            elif json['message'] == 'Unauthorized':
                raise exceptions.UnauthorizedError('You\'re unauthorized')
        return json

    async def get_gdps_logs(self, gdps: str, type: int, page: int):
        req = await self.session.post(self.url+f'servers/gd/{gdps}/logs', headers=self.headers, data={'type': type, 'page': page})
        json = await req.json()
        if json['status'] == 'error':
            if json['message'] == 'You have no permission to manage this server':
                raise exceptions.NoPermissionError('You have no permission to manage this server')
            elif json['message'] == 'Unauthorized':
                raise exceptions.UnauthorizedError('You\'re unauthorized')
        return json

    async def upload_music(self, gdps: str, type: str, url: str):
        req = await self.session.put(self.url+f'servers/gd/{gdps}/music', headers=self.headers, data={'type': type, 'url': url})
        json = await req.json()
        if json['status'] == 'error':
            if json['message'] == 'You have no permission to manage this server':
                raise exceptions.NoPermissionError('You have no permission to manage this server')
            elif json['message'] == 'Unauthorized':
                raise exceptions.UnauthorizedError('You\'re unauthorized')
        return json

class GDPS:
    def __init__(self, gdps: str):
        self.url = f'https://rugd.gofruit.space/{gdps}/db/'
        self.session = aiohttp.ClientSession()


    async def get_user(self, accid: int):
        req = await self.session.post(self.url+'getGJUserInfo20.php', data={"secret": "Wmfd2893gb7", "targetAccountID": accid})
        return User(await req.text())

    async def download_level(self, levelid: int):
        req = await self.session.post(self.url+'downloadGJLevel22.php', data={"secret": "Wmfd2893gb7", "levelID": levelid})
        print(req.text)
        return Level(await req.text())

    async def get_comments(self, levelid):
        req = await self.session.post(self.url + 'getGJComments.php', data={"secret": "Wmfd2893gb7", "levelID": levelid})
        text = await req.text()
        comments = []
        for comment in text.split('|'):
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
        req = requests.post(self.url+'getGJSongInfo.php', data = {
            "secret": "Wmfd2893gb7",
            "songID": song_id
        })
        return Song(req.text)

    def get_daily(self):
        req = requests.post(self.url+'getGJDailyLevel.php', data={"secret": "Wmfd2893gb7"})
        return {'remaining_time': req.text.split('|')[1], 'level': self.download_level(int(req.text.split('|')[0]))}

    def get_weekly(self):
        req = requests.post(self.url+'getGJDailyLevel.php', data={"secret": "Wmfd2893gb7", "weekly": 1})
        return {'remaining_time': req.text.split('|')[1], 'level': self.download_level(int(req.text.split('|')[0]))}

    def get_user_with_username(self, username):
        req = requests.post(self.url+'getGJUsers20.php', data={"secret": "Wmfd2893gb7", "str": username})
        req2 = self.get_user(int(req.text.split(':')[3]))
        return req2