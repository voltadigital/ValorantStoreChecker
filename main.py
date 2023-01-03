import aiohttp, json, requests
from fastapi import FastAPI
import os
import pprint

async def Auth():
	text0 = """
 		██╗   ██╗ █████╗ ██╗      ██████╗ ██████╗  █████╗ ███╗   ██╗████████╗
		██║   ██║██╔══██╗██║     ██╔═══██╗██╔══██╗██╔══██╗████╗  ██║╚══██╔══╝
		██║   ██║███████║██║     ██║   ██║██████╔╝███████║██╔██╗ ██║   ██║   
		╚██╗ ██╔╝██╔══██║██║     ██║   ██║██╔══██╗██╔══██║██║╚██╗██║   ██║   
		 ╚████╔╝ ██║  ██║███████╗╚██████╔╝██║  ██║██║  ██║██║ ╚████║   ██║   
		  ╚═══╝  ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝   
 	"""
	text1 = """
	 	███████╗████████╗ ██████╗ ██████╗ ███████╗     ██████╗██╗  ██╗███████╗ ██████╗██╗  ██╗███████╗██████╗ 
		██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗██╔════╝    ██╔════╝██║  ██║██╔════╝██╔════╝██║ ██╔╝██╔════╝██╔══██╗
		███████╗   ██║   ██║   ██║██████╔╝█████╗      ██║     ███████║█████╗  ██║     █████╔╝ █████╗  ██████╔╝
		╚════██║   ██║   ██║   ██║██╔══██╗██╔══╝      ██║     ██╔══██║██╔══╝  ██║     ██╔═██╗ ██╔══╝  ██╔══██╗
		███████║   ██║   ╚██████╔╝██║  ██║███████╗    ╚██████╗██║  ██║███████╗╚██████╗██║  ██╗███████╗██║  ██║
		╚══════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚══════╝     ╚═════╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝                                                                              
 """
	
	cw = os.get_terminal_size().columns
	pprint(center(text0,cw))
	pprint(center(text1,cw))
	
async def store(jwt, region):

	auth = await Auth()
	region = auth.region
  
  token_type = auth.token_type
  access_token = auth.access_token
  entitlements_token = auth.entitlements_token
  user_id = auth.user_id

  conn = aiohttp.TCPConnector()
  session = aiohttp.ClientSession(connector=conn)

  headers = {
   'X-Riot-Entitlements-JWT' : entitlements_token,
   'Authorization': 'Bearer '+ access_token,
  }

  async with session.get('https://pd.'+region+'.a.pvp.net/store/v1/offers/', headers=headers) as r:
    pricedata = await r.json()
  
  async with session.get('https://pd.'+ region +'.a.pvp.net/store/v2/storefront/'+ user_id, headers=headers) as r:
    data = json.loads(await r.text())
  allstore = data.get('SkinsPanelLayout')
  singleitems = allstore["SingleItemOffers"]
  skin1uuid = singleitems[0]
  skin2uuid = singleitems[1]
  skin3uuid = singleitems[2]
  skin4uuid = singleitems[3]

  async with session.get('https://valorant-api.com/v1/weapons/skinlevels/'+ skin1uuid) as r:
    skin1 = json.loads(await r.text())['data']['displayName']

  async with session.get('https://valorant-api.com/v1/weapons/skinlevels/'+ skin2uuid) as r:
    skin2 = json.loads(await r.text())['data']['displayName']

  async with session.get('https://valorant-api.com/v1/weapons/skinlevels/'+ skin3uuid) as r:
    skin3 = json.loads(await r.text())['data']['displayName']

  async with session.get('https://valorant-api.com/v1/weapons/skinlevels/'+ skin4uuid) as r:
    skin4 = json.loads(await r.text())['data']['displayName']
 
  def getprice(uuid):
    for item in pricedata['Offers']:
      if item["OfferID"] == uuid:
        return item['Cost']['85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741']

  def nightmarket(datad):
    out = []
    try:
      for item in datad["BonusStore"]["BonusStoreOffers"]:
        r = requests.get(f'https://valorant-api.com/v1/weapons/skinlevels/'+item['Offer']['Rewards'][0]['ItemID'])
        skin = r.json()
        data = {
          'name':skin['data']['displayName'],
          'uuid': item['Offer']['OfferID'],
          'price': {
            'oringinal':item['Offer']['Cost']['85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741'],
            'discount': item['DiscountPercent'],
            'final': item['DiscountCosts']['85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741'],
          }
        }
        out.append(data)
        return out
    except KeyError:
      print('no nm')
      return None
        
    


  sendit = {
    'store': [
      {
        "name": skin1,
        "uuid": skin1uuid,
        'price' : getprice(skin1uuid)
      },
      {
        "name": skin2,
        "uuid": skin2uuid,
        'price' : getprice(skin2uuid)
      },
      {
        "name": skin3,
        "uuid": skin3uuid,
        'price' : getprice(skin3uuid)
      },
      {
        "name": skin4,
        "uuid": skin4uuid,
        'price' : getprice(skin4uuid)
      }
    ],
    'nmdata' : nightmarket(data)
  }

  await session.close()
  return sendit
if __name__ == __main__:
	asyncio.run(store())