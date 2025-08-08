import json

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

    api_status_response: Response = requests.get(urls.CURRENCY_API_URL_STATUS + urls.API_KEY_STRING)

    if api_status_response.status_code != 200:
        return

    if api_status_response.json()["quotas"]["month"]["remaining"] == 0:
        await handle_out_of_limit_requests(update, context)
        return

    latest_currencies_response = requests.get(urls.CURRENCY_API_URL_LATEST + urls.API_KEY_STRING)

    with open("latest_currencies.json", "w") as latest_currencies_file:
        json.dump(latest_currencies_response.json(), latest_currencies_file, indent=4)

    # if (input[0] in api_status_response.json().keys()) and (input[-1] in api_status_response.json().keys()):
    #     print(api_status_response.json()[input[0]] + " converts to " + api_status_response.json()[input[-1]])

async def handle_out_of_limit_requests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass

def main():
    app = Application.builder().token(config.BOT_TOKEN).build()
    app.add_handler(InlineQueryHandler(handle_inline_query))

    print("Bot is running")
    app.run_polling()


if __name__ == '__main__':
    main()