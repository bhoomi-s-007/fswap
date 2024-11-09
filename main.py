import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler

# Bot token and API credentials
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
API_URL = "https://api.clothoff.com/face_swap"
API_HEADERS = {"Authorization": "Bearer YOUR_API_TOKEN"}

# Initialize user credits
user_credits = {}

# Log group ID and admin ID for private refilling and logging
LOG_GROUP_ID = -1001234567890
ADMIN_ID = 123456789

# Start function to show credits and user ID
def start(update, context):
    user_id = update.effective_user.id
    user_credits.setdefault(user_id, 0)
    update.message.reply_text(
        "Welcome! Your Telegram ID is {}. You have {} credits.".format(user_id, user_credits[user_id])
    )

# Refill credits (admin-only command)
def refill(update, context):
    if update.effective_user.id != ADMIN_ID:
        update.message.reply_text("Only the 
