import aiohttp, json, requests
from fastapi import FastAPI
import os, sys
import asyncio
from riot_auth import RiotAuth, auth_exceptions
from getpass import getpass

cw = os.get_terminal_size().columns

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
		╚══════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚══════╝     ╚═════╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝"""
	

  print(text0.center(cw))
  print(text1.center(cw))


  build = requests.get('https://valorant-api.com/v1/version').json()['data']['riotClientBuild']
  print('Valorant Build '+build)

  RiotAuth.RIOT_CLIENT_USER_AGENT = build + '%s (Windows;10;;Professional, x64)'

  if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

  CREDS = input('Username:\n'), getpass('Password:\n')

  auth = RiotAuth()
  try: await auth.authorize(*CREDS)

  except auth_exceptions.RiotAuthenticationError:
    exit('Error: Auth Failed, Please check credentials and try again.')

  except auth_exceptions.RiotMultifactorError:
    exit('Accounts with MultiFactor enabled are not supported at this time.')
    
  return auth
	
async def store():

  auth = await Auth()

  print('Enter your region: \nna - North America, latam - Latin America, br -	Brazil, eu - Europe, ap - Asia Pacific, kr - Korea')
  region = input()
  
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
      return None
        
  ms_text = """
    ███╗   ███╗ █████╗ ██╗███╗   ██╗    ███████╗████████╗ ██████╗ ██████╗ ███████╗
    ████╗ ████║██╔══██╗██║████╗  ██║    ██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗██╔════╝
    ██╔████╔██║███████║██║██╔██╗ ██║    ███████╗   ██║   ██║   ██║██████╔╝█████╗  
    ██║╚██╔╝██║██╔══██║██║██║╚██╗██║    ╚════██║   ██║   ██║   ██║██╔══██╗██╔══╝  
    ██║ ╚═╝ ██║██║  ██║██║██║ ╚████║    ███████║   ██║   ╚██████╔╝██║  ██║███████╗
    ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝    ╚══════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚══════╝
                                                                              """.center(cw)
  print(ms_text)
  print(f"""
  
  {skin1} for {getprice(skin1uuid)}
  {skin2} for {getprice(skin2uuid)}
  {skin3} for {getprice(skin3uuid)}
  {skin4} for {getprice(skin4uuid)}
  """)
  
  nm = nightmarket(data)
  if nm != None:
    nm_text = """
      ███╗   ██╗██╗ ██████╗ ██╗  ██╗████████╗    ███╗   ███╗ █████╗ ██████╗ ██╗  ██╗███████╗████████╗
      ████╗  ██║██║██╔════╝ ██║  ██║╚══██╔══╝    ████╗ ████║██╔══██╗██╔══██╗██║ ██╔╝██╔════╝╚══██╔══╝
      ██╔██╗ ██║██║██║  ███╗███████║   ██║       ██╔████╔██║███████║██████╔╝█████╔╝ █████╗     ██║   
      ██║╚██╗██║██║██║   ██║██╔══██║   ██║       ██║╚██╔╝██║██╔══██║██╔══██╗██╔═██╗ ██╔══╝     ██║   
      ██║ ╚████║██║╚██████╔╝██║  ██║   ██║       ██║ ╚═╝ ██║██║  ██║██║  ██║██║  ██╗███████╗   ██║   
      ╚═╝  ╚═══╝╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝       ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝   ╚═╝                                                                                              
    """.center(cw)
    print(nm_text)
    nm_items = []

    for item in nm:
      nmitem_text = f"{item['name']} for {item['price']['final']} ({item['price']['oringinal']} with {item['price']['discount']}% discount) \n"
      nm_items.append(nmitem_text)

    print(''.join(nm_items))
  await session.close()
if __name__ == '__main__':
	asyncio.run(store())