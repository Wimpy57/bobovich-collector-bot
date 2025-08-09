import json
import os.path

import aiohttp

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
    if len(input) not in (2, 3):
        return

    if not os.path.exists("latest_currencies.json"):
        await update_currencies_info(update, context)

    latest_currencies: dict
    with open("latest_currencies.json", "r") as json_file:
        latest_currencies = json.load(json_file)

    convert_from = input[0].upper()
    convert_to = input[-1].upper()
    data = latest_currencies["data"]

    if (convert_from in data.keys()) and (convert_to in data.keys()):
        amount = 1.0
        if len(input) == 3 and is_float(input[1]):
            amount = float(input[1])
        await convert_currency(data[convert_from], amount, data[convert_to])

async def handle_out_of_limit_requests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass


#used to daily update info about currencies
async def update_currencies_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    api_status = await request(urls.CURRENCY_API_URL_STATUS, {"apikey":config.CURRENCY_API_KEY})
    if not api_status:
        return

    if api_status["quotas"]["month"]["remaining"] == 0:
        await handle_out_of_limit_requests(update, context)
        return

    latest_currencies = await request(urls.CURRENCY_API_URL_LATEST, {"apikey":config.CURRENCY_API_KEY})
    if not latest_currencies:
        return

    with open("latest_currencies.json", "w") as latest_currencies_file:
        json.dump(latest_currencies, latest_currencies_file, indent=4)


async def request(url: str, params: dict) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status != 200:
                return {}
            return await response.json()

def is_float(string: str) -> bool:
    try:
        float(string.strip())
    except (ValueError, TypeError):
        return False

    return True

async def convert_currency(convert_from: dict, amount: float, convert_to: dict):
    print(convert_from, amount, convert_to)

def main():
    app = Application.builder().token(config.BOT_TOKEN).build()
    app.add_handler(InlineQueryHandler(handle_inline_query))

    print("Bot is running")
    app.run_polling()

if __name__ == '__main__':
    main()