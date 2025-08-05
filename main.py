import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import yt_dlp

# Load token from environment variable
BOT_TOKEN = os.getenv("BOT_TOKEN")

# In-memory usage tracker (replace with database like Supabase later)
user_usage = {}

MAX_FREE_DOWNLOADS = 3

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎵 Send /download <YouTube URL> to get your music.\nYou get 3 free downloads!")

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    if user_id not in user_usage:
        user_usage[user_id] = 0

    if user_usage[user_id] >= MAX_FREE_DOWNLOADS:
        await update.message.reply_text("⚠️ You've used all 3 free downloads.\nPay ₹XX to unlock unlimited usage.")
        return

    if len(context.args) == 0:
        await update.message.reply_text("❌ Please provide a YouTube link.\nExample: /download https://youtube.com/...")
        return

    url = context.args[0]
    await update.message.reply_text("⏬ Downloading your music, please wait...")

    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'downloads/{user_id}.mp3',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        with open(f'downloads/{user_id}.mp3', 'rb') as audio_file:
            await update.message.reply_audio(audio=audio_file, title="Downloaded Track")

        os.remove(f'downloads/{user_id}.mp3')
        user_usage[user_id] += 1

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("download", download))

    print("Bot is running...")
    app.run_polling()
