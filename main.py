import requests
from requests import Response
from telegram import Update
from telegram.ext import Application, InlineQueryHandler, ContextTypes

import config
import urls


async def handle_inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    if not query:
        return

    input = query.split()
    print(input)
    if len(input) != 3:
        return

    available_currencies_response: Response = requests.get(urls.FRANKFURTER_URL_AVAILABLE_CURRENCIES)
    print(available_currencies_response.status_code)
    if available_currencies_response.status_code != 200:
        return

    if (input[0] in available_currencies_response.json().keys()) and (input[-1] in available_currencies_response.json().keys()):
        print(available_currencies_response.json()[input[0]] + " converts to " + available_currencies_response.json()[input[-1]])


def main():
    app = Application.builder().token(config.BOT_TOKEN).build()
    app.add_handler(InlineQueryHandler(handle_inline_query))

    print("Bot is running")
    app.run_polling()


if __name__ == '__main__':
    main()