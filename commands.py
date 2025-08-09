import json
import os

from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from SerializableObjects.plan import Plan
from conversation_states import ConversationStates

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



async def new_plan(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    chat = update.message.chat

    if context.chat_data.get("conversation_owner") and context.chat_data["conversation_owner"] != user.id:
        await chat.send_message("Another person is setting up a plan at the moment.")
        return ConversationHandler.END

    if chat.type == "private":
        await chat.send_message("This command is only available for group chats.")
        return ConversationHandler.END

    is_admin = False
    for admin in await chat.get_administrators():
        if admin.user.id == user.id:
            is_admin = True
            break

    if not is_admin:
        await chat.send_message("You need to be a group administrator to use this command.")
        return ConversationHandler.END

    context.chat_data["state"] = ConversationStates.NAMING
    context.chat_data["conversation_owner"] = user.id

    await chat.send_message("What should your plan be called?")

    return context.chat_data["state"]

async def name_plan(update: Update, context: CallbackContext) -> int:
    if context.chat_data["conversation_owner"] != update.message.from_user.id:
        return context.chat_data["state"]

    name = update.message.text

    if os.path.exists("groups.json"):
        with open("groups.json") as f:
            groups = json.load(f)
        for group in groups:
            if group["id"] != update.message.chat_id:
                continue
            for plan in group["plan"]:
                if plan["name"] != name:
                    continue
                await update.message.chat.send_message("There is already a plan with this name for this group.\n"
                                                       "Please think of a different plan name.")
                return context.chat_data["state"]

    newplan = Plan(name=name)
    await update.message.chat.send_message("What day do you want the plan to start from?\n"
                                           "Your response should be sent in this format: dd.mmm.yyyy\n"
                                           "If you want to start your plan today, just send a point (.)")

    context.chat_data["plan"] = newplan
    context.chat_data["state"] += 1
    return context.chat_data["state"]

async def cancel(update: Update, context: CallbackContext) -> int:
    context.chat_data.pop("conversation_owner")
    context.chat_data.pop("state")

    return ConversationHandler.END