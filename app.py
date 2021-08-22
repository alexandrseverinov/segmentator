import os
import io
import csv
import logging

import pandas as pd
from sklearn.model_selection import train_test_split
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


PORT = int(os.environ.get("PORT", 5000))

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)
TOKEN = os.environ["BOT_TOKEN"]


def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text(
        "Hi! Send me your csv file with users"
        "I'll split to specified number of segments for you"
    )


def _help(update, context):
    """Send a message when the command /_help is issued."""
    update.message.reply_text(
        "Send me your csv file with users"
        "I'll split to specified number of segments for you"
    )


def echo(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def process_csv_flow(update, context):
    csv_file = ...
    n_segments = ask_for_n_segments()
    segments_sizes = ask_for_segments_sizes()

    segments = process_csv(csv_file, n_segments, segments_sizes)
    for i, df in enumerate(segments):
        s = io.StringIO()
        csv.writer(s).writerows(df)
        s.seek(0)

        buf = io.BytesIO()
        buf.write(s.getvalue().encode())
        buf.seek(0)

        i = 0
        buf.name = f"segment_{i}.csv"

        context.bot.send_document(
            chat_id=update.message.chat_id,
            document=buf
        )


def process_csv(file, n_segments, segments_size):
    data = pd.read_csv(file, sep=";").drop_duplicates()
    # print(data.shape[0])
    segments = []
    for i in range(n_segments):
        data, to_save = train_test_split(
            data, test_size=segments_size[i]
        )
        segments.append(to_save)

    return segments


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bots token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    # dp.add_handler(CommandHandler("coffee", get_places))
    dp.add_handler(CommandHandler("help", _help))

    # on non command i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    dp.add_handler(MessageHandler(Filters.location, ))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_webhook(
        listen="0.0.0.0", port=int(PORT), url_path=TOKEN
    )
    updater.bot.setWebhook("https://segmentator.herokuapp.com/" + TOKEN)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    main()
