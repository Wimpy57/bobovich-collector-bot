import json
import os

from telegram import Update
from telegram.ext import ContextTypes, CallbackContext

import main

"""
    does not work without pages
"""
# async def show_all_currencies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # if not os.path.exists('all_currencies.json'):
    #     await main.load_all_currencies()
    #
    # with open('all_currencies.json', 'r') as json_file:
    #     all_currencies = json.load(json_file)["data"]
    #
    # reply = ""
    #
    # i = 0
    # for currency in all_currencies.values():
    #     i += 1
    #     reply += f"{currency["code"]} - {currency["name"]}\n"
    #     if i == 10:
    #         break
    #
    # await update.message.reply_text(reply)

async def new_plan(update: Update, context: CallbackContext) -> None:
    pass
