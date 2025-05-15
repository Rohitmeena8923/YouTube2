
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from utils.youtube import search_youtube, get_streams, download_stream, download_audio
from config import TELEGRAM_BOT_TOKEN

logging.basicConfig(level=logging.INFO)
user_sessions = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome!\nUse /search <query> to search videos.\nUse /get <YouTube URL> to download.")

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = ' '.join(context.args)
    if not query:
        return await update.message.reply_text("Please provide a search term.")
    results = search_youtube(query)
    keyboard = [[InlineKeyboardButton(res['title'], callback_data=f"get|{res['url']}")] for res in results]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Top 20 YouTube search results:", reply_markup=reply_markup)

async def get(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = ' '.join(context.args)
    if not url:
        return await update.message.reply_text("Please provide a YouTube URL.")
    await send_quality_buttons(update, url)

async def send_quality_buttons(update_or_query, url):
    user_id = update_or_query.effective_chat.id
    user_sessions[user_id] = url
    streams = get_streams(url)
    buttons = [[InlineKeyboardButton(f"{s['res']}", callback_data=f"video|{s['itag']}")] for s in streams]
    buttons.append([InlineKeyboardButton("Download Audio", callback_data="audio")])
    markup = InlineKeyboardMarkup(buttons)
    if hasattr(update_or_query, 'message'):
        await update_or_query.message.reply_text("Choose quality or audio:", reply_markup=markup)
    else:
        await update_or_query.edit_message_text("Choose quality or audio:", reply_markup=markup)

async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.message.chat.id
    url = user_sessions.get(user_id)

    if not url and data.startswith("get|"):
        _, url = data.split("|", 1)
        await send_quality_buttons(query, url)
        return

    if data == "audio":
        file_path = download_audio(url)
        if file_path:
            with open(file_path, 'rb') as f:
                await query.message.reply_audio(audio=f)
            os.remove(file_path)
    elif data.startswith("video|"):
        itag = data.split("|")[1]
        file_path = download_stream(url, itag)
        if file_path:
            with open(file_path, 'rb') as f:
                await query.message.reply_video(video=f)
            os.remove(file_path)
        else:
            await query.message.reply_text("Failed to download video.")