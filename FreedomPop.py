import requests, urllib, json, logging, sys, base64, datetime, math
import pprint

class FreedomPop:
    session = requests.Session() 
    #logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger('FreedomPop')
    #handler = logging.StreamHandler()
    #logger.addHandler(handler)
    #logger.setLevel(logging.DEBUG)

    user_token = None
    out = None
   
    identity_url = "https://my.freedompop.com/api/identity"
    user_url = "https://my.freedompop.com/api/user/{}/"
    accounts_url = "https://my.freedompop.com/api/user/{}/accounts"
    usage_url = "https://my.freedompop.com/api/account/{}/usage/{}-activity/current"

    MB = 1024*1024;

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.out = open("{}.log".format( self.username ), 'wt')

    def __exit__(self, exc_type, exc_value, traceback):
        self.session.cookies.clear()
        if self.out is not None:
            self.out.close()

    def _identityLogin(self):
        try:
            resp = self.session.post( FreedomPop.identity_url, json={"username": self.username, "password": self.password})
            if resp.status_code == 200:
                self.user_token = resp.json()["sub"]
                self.logger.debug("User token: %s", self.user_token) 
            else:
                self.logger.warning("Account %s login Error!", self.username)

        except:
            self.logger.warning("Network Error!")
        return True

    def getDataFromUrl(self, url):
        try:
            resp = self.session.get(url)
            if resp.status_code == 200:
                data = resp.json()
                return data
            else:
                self.logger.warning("Unauthorized access")
        except:
            self.logger.warning("Network Error!")
        return None

    def getUserInfo(self):
        if self.user_token is None:
            self._identityLogin()
        if self.user_token is not None:
            return self.getDataFromUrl(FreedomPop.user_url.format(self.user_token))
        return None

    def getAccountsInfo(self):
        if self.user_token is None:
            self._identityLogin()
        if self.user_token is not None:
            return self.getDataFromUrl(FreedomPop.accounts_url.format(self.user_token))
        return None

    def _getUsage(self, deviceId, item ):
        return self.getDataFromUrl( FreedomPop.usage_url.format( deviceId, item) ) 

    def getPhoneUsage(self, deviceId ):
        return self._getUsage(deviceId, "phone")

    def getDataUsage(self, deviceId ):
        return self._getUsage(deviceId, "data")

    def getPhoneNumber(device):
        return device["fpopPhone"]
    
    def getDeviceId(device):
        return device["externalId"]

    def getPlan(device):
        return device["plan"]

    def _getPlanInfo(phoneUsage, planName, type = None):
        info = None
        for plan in phoneUsage["phoneActivityPlans"]:
            if plan["voicePlanType"] == planName:
                if type is None: 
                    info = plan
                else:
                    info = plan[type]
                break
        return info

    def getTotalTexts(phoneUsage):
        total = 0
        info = FreedomPop._getPlanInfo( phoneUsage, "MAIN", "text" )
        if info is not None:
            total = info["totalAllocated"] 
        return total
        
    def getUsedTexts(phoneUsage):
        used = 0
        info = FreedomPop._getPlanInfo( phoneUsage, "MAIN", "text" )
        if info is not None:
            used = info["totalUsed"]
        return used
        
    def getTotalMinutes(phoneUsage):
        total = 0
        info = FreedomPop._getPlanInfo( phoneUsage, "MAIN", "talk" )
        if info is not None:
            total = round( info["totalAllocated"] / 60 )
        return total
        
    def getUsedMinutes(phoneUsage):
        used = 0
        info = FreedomPop._getPlanInfo( phoneUsage, "MAIN", "talk" )
        if info is not None:
            used = math.ceil( info["totalUsed"] / 60 )
        return used
        
    def getTotalData(dataUsage):
        total = dataUsage["totalAllocated"]
        return total / FreedomPop.MB 

    def getUsedData(dataUsage):
        used = dataUsage["totalUsed"]
        return used / FreedomPop.MB 

    def getEndTime(dataUsage):
        endTime = datetime.datetime.fromtimestamp(dataUsage["endTime"] / 1000)
        return endTime

    def getDeltaFromNow(nextTime):
        return nextTime - datetime.datetime.now()

    def getBilling(self): 
        if self.user_token is None:
            self._identityLogin()
        try:
            resp = self.session.get("https://my.freedompop.com/billing")
            print( resp.text )
        except:
            self.logger.warning("Network Error!")
        return None
    
    def printSummary(self):
        accounts = self.getAccountsInfo()
        pp = None
        if self.out is not None:
            pp = pprint.PrettyPrinter(stream=self.out)
        if pp is not None:
            pp.pprint( accounts )
        for device in accounts:
            number = FreedomPop.getPhoneNumber( device )
            id = FreedomPop.getDeviceId( device )
            plan = FreedomPop.getPlan( device )
            phone = self.getPhoneUsage(id)
            data = self.getDataUsage(id)
            if pp is not None:
                pp.pprint( phone )
                pp.pprint( data )
            endTime = FreedomPop.getEndTime( data )
            delta = FreedomPop.getDeltaFromNow( endTime )
            print( "{}({}): {}/{} minutes {}/{} text messages {}MB/{}MB mobile data, plan {} renew in {} days {} hours ({})".format( 
                self.username, number,
                FreedomPop.getUsedMinutes(phone), FreedomPop.getTotalMinutes(phone) , 
                FreedomPop.getUsedTexts(phone), FreedomPop.getTotalTexts(phone), 
                round( FreedomPop.getUsedData(data), 2), FreedomPop.getTotalData(data),
                plan,
                delta.days, round(delta.seconds / 3600), endTime ) )
        

