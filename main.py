import json
import os.path

import aiohttp

from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Application, InlineQueryHandler, ContextTypes

import config
import urls


async def handle_inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    if not query:
        return

    query_input = query.split()
    print(query_input)
    if len(query_input) not in (2, 3):
        return

    if not os.path.exists("latest_currencies.json"):
        await update_currencies_info(update, context)

    latest_currencies: dict
    with open("latest_currencies.json", "r") as json_file:
        latest_currencies = json.load(json_file)

    convert_from = query_input[0].upper()
    convert_to = query_input[-1].upper()
    data = latest_currencies["data"]

    if (convert_from in data.keys()) and (convert_to in data.keys()):
        amount = 1.0
        if len(query_input) == 3 and is_float(query_input[1].replace(",", ".")):
            amount = float(query_input[1].replace(",", "."))
        result = round(await convert_currency(data[convert_from], amount, data[convert_to]), 2)

        if not os.path.exists("all_currencies.json"):
            await load_all_currencies()

        all_currencies: dict
        with open("all_currencies.json", "r") as json_file:
            all_currencies = json.load(json_file)["data"]

        if result == int(result):
            result = int(result)
        if amount == int(amount):
            amount = int(amount)

        await update.inline_query.answer([InlineQueryResultArticle(
            id="0",
            title=f"{result} {convert_to}",
            input_message_content=InputTextMessageContent(
                message_text=f"{amount} {all_currencies[convert_from]["name"]} is {result} {all_currencies[convert_to]["name"]}",
            ),
            description=f"Convert {amount} {convert_from} to {convert_to}"
        )], cache_time=0)


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

async def load_all_currencies():
    all_currencies = await request(urls.CURRENCY_API_URL_CURRENCIES, {"apikey": config.CURRENCY_API_KEY})
    if not all_currencies:
        return

    with open("all_currencies.json", "w") as currencies_file:
        json.dump(all_currencies, currencies_file, indent=4)


def is_float(string: str) -> bool:
    try:
        float(string.strip())
    except (ValueError, TypeError):
        return False

    return True


async def convert_currency(convert_from: dict, amount: float, convert_to: dict) -> float:
    return (convert_to["value"] / convert_from["value"]) * amount


def main():
    app = Application.builder().token(config.BOT_TOKEN).build()
    app.add_handler(InlineQueryHandler(handle_inline_query))

    print("Bot is running")
    app.run_polling()


if __name__ == '__main__':
    main()