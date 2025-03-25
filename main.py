import os
from telegram import Update, InputMediaDocument
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from delete import delete_lines

TOKEN = "7782085620:AAG_ktDIMiH2DWIr0kO5DaeD8UjuTWOwN1U"  # Replace with your bot token
LOG_CHANNEL_ID = -1002669209072  # Your private channel ID

# Ensure temp directory exists
os.makedirs("temp", exist_ok=True)

def start(update: Update, context: CallbackContext):
    update.message.reply_text("📋 Send me a TXT file first, then use /del to delete lines.")

def handle_file(update: Update, context: CallbackContext):
    if not update.message.document.file_name.endswith('.txt'):
        update.message.reply_text("❌ Only .txt files accepted!")
        return
    
    # Save the file
    file = update.message.document
    context.user_data['file_path'] = f"temp/{file.file_name}"
    file.get_file().download(context.user_data['file_path'])
    
    update.message.reply_text("✅ File saved! Use /del to delete lines.")

def ask_start_line(update: Update, context: CallbackContext):
    if 'file_path' not in context.user_data:
        update.message.reply_text("⚠️ Send a TXT file first!")
        return
    
    update.message.reply_text("Enter START line number (e.g., 2):")
    return "ASK_END_LINE"

def ask_end_line(update: Update, context: CallbackContext):
    try:
        context.user_data['start_line'] = int(update.message.text)
        update.message.reply_text("Enter END line number (e.g., 4):")
        return "DELETE_LINES"
    except ValueError:
        update.message.reply_text("❌ Please enter a valid number!")

def delete_lines_range(update: Update, context: CallbackContext):
    try:
        end_line = int(update.message.text)
        start_line = context.user_data['start_line']
        file_path = context.user_data['file_path']

        # Process deletion and log
        output_file, error = delete_lines(
            file_path, start_line, end_line,
            context.bot, update.message.chat_id, LOG_CHANNEL_ID
        )

        if error:
            update.message.reply_text(error)
            return

        # Send updated file with thumbnail
        with open("nKr.jpg", "rb") as thumb:
            update.message.reply_document(
                document=open(output_file, "rb"),
                thumb=thumb,
                caption=f"✅ Deleted lines {start_line}-{end_line}"
            )

    except Exception as e:
        update.message.reply_text(f"❌ Critical error: {str(e)}")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.document, handle_file))
    dp.add_handler(CommandHandler("del", ask_start_line))
    
    # Conversation handlers
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, ask_end_line))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, delete_lines_range))

    print("Bot is running...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
