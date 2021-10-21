import threading
import requests, time, json, random
import dateutil.parser as dp
from requests.auth import HTTPProxyAuth

__ownerId = 93937677 #YOUR ACCOUNT'S ID
cookie = 'YOUR_COOKIE_HERE'
ownersUrl = 'https://inventory.roblox.com/v2/assets/' # %d/owners?limit=10
sendTradeUrl = 'https://trades.roblox.com/v1/trades/send'
canTrade = 'https://trades.roblox.com/v1/users/' # %d/can-trade-with

proxies = [
	# INSERT PROXIES HERE AS LIST
]

AlreadyTradingWith = {}

with open('indexed.txt', 'r') as file:
    f = file.read().replace('\n', '')
    file.close()
indexedUsers = json.loads(f)

with open('whitelist.txt', 'r') as filew:
    w = filew.read().replace('\n', '')
    filew.close()
whitelist = json.loads(w)

def getProxy():
    return proxies[random.randrange(len(proxies))]

def recentlyOnline(USERID):
    userlastonline = requests.get(url='https://api.roblox.com/users/' + str(USERID) + '/onlinestatus/', proxies={'https': getProxy()}).json()
    lastonline = userlastonline['LastOnline']
	#print(lastonline)
    parsed_time = dp.parse(lastonline)
    time_in_seconds = parsed_time.timestamp()
    final_time = time.time()-time_in_seconds

    return final_time/259200 <= 1

def CanUserTrade(USERID):
    r = requests.get(canTrade + str(USERID) + '/can-trade-with', headers={'cookie': f'.ROBLOSECURITY={cookie}' + ';'}, proxies={'https': getProxy()}).json()
    if 'errors' in r:
        print('Delaying for 7 seconds due to rate limitation')
        time.sleep(7)
        return CanUserTrade(USERID)
    
    if r['canTrade'] == True:
        return True
    return False

OfferItem1 = input('Item UAID #1 you are offering > ')
OfferItem2 = input('Item UAID #2 you are offering (optional) > ')
OfferItem3 = input('Item UAID #3 you are offering (optional) > ')
OfferItem4 = input('Item UAID #4 you are offering (optional) > ')

Requesting1 = input('Item ID #1 you are requesting > ')

itemId = Requesting1

ItemsSending = []
ItemsSending.insert(1, int(OfferItem1))
if OfferItem2.isnumeric():
    ItemsSending.insert(1, int(OfferItem2))
    if OfferItem3.isnumeric():
        ItemsSending.insert(1, int(OfferItem3))
        if OfferItem4.isnumeric():
	        ItemsSending.insert(1, int(OfferItem4))


XCSRF_Token = None
def loadXCSRF_Token():
    auth_response = requests.post('https://auth.roblox.com/v1/logout', headers={'cookie': f'.ROBLOSECURITY={cookie}' + ';'})
    if 'x-csrf-token' in auth_response.headers:
        global XCSRF_Token
        XCSRF_Token = auth_response.headers['x-csrf-token']
    else:
        print('exit')
        exit()


def sendTrade(userId, request):
    print('Sending trade to', userId)
    data = json.dumps({
        "offers": [
            {
                "userId": __ownerId,
                "userAssetIds": ItemsSending,
                "robux": 0
            },
            {
                "userId": userId,
                "userAssetIds": [
                    request
                ],
                "robux": 0
            }
        ]
    })

    loadXCSRF_Token()
    requests.post("https://trades.roblox.com/v1/trades/send", data=data,  headers={'cookie': f'.ROBLOSECURITY={cookie}', 'Content-Type': 'application/json', 'X-CSRF-TOKEN': XCSRF_Token}, proxies={'https': getProxy()}).json()
  

index = 0
owners = requests.get(ownersUrl + str(itemId) + '/owners?limit=100', headers={'cookie': f'.ROBLOSECURITY={cookie}' + ';'}).json()
while True:
    print('\n', index, '\n')
    for x in owners['data']:
        index += 1
        try:
            if not x['owner']:
                continue
            
            ownerId = str(x['owner']['id'])
            if ownerId in AlreadyTradingWith:
                print('Already trading with', ownerId)
                continue
            
            if ownerId in indexedUsers:
                print('Passed', ownerId)
                continue
                 
            if not ownerId in whitelist:   
                if not recentlyOnline(x['owner']['id']):
                    indexedUsers[x['owner']['id']] = True
                    continue
                if not CanUserTrade(x['owner']['id']):
                    indexedUsers[x['owner']['id']] = True
                    continue
            else:
                print(ownerId, 'whitelisted')
            
            AlreadyTradingWith[ownerId] = True
            
            f = open('indexed.txt', 'w')
            f.write(json.dumps(indexedUsers))
            f.close()
            
            whitelist[x['owner']['id']] = True
            f = open('whitelist.txt', 'w')
            f.write(json.dumps(whitelist))
            f.close()

            def TRADE():
                sendTrade(x['owner']['id'], x['id'])
            threading.Thread(target=TRADE, args=()).start()
        except:
            print('DUMPED')


    if owners['nextPageCursor']:
        owners = requests.get(ownersUrl + str(itemId) + '/owners?cursor=' + owners['nextPageCursor'] + '&limit=100', headers={'cookie': f'.ROBLOSECURITY={cookie}' + ';'}, proxies={'https': getProxy()}).json()
    else:
        break
