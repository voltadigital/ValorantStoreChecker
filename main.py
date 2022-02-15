import json
import asyncio
import aiohttp
import re

riotuser = input('user')
riotpass = input('pass')

async def run(formuser, formpass):
    session = aiohttp.ClientSession()
    headers = {
     'User-Agent': 'RiotClient/43.0.1.4195386.4190634 rso-auth (Windows;10;;Professional, x64)'
      }

    data = {
        'client_id': 'play-valorant-web-prod',
        'nonce': '1',
        'redirect_uri': 'https://playvalorant.com/opt_in',
        'response_type': 'token id_token',
    }
    await session.post('https://auth.riotgames.com/api/v1/authorization', headers=headers, json=data)

    data = {
        'type': 'auth',
        'username': formuser,
        'password': formpass
    }
    async with session.put('https://auth.riotgames.com/api/v1/authorization', 
headers=headers, json=data) as r:
          data = await r.json()
    if data['type'] == "multifactor":
        mfacode = input('Please Enter the MFA code!')
        mfa = {
          "type":"multifactor",
          "code": mfacode,
          "rememberDevice": "false"
        }
        async with session.put('https://auth.riotgames.com/api/v1/authorization', json=mfa) as r:
            data = await r.json()
    pattern = re.compile('access_token=((?:[a-zA-Z]|\d|\.|-|_)*).*id_token=((?:[a-zA-Z]|\d|\.|-|_)*).*expires_in=(\d*)')
    data = pattern.findall(data['response']['parameters']['uri'])[0]
    access_token = data[0]
    id_token = data[1]
    expires_in = data[2]

    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    async with session.post('https://entitlements.auth.riotgames.com/api/token/v1', headers=headers, json={}) as r:
        data = await r.json()
    entitlements_token = data['entitlements_token']

    async with session.post('https://auth.riotgames.com/userinfo', headers=headers, json={}) as r:
        data = await r.json()
    user_id = data['sub']
    headers = {
      'X-Riot-Entitlements-JWT' : entitlements_token,
      'Authorization': 'Bearer '+ access_token,
    }
    
    
    # Example Request. (Access Token and Entitlements Token needs to be included!)
    async with session.get('https://pd.na.a.pvp.net/store/v2/storefront/'+user_id, headers=headers, json=data) as r:
        data = json.loads(await r.text())
    allstore = data.get('SkinsPanelLayout')
    singleitems = allstore["SingleItemOffers"]
    skin1 = singleitems[0]
    skin2 = singleitems[1]
    skin3 = singleitems[2]
    skin4 = singleitems[3]

    async with session.get('https://valorant-api.com/v1/weapons/skinlevels/'+ skin1) as r:
        skin1 = json.loads(await r.text())

    async with session.get('https://valorant-api.com/v1/weapons/skinlevels/'+ skin2) as r:
        skin2 = json.loads(await r.text())

    async with session.get('https://valorant-api.com/v1/weapons/skinlevels/'+ skin3) as r:
        skin3 = json.loads(await r.text())

    async with session.get('https://valorant-api.com/v1/weapons/skinlevels/'+ skin4) as r:
        skin4 = json.loads(await r.text())

    skin1 = skin1.get('data')
    skin1 = skin1.get('displayName')
    skin2 = skin2.get('data')
    skin2 = skin2.get('displayName')
    skin3 = skin3.get('data')
    skin3 = skin3.get('displayName')
    skin4 = skin4.get('data')
    skin4 = skin4.get('displayName')

    print('You have:')
    print(skin1)
    print(skin2)
    print(skin3)
    print(skin4)

    await session.close()


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(run(riotuser, riotpass))
