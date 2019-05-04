# Import libraries
import telegram
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
import functions
import atexit

# Main code


def main():

    # Initiate logging module
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    # Retrieve token from external file
    # Token.txt should only contain 1 line which is the api token of your bot.
#	f = open('token.txt', 'r')
#	tokenId = f.readline()
#	f.close()
    tokenId = 'Bot token here'
    # Retrieve user data from external file
    # UserDetails.txt will contain XYZ data in the format ....

    # Create bot object and its corresponding updater, dispatcher and job queue
    bot = telegram.Bot(token=tokenId)
    updater = Updater(token=tokenId)
    dispatcher = updater.dispatcher
    jqueue = updater.job_queue

    # Scheduled jobs
    job_rollingBanLimit = jqueue.run_repeating(
        functions.rollingBanLimitLogic, interval=1800, first=0)
    job_getAdmins = jqueue.run_repeating(
        functions.getAdmins, interval=86400, first=0)
    job_rollingBanRemoval = jqueue.run_repeating(
        functions.rollingBanRemovalLogic, interval=10800, first=0)

    # Enable scheduled jobs
    job_rollingBanLimit.enabled = True
    job_getAdmins.enabled = True
    job_rollingBanRemoval.enabled = True

    # Creating hanlders
    start_handler = CommandHandler('start', functions.start)
    help_handler = CommandHandler('help', functions.start)
    setVoteLimit_handler = CommandHandler(
        'setVoteLimit', functions.setVoteLimit, pass_args=True)
    getVoteLimit_handler = CommandHandler(
        'getVoteLimit', functions.getVoteLimit)
    setBanLimit_handler = CommandHandler(
        'setBanLimit', functions.setBanLimit, pass_args=True)
    getBanLimit_handler = CommandHandler('getBanLimit', functions.getBanLimit)
    getTimeOfBans_handler = CommandHandler(
        'getTimeOfBans', functions.getTimeOfBans)
    getPending_handler = CommandHandler('getPending', functions.getPending)
    ban_handler = MessageHandler(Filters.command, functions.ban)
    callback_handler = CallbackQueryHandler(functions.processCallback)

    # Adding the handlers to the dispatcher
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(setVoteLimit_handler)
    dispatcher.add_handler(getVoteLimit_handler)
    dispatcher.add_handler(setBanLimit_handler)
    dispatcher.add_handler(getBanLimit_handler)
    dispatcher.add_handler(getTimeOfBans_handler)
    dispatcher.add_handler(getPending_handler)
    dispatcher.add_handler(ban_handler)
    dispatcher.add_handler(callback_handler)

    # Register exit handler when keyboard interupt (ctrl + c) is detected
    atexit.register(functions.exit_handler)

    # Start the bot
    print("Bot started!")
    updater.start_polling(clean=True)


if __name__ == "__main__":
    main()
