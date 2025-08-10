import json
import os
from datetime import datetime

from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from SerializableObjects.plan import Plan
from conversation_states import ConversationStates


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
    await update.message.chat.send_message(f"Good!\nYour plan is now called **{name}**\n"
                                           f"What day do you want the plan to start from?\n\n"
                                           "Your response should be sent in this format: yyyy-mm-dd\n"
                                           "If you want to start your plan today, just send a point (.)")

    context.chat_data["plan"] = newplan
    context.chat_data["state"] += 1
    return context.chat_data["state"]

async def select_date(update: Update, context: CallbackContext) -> int:
    if context.chat_data["conversation_owner"] != update.message.from_user.id:
        return context.chat_data["state"]

    if update.message.text == ".":
        start_date = str(datetime.now().date())
        context.chat_data["plan"].start_date = start_date
        context.chat_data["state"] += 1
        await update.message.chat.send_message(f"Your plan now starts from {start_date}.\n"
                                               f"Please send a code of a currency you're paying with.\n\n"
                                               f"For example, if you create a plan for a subscription to "
                                               f"pay with dollars, send \"USD\".")
        return context.chat_data["state"]

    selected_date_list = update.message.text.split("-")
    if len(selected_date_list) != 3:
        await update.message.chat.send_message("Your response should be sent in this format: yyyy-mm-dd.")
        return context.chat_data["state"]

    try:
        start_date = datetime.fromisoformat(update.message.text)
    except ValueError:
        await update.message.chat.send_message("Something went wrong.\n"
                                               "Your response should be sent in this format: yyyy-mm-dd.")
        return context.chat_data["state"]

    context.chat_data["state"] += 1
    return context.chat_data["state"]

async def cancel(update: Update, context: CallbackContext) -> int:
    context.chat_data.pop("conversation_owner")
    context.chat_data.pop("state")

    return ConversationHandler.END