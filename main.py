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
        update.message.reply_text("Only the admin can add credits.")
        return

    if len(context.args) < 2:
        update.message.reply_text("Usage: /refill <user_id> <amount>")
        return

    try:
        user_id = int(context.args[0])
        amount = int(context.args[1])
        user_credits[user_id] = user_credits.get(user_id, 0) + amount
        update.message.reply_text("Added {} credits to user {}.".format(amount, user_id))
        context.bot.send_message(
            chat_id=LOG_GROUP_ID,
            text="Admin added {} credits to user {}. New balance: {}".format(amount, user_id, user_credits[user_id])
        )
    except ValueError:
        update.message.reply_text("Please provide a valid user_id and amount.")

# Function for face swap image requests
def faceswap_image(update, context):
    user_id = update.effective_user.id
    if user_credits.get(user_id, 0) < 1:
        update.message.reply_text("Insufficient credits. Contact admin to refill.")
        return

    if not update.message.photo:
        update.message.reply_text("Please send a photo with this command.")
        return

    # Download user's photo
    photo_file = context.bot.get_file(update.message.photo[-1].file_id)
    photo_path = "user_photo.jpg"
    photo_file.download(photo_path)

    # Send request to FaceSwap API
    files = {"image": open(photo_path, "rb")}
    response = requests.post(API_URL, headers=API_HEADERS, files=files)

    if response.status_code == 200:
        user_credits[user_id] -= 1
        with open("faceswap_result.jpg", "wb") as f:
            f.write(response.content)
        update.message.reply_photo(photo=open("faceswap_result.jpg", "rb"))
        context.bot.send_message(
            chat_id=LOG_GROUP_ID,
            text="User {} requested an image face swap. Remaining credits: {}".format(user_id, user_credits[user_id])
        )
    else:
        update.message.reply_text("Face swap failed. Please try again later.")

# Function for face swap video requests
def faceswap_video(update, context):
    user_id = update.effective_user.id
    if user_credits.get(user_id, 0) < 2:
        update.message.reply_text("Insufficient credits. Contact admin to refill.")
        return

    if not update.message.video:
        update.message.reply_text("Please send a video with this command.")
        return

    # Download user's video
    video_file = context.bot.get_file(update.message.video.file_id)
    video_path = "user_video.mp4"
    video_file.download(video_path)

    # Send request to FaceSwap API
    files = {"video": open(video_path, "rb")}
    response = requests.post(API_URL, headers=API_HEADERS, files=files)

    if response.status_code == 200:
        user_credits[user_id] -= 2
        with open("faceswap_result.mp4", "wb") as f:
            f.write(response.content)
        update.message.reply_video(video=open("faceswap_result.mp4", "rb"))
        context.bot.send_message(
            chat_id=LOG_GROUP_ID,
            text="User {} requested a video face swap. Remaining credits: {}".format(user_id, user_credits[user_id])
        )
    else:
        update.message.reply_text("Face swap failed. Please try again later.")

# Main function to start the bot
if __name__ == "__main__":
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("refill", refill))
    application.add_handler(CommandHandler("faceswap_image", faceswap_image))
    application.add_handler(CommandHandler("faceswap_video", faceswap_video))

    print("Bot is running...")
    application.run_polling()
