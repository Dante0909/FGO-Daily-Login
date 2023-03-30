import os
import requests
import time
import json
import fgourl
import user
import coloredlogs
import logging
import mytime
import datetime

from dotenv import load_dotenv
load_dotenv()
# Enviroments Variables
userIds = os.environ['userIds'].split(',')
authKeys = os.environ['authKeys'].split(',')
secretKeys = os.environ['secretKeys'].split(',')
fate_region = os.environ['fateRegion']
webhook_discord_url = os.environ['webhookDiscord']
UA = os.environ['UserAgent']

if UA != 'nullvalue':
    fgourl.user_agent_ = UA

userNums = len(userIds)
authKeyNums = len(authKeys)
secretKeyNums = len(secretKeys)

logger = logging.getLogger("FGO Daily Login")
coloredlogs.install(fmt='%(asctime)s %(name)s %(levelname)s %(message)s')


def get_latest_verCode():
    endpoint = ""

    if fate_region == "NA":
        endpoint += "https://raw.githubusercontent.com/O-Isaac/FGO-VerCode-extractor/NA/VerCode.json"
    else:
        endpoint += "https://raw.githubusercontent.com/O-Isaac/FGO-VerCode-extractor/JP/VerCode.json"

    response = requests.get(endpoint).text
    response_data = json.loads(response)

    return response_data['verCode']


def main():
    if userNums == authKeyNums and userNums == secretKeyNums:
        logger.info('Getting Lastest Assets Info')
        fgourl.set_latest_assets()

        try:
            secondAccount = user.user(userIds[0], authKeys[0], secretKeys[0])
            time.sleep(3)
            logger.info('Logging into bot')
            secondAccount.topLogin()
            time.sleep(2)
            secondAccount.topHome()
            time.sleep(2)
            lastActualLogin = secondAccount.checkFriends()
            time.sleep(2)
            lastBotLogin = int(requests.get("https://dante.square.ovh/lastlogin").content)

            if(lastActualLogin != lastBotLogin):

                timeDiff = datetime.datetime.now() - datetime.datetime.fromtimestamp(lastActualLogin)
                if(timeDiff.seconds < 18000):
                    logger.info("Last login by player is less than 5 hours ago, exiting")
                    return
                
            mainAccount = user.user(userIds[1], authKeys[1], secretKeys[1])
            time.sleep(3)
            logger.info("Logging into main account")
            newLastLogin = mainAccount.topLogin()
            time.sleep(2)
            requests.get('https://dante.square.ovh/lastlogin/' + str(newLastLogin))
            time.sleep(2)
            mainAccount.topHome()
            hour = datetime.datetime.utcnow().time().hour
            if hour == 9:
                logger.info('Throw daily friend summon!')
                mainAccount.drawFP()
                time.sleep(2)
            else:
                logger.info('Not throwing daily friend summon')

        except Exception as ex:
            logger.error(ex)

if __name__ == "__main__":
    main()
