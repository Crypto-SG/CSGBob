from telegram import InlineKeyboardButton, InlineKeyboardMarkup,ChatAction
from threading import Thread
import time
from random import randint
import datetime
import json
import requests
# Config variables
voteLimit = 8
banLimit = 8
timeOfBans = list()
easteregg_list=['-1001375339070','-1001228209853','-1001123530370','-1001097080601']
hammer_repo=['https://thumbs.gfycat.com/DenseMatureBuckeyebutterfly-small.gif','https://thumbs.gfycat.com/GaseousHandyAmericanbadger-small.gif','https://thumbs.gfycat.com/AssuredActualCranefly-small.gif','https://gfycat.com/sizzlingindeliblegodwit-small.gif,https://gfycat.com/naughtyadorabledairycow-small.gif','https://gfycat.com/mintysnarlingargusfish-small.gif']
bob_repo=['https://thumbs.gfycat.com/WebbedSpicyGreathornedowl-small.gif','https://thumbs.gfycat.com/FatherlyWearyBlackfootedferret-small.gif']
channelHandle = "@CryptoSG"
# channelHandle = "https://t.me/joinchat/DAA6s1E-70Wdz_BYMotLwA"
# channelHandle = "@CryptoSGSpam"
admins = dict()
pending = dict()

def getReinhardt():
    try:
        url='https://api.gfycat.com/v1/gfycats/search?search_text=reinhardt&count=1000'
        print(f'Getting {url}')
        response=requests.get(url)
        print(f'response: {response.status_code}')
        if response.status_code==200:
            gifurl=response.json()['gfycats'][randint(1,999)]['content_urls']['max5mbGif']['url']
            print(f'returning {gifurl}')
            return gifurl
        else:
            print('Response code error')
            return 'https://thumbs.gfycat.com/DenseMatureBuckeyebutterfly-small.gif'
    except Exception as e:
        print(f'getReinhardt exception {e}')
        return 'https://thumbs.gfycat.com/DenseMatureBuckeyebutterfly-small.gif'

def delayedDel(bot, chat_id,message_id):
    time.sleep(60*5)
    bot.delete_message(chat_id, message_id)
    
def sendEasterEgg(bot, image_url,chat_id):#, reply_id):
    print('Sending easter egg')
#     image_url='https://thumbs.gfycat.com/WebbedSpicyGreathornedowl-size_restricted.gif'
    bot.sendChatAction(chat_id=chat_id, action=ChatAction.UPLOAD_PHOTO)
    sent=bot.sendDocument(chat_id=chat_id, document=image_url)
    sentMsgId=sent['message_id']
    if image_url in bob_repo:
        Thread(target=delayedDel,args=[bot,chat_id,sentMsgId]).start()
    
# Inline keyboard to be sent when /ban is initiated
def keyboard(numYesVotes, numNoVotes, id):
    # id = user Id of the target to be banned
    # Becareful of the capitalisation of y and n in yes and no
    keyboard = [[InlineKeyboardButton('Yes: ' + numYesVotes + '/' + str(voteLimit), callback_data='yes,' + id)],
              [InlineKeyboardButton('No: ' + numNoVotes + '/' + str(voteLimit), callback_data='no,' + id)]]
    return InlineKeyboardMarkup(keyboard)

# Inner function to get number of votes
def getNumVotes(votes):
    # Check if kicked or saved
    numYes = 0
    numNo = 0
    for k, v in votes.items():
        if v['value'] == 'yes':
            numYes = numYes + 1 
        else:
            numNo = numNo + 1
    return {'yes': str(numYes), 'no': str(numNo)}

# Inner function to process the inline callback query 
def processCallback(bot, update):
    # Get details about vote
    data = update.callback_query.data.split(',')
    id = int(data[1])

    try:
        details = pending[id]
    except KeyError:
        print("Critical error occured, check your dataset.")
        # Maybe make bot post sth so I can be notified
    else:
        chatId = details['chatId']
        messageId = details['messageId']
        botMessageId = details['botMessageId']
        voterId = update.callback_query.from_user.id
        voterName = getName(update.callback_query.from_user)

        # Process latest vote
        pending[id]['votes'][voterId] = {'voterName': voterName, 'value': data[0]}

    res = getNumVotes(pending[id]['votes'])
    numYes = int(res['yes'])
    numNo = int(res['no'])

    # Update text
    text = ''
    voterNames = ", ".join(getVoters(pending[id]['votes'], data[0]))
    if numYes >= voteLimit:
        text = "The community has decided that " + details['name'] + " should be banned. The following users voted yes: " + voterNames
        bot.edit_message_text(text=text, chat_id=chatId, message_id=update.callback_query.message.message_id) # Update the vote message
        bot.kick_chat_member(chatId, id, until_date=0)
        try:
            bot.delete_message(chatId, messageId) # Delete offender's message but you should be deleting all.
        except Exception:
            pass
        del pending[id]
        timeOfBans.append(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
#         if str(chatId) in easteregg_list:
#             sendEasterEgg(bot, hammer_repo[randint(0,len(hammer_repo)-1)], chatId)
#             sendEasterEgg(bot, getReinhardt(), chatId)


    elif numNo >= voteLimit:
        text = "The community has decided that " + details['name'] + " should not be banned. The following users voted no: " + voterNames
        bot.edit_message_text(text=text, chat_id=chatId, message_id=update.callback_query.message.message_id) # Update the vote message
        del pending[id]
    else:
        try:
            bot.edit_message_reply_markup(chatId, botMessageId, reply_markup = keyboard(res['yes'], res['no'], data[1]))
        except Exception as e:
            print("Num votes didn't change, ignoring error ", e)

# Inner function to get list of voters
def getVoters(voters, value):
    names = []
    for _, v in voters.items():
        if v['value'] == value:
            names.append(v['voterName'])
    return names

# Inner function to get list of admins
def getAdmins(bot, update):
    for admin in bot.get_chat(str(channelHandle)).get_administrators():
        try:
            id = admin.user.id
            name = getName(admin.user)
        except KeyError:
            print("Error retriving admin details, please see getAdmin function.")
        else:
            admins[id] = name
    print(admins)

# Inner function to check if id is an admin
def adminOnly(id):
    try:
        admins[id]
        return True
    except KeyError:
        return False

# Public function to get more details about the bot
def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text="This bot is created by @itsmestyj for the group " + 
                     "@CryptoSG. If you wish to use this bot, please pm me or @milodino.")

# Admin only function to set the limit for the number of votes required to ban
def setVoteLimit(bot, update, args):
    if adminOnly(update.message.from_user.id):
        if len(args) == 1 and args[0].isdigit():
            global voteLimit
            voteLimit = int(args[0])
            bot.send_message(chat_id=update.message.chat_id, text="Number of votes required to kick a user is updated to " + str(voteLimit))
        else:
            bot.send_message(chat_id=update.message.chat_id, text="Please enter 1 integer only.")
    else:
        bot.send_message(chat_id=update.message.chat_id, text="Only admins of @CryptoSG can call this function.")

# Pubic function to get the number of votes required to ban someone
def getVoteLimit(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="The number of votes required per ban is " + str(voteLimit) + ".")

# Admin only function to set the limit for the number of bans in the next 24 hours    
def setBanLimit(bot, update, args):
    if adminOnly(update.message.from_user.id):
        if len(args) == 1 and args[0].isdigit():
            global banLimit
            banLimit = int(args[0])
            bot.send_message(chat_id=update.message.chat_id, text="The maximum number of bans allowed per day is updated to " + str(banLimit))
        else:
            bot.send_message(chat_id=update.message.chat_id, text="Please enter 1 integer only.")
    else:
        bot.send_message(chat_id=update.message.chat_id, text="Only admins of @CryptoSG can call this function.")

# Public function to get the number of bans in a day
def getBanLimit(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="The number of bans allowed a day is " + str(banLimit) + ".")

# Admin only function to get the time of past bans
def getTimeOfBans(bot, update):
    if adminOnly(update.message.from_user.id):
        if len(timeOfBans) >= 1:
            text = "\n".join(timeOfBans)
        else:
            text = "No bans in the last 24 hours"
        bot.send_message(chat_id=update.message.chat_id, text=text)
    else:
        bot.send_message(chat_id=update.message.chat_id, text="Only admins of @CryptoSG can call this function.")


# Inner function to remove old bans after 24 hours has passed
def rollingBanLimitLogic(bot, update):
    global timeOfBans
    currTime = datetime.datetime.now()
    if len(timeOfBans) >= 1:
        oldTime = datetime.datetime.strptime(timeOfBans[0], '%d/%m/%Y %H:%M:%S')
        delta = datetime.timedelta(days=1)
        
        if oldTime + delta < currTime:
            # remove the latest time
            timeOfBans = timeOfBans[1:]
            print("removing 1 ban")
        else:
            print("time is not up yet")
    else:
        print("no bans yet in the past 24 hours")

# Inner function to remove votes that existed for more than 24 hours
def rollingBanRemovalLogic(bot, update):
    toDelete = list()
    global pending
    for k, v in pending.items():
        currTime = datetime.datetime.now()
        delta = datetime.timedelta(days=1)
        oldTime = v['time']
        if oldTime + delta < currTime:
            toDelete.append(k)
            print("Removing an old vote")
        else:
            print("Votes are still valid")

    for k in toDelete:
        bot.delete_message(pending[k]['chatId'], pending[k]['botMessageId'])
        del pending[k]

# Inner function to get the username (or first name if username doesn't exist)
def getName(user):
    name = user.username
    # Unable to do try and catch here cause username has a default value of None
    if name is None:
        name = user.first_name
    else:
        name = "@" + name
    return name

# Public function to ban someone
def ban(bot, update):
#     print(update.message.chat_id)
    # Check if command is /ban
    global easteregg_list
    
    if update.message.text == '/bob':
        # Check if number of bans < banLimit or if the requester is an admin
        if len(timeOfBans) < banLimit or update.message.from_user.id in admins.keys():
            try:
                reply = update.message.reply_to_message
                name = getName(reply.from_user)
                id = reply.from_user.id
            except AttributeError:
                # Cannot use KeyError because PTB's classes are not dictionaries
                bot.send_message(chat_id=update.message.chat_id, text="Reply to a message with /bob instead")
            else:
                # Check if the one being voted on is an admin
                if id in admins.keys():
                    bot.send_message(chat_id=update.message.chat_id, text="Nice try buddy but you can't kick an admin.")
                else:
                    # Checks pending dictionary
                    try:
                        pending[id]
                    except KeyError:
                        # Adding new vote into dictionary
                        chatId = update.message.chat_id
                        messageId = reply.message_id # This is for deleting the offending message
                        messageLink = ""
                        botMessageId = 0 # This is for editing the message sent out by the bot
                        requesterId = update.message.from_user.id
                        requesterName = getName(update.message.from_user)
                        
                        sendEasterEgg(bot, bob_repo[randint(0,len(bob_repo)-1)], chatId)
                        
                        text = requesterName + " would like to kick " + name + ". Do you agree?"
                        pending[id] = {'name': name, 'chatId': chatId, 'messageId': messageId, 'messageLink': messageLink, 'botMessageId': botMessageId, 'time': datetime.datetime.now(), 'votes': {requesterId: {'voterName': requesterName, 'value': 'yes'}}}
                        res = getNumVotes(pending[id]['votes'])

                        # Updating the bot message ID and message link url
                        retMsg = bot.send_message(chat_id=update.message.chat_id, text=text, reply_markup=keyboard(res['yes'], res['no'], str(id)))
                        botMessageId = retMsg['message_id']
                        pending[id]['botMessageId'] = botMessageId
                        pending[id]['messageLink'] = "https://t.me/{}/{}".format(update.message.chat.username, botMessageId)
                    else:
                        bot.send_message(chat_id=update.message.chat_id, text="Please cast your vote here instead " + pending[id]['messageLink'] + ".", disable_web_page_preview=True)
    

        else:
            listOfAdmins = ", ".join(("{}".format(v) for _, v in admins.items()))
            bot.send_message(chat_id=update.message.chat_id, text="The maximum number of bans in the past 24 hours has been hit. If a ban is required, please contact one of the following admins: " + listOfAdmins)
    
    elif update.message.text=='/BOB DO SOMETHING!' and str(update.message.chat_id) in easteregg_list:
        chat_id = str(update.message.chat_id)
        sendEasterEgg(bot, bob_repo[randint(0,len(bob_repo)-1)], chat_id)
        

# Admin only function to get which votes are still pending
def getPending(bot, update):
    if adminOnly(update.message.from_user.id):
        if len(pending.keys()):
            res = "\n\n".join(("{}: {}".format(k,v) for k, v in pending.items()))
            bot.send_message(chat_id=update.message.chat_id, text=res, disable_web_page_preview=True)
        else:
            bot.send_message(chat_id=update.message.chat_id, text="No bans are pending ")
    else:
        bot.send_message(chat_id=update.message.chat_id, text="Only admins of @CryptoSG can call this function.")

# Admin only function to reset the ban limit
def resetBanLimit(bot, update):
	print('in resetBanLimit')
#     global admins
#     print(admins)
	if adminOnly(update.message.from_user.id):
		global timeOfBans
		timeOfBans=[]
		bot.send_message(chat_id=update.message.chat_id, text=f"Current number of bans {len(timeOfBans)}")    
        
def exit_handler():
    print()
    # https://www.pythonforbeginners.com/cheatsheet/python-file-handling
    print("Keyboard Interupt detected, writing files to XYZ before the program closes")

