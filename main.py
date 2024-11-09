import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Bot token and API credentials
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
API_URL = "https://api.clothoff.com/face_swap"  # Replace with the correct endpoint
API_HEADERS = {"Authorization": "Bearer YOUR_API_TOKEN"}

# Initialize user credits (using a dictionary for simplicity)
user_credits = {}

# Log group ID and admin ID for private refilling and logging
LOG_GROUP_ID = -1001234567890  # Replace with your log group ID
ADMIN_ID = 123456789  # Replace with your Telegram ID

# Start function to show credits and user ID
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_credits.setdefault(user_id, 0)  # Initialize with 0 credits if not set
    await update.message.reply_text(
        f"Welcome! Your Telegram ID is {user_id}. You have {user_credits[user_id]} credits."
    )

# Refill credits (admin-only command)
async def refill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Only the admin can add credits.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("Usage: /refill <user_id> <amount>")
        return

    try:
        user_id = int(context.args[0])
        amount = int(context.args[1])
        user_credits[user_id] = user_credits.get(user_id, 0) + amount
        await update.message.reply_text(f"Added {amount} credits to user {user_id}.")

        # Log the refill event
        await context.bot.send_message(
            chat_id=LOG_GROUP_ID,
            text=f"Admin added {amount} credits to user {user_id}. New balance: {user_credits[user_id]}"
        )
    except ValueError:
        await update.message.reply_text("Please provide a valid user_id and amount.")

# Function for face swap image requests
async def faceswap_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_credits.get(user_id, 0) < 1:
        await update.message.reply_text("Insufficient credits. Contact admin to refill.")
        return

    if not update.message.photo:
        await update.message.reply_text("Please send a photo with this command.")
        return

    # Download user's photo
    photo_file = await context.bot.get_file(update.message.photo[-1].file_id)
    photo_path = "user_photo.jpg"
    await photo_file.download(photo_path)

    # Send request to FaceSwap API
    files = {"image": open(photo_path, "rb")}
    response = requests.post(API_URL, headers=API_HEADERS, files=files)

    if response.status_code == 200:
        user_credits[user_id] -= 1
        with open("faceswap_result.jpg", "wb") as f:
            f.write(response.content)
        await update.message.reply_photo(photo=open("faceswap_result.jpg", "rb"))

        # Log transaction
        await context.bot.send_message(
            chat_id=LOG_GROUP_ID,
            text=f"User {user_id} requested an image face swap. Remaining credits: {user_credits[user_id]}"
        )
    else:
        await update.message.reply_text("Face swap failed. Please try again later.")

# Function for face swap video requests
async def faceswap_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_credits.get(user_id, 0) < 2:
        await update.message.reply_text("Insufficient credits. Contact admin to refill.")
        return

    if not update.message.video:
        await update.message.reply_text("Please send a video with this command.")
        return

    # Download user's video
    video_file = await context.bot.get_file(update.message.video.file_id)
    video_path = "user_video.mp4"
    await video_file.download(video_path)

    # Send request to FaceSwap API
    files = {"video": open(video_path, "rb")}
    response = requests.post(API_URL, headers=API_HEADERS, files=files)

    if response.status_code == 200:
        user_credits[user_id] -= 2
        with open("faceswap_result.mp4", "wb") as f:
            f.write(response.content)
        await update.message.reply_video(video=open("faceswap_result.mp4", "rb"))

        # Log transaction
        await context.bot.send_message(
            chat_id=LOG_GROUP_ID,
            text=f"User {user_id} requested a video face swap. Remaining credits: {user_credits[user_id]}"
        )
    else:
        await update.message.reply_text("Face swap failed. Please try again later.")

# Main function to start the bot
if __name__ == "__main__":
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("refill", refill))
    application.add_handler(CommandHandler("faceswap_image", faceswap_image))
    application.add_handler(CommandHandler("faceswap_video", faceswap_video))

    print("Bot is running...")
    application.run_polling()
