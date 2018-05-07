import requests, urllib, json, logging, sys, base64, datetime, math
import pprint
from colorCode import colors 

def printNoEnd( str ):
        print( str, end='' ) 

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
#    accounts_url = "https://my.freedompop.com/api/user/{}/accounts?expand=deviceProduct&expand=plan&expand=debitAccount"
#    accounts_url = "https://my.freedompop.com/api/user/{}/accounts?expand=plan"
    usage_url = "https://my.freedompop.com/api/account/{}/usage/{}-activity/current"
    subscription_url = "https://my.freedompop.com/api/account/{}/subscription/current"
    intl_url = "https://my.freedompop.com/api/account/{}/product/international/voice-plan/current"
    credit_url = "https://my.freedompop.com/api/account/{}/credit/balance"
    plan_url = "https://my.freedompop.com/api/account/{}/product/plan/current"
    service_url = "https://my.freedompop.com/api/account/{}/product/service/current"
    port_out_url = "https://my.freedompop.com/api/account/{}/phone/port-out-order"
    credit_balance_url = "https://my.freedompop.com/api/account/{}/credit/balance"
    credit_history_url = "https://my.freedompop.com/api/account/{}/credit?page=0&pageSize=2"

    MB = 1024*1024;

    resetColor = colors.reset
    warningColor = colors.fg.lightblue
    limitColor = colors.fg.lightred

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __exit__(self, exc_type, exc_value, traceback):
        self.session.cookies.clear()
        if self.out is not None:
            self.out.close()

    def enableLog(self):
        self.out = open("{}.log".format( self.username ), 'wt')
        
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

    def getSubscription(self, deviceId ):
        return self.getDataFromUrl( FreedomPop.subscription_url.format( deviceId ) )

    def getCreditBalance(self, deviceId ):
        return self.getDataFromUrl( FreedomPop.credit_balance_url.format( deviceId ) )

    def getCreditHistory(self, deviceId ):
        return self.getDataFromUrl( FreedomPop.credit_history_url.format( deviceId ) )

    def getDueDate(subscription):
        dueDate = subscription["nextBillingDate"]
        return datetime.datetime.utcfromtimestamp( dueDate/1000 )

    def getPaymentAmount(subscription):
        nextBillingAmountTotal = subscription["nextBillingAmountTotal"]
        return "{}{:.2f}".format( nextBillingAmountTotal["symbol"], nextBillingAmountTotal["amount"] )

    def getSubscriptionCredit(subscription):
        subscriptionCredit = subscription["subscriptionCredit"]
        return "{}{:.2f}".format( subscriptionCredit["symbol"], subscriptionCredit["amount"] )

    def getBillingDaysLeft(subscription):
        return subscription["billingDaysLeft"]

    def getTopUpCreditBalance(credit):
        return credit["current"]["balance"]

    def getPhoneNumber(device):
        return device["fpopPhone"]
    
    def getDeviceId(device):
        return device["externalId"]

    def getPlan(device):
        return device["plan"]

    def getIntlPlanName(self, deviceId ):
        plan = self.getDataFromUrl( FreedomPop.intl_url.format( deviceId ) )
        if plan is not None:
            return plan[0]["name"]
        return None

    def getPlanInfo(phoneUsage, planName, type = None):
        info = None
        for plan in phoneUsage["phoneActivityPlans"]:
            if plan["voicePlanType"] == planName:
                if type is None: 
                    info = plan
                else:
                    info = plan[type]
                break
        return info

    def getTotalTexts(phoneUsage, planName = 'MAIN'):
        total = 0
        info = FreedomPop.getPlanInfo( phoneUsage, planName, "text" )
        if info is not None:
            total = info["totalAllocated"] 
        return total
        
    def getUsedTexts(phoneUsage, planName = 'MAIN'):
        used = 0
        info = FreedomPop.getPlanInfo( phoneUsage, planName, "text" )
        if info is not None:
            used = info["totalUsed"]
        return used
        
    def getTotalMinutes(phoneUsage, planName = 'MAIN'):
        total = 0
        info = FreedomPop.getPlanInfo( phoneUsage, planName, "talk" )
        if info is not None:
            total = round( info["totalAllocated"] / 60 )
        return total
        
    def getUsedMinutes(phoneUsage, planName = 'MAIN'):
        used = 0
        info = FreedomPop.getPlanInfo( phoneUsage, planName, "talk" )
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
        endTime = datetime.datetime.utcfromtimestamp(dataUsage["endTime"] / 1000)
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

    def roundDays(dt):
        return round( dt.days + (dt.seconds / (60*60*24)) )
  
    def printPhoneUsage(self, phone):
        printNoEnd( "{:3d}/{}".format( FreedomPop.getUsedMinutes(phone), FreedomPop.getTotalMinutes(phone) ) )
        printNoEnd( " minutes " )
        printNoEnd( "{:3d}/{}".format( FreedomPop.getUsedTexts(phone), FreedomPop.getTotalTexts(phone) ) )
        printNoEnd( " text messages, " )

    def printGlobalUsage(self, phone):
        printNoEnd( "{:2d}/{}".format(
            FreedomPop.getUsedMinutes(phone, 'GLOBAL'), FreedomPop.getTotalMinutes(phone, 'GLOBAL')))
        printNoEnd( " intl' minutes, " )

    def highlightCheck(self, used, total, limit, colorCode):
        if limit is not None:
            if limit < 1:
                percentage = used / total
                if percentage > limit:
                    printNoEnd( colorCode )
                    return True
            elif limit > 1 and used > limit:
                printNoEnd( colorCode )
                return True
        return False

    def printDataUsage(self, data, warning, limit):
        used = FreedomPop.getUsedData(data)
        total = FreedomPop.getTotalData(data)
        percentage = used / total
        colored = self.highlightCheck( used, total, limit, self.limitColor )
        if colored is not True:
            colored = self.highlightCheck( used, total, warning, self.warningColor )
        printNoEnd( "{:6.2f}MB/{}MB".format(used, total) )
        if colored is not False:
            printNoEnd( self.resetColor );
        printNoEnd( " mobile data, " )

    def printBilling(self, subscription):
        printNoEnd( "next bill ")
        printNoEnd( "due date {} amount {} {} left ".format(
            FreedomPop.getDueDate(subscription).strftime('%Y-%m-%d'),
            FreedomPop.getPaymentAmount(subscription),
            FreedomPop.getBillingDaysLeft(subscription)) )

    def printTopUpCreditBalance(self, credit):
        balance = FreedomPop.getTopUpCreditBalance(credit)
        printNoEnd( "top-up credit {}{} ".format( balance['symbol'], balance['amount'] ) )

    def printSubscriptionCredit(self, subscription ):
        printNoEnd( "subscription credit {}".format( FreedomPop.getSubscriptionCredit(subscription) ) )

    def printNewLineLeading( newLine ):
        if newLine is True:
            print('')
            printNoEnd( '\t\t\t\t' )
        return False
        
    def printSummary(self, warning, limit):
        accounts = self.getAccountsInfo()
        pp = None

        if self.out is not None:
            pp = pprint.PrettyPrinter(stream=self.out)
        if pp is not None:
            pp.pprint( self.getUserInfo() )
            pp.pprint( accounts )
        for device in accounts:
            number = FreedomPop.getPhoneNumber( device )
            id = FreedomPop.getDeviceId( device )
            plan = FreedomPop.getPlan( device )
            phone = self.getPhoneUsage(id)
            data = self.getDataUsage(id)
            subscription = self.getSubscription(id)
            newLine = True
            if pp is not None:
                if phone is not None:
                    pp.pprint( phone )
                pp.pprint( data )
            printNoEnd( "{}({}):\t{}\t".format( self.username, number, plan ) )
            if phone is not None:
                self.printPhoneUsage(phone)
                if FreedomPop.getPlanInfo( phone, 'GLOBAL' ) is not None:
                    self.printGlobalUsage(phone)

            if data is not None:
                self.printDataUsage(data, warning, limit)

            if subscription is not None:
                self.printBilling(subscription)

            credit = self.getCreditBalance(id)
            if credit is not None:
                balance = FreedomPop.getTopUpCreditBalance(credit)
                if balance['amount'] > 0:
                    newLine = FreedomPop.printNewLineLeading( newLine )
                    self.printTopUpCreditBalance(credit)
            if subscription["subscriptionCredit"]["amount"] > 0:
                newLine = FreedomPop.printNewLineLeading( newLine )
                self.printSubscriptionCredit( subscription )


            print( "" )

#            endTime = FreedomPop.getEndTime( data )
#            deltaTime = FreedomPop.getDeltaFromNow( endTime )
#            if deltaTime.days > 1:
#                printNoEnd( "{} renew in {} days ({})".format(
#                    plan,
#                    FreedomPop.roundDays(deltaTime), endTime.strftime('%Y-%m-%d') ) )
#            else:
#                printNoEnd( "plan {} will renew in {} hours ({})".format(
#                    plan, round(deltaTime.seconds / 3600), endTime.strftime('%Y-%m-%d') ) )
#            print( " Billing Remaining {} days".format( device["trackingParams"]["BillingDaysRemaining"] ) )

