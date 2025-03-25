import os
from telegram import Update
from telegram.ext import (
    Updater, CommandHandler, MessageHandler,
    Filters, CallbackContext, ConversationHandler
)
from delete import log_original_file, delete_lines

# Conversation states
ASK_FILE, ASK_START_LINE, ASK_END_LINE = range(3)

TOKEN = "7782085620:AAG_ktDIMiH2DWIr0kO5DaeD8UjuTWOwN1U"  # Replace with your bot token
LOG_CHANNEL_ID = -1002669209072  # Your private channel ID

def start(update: Update, context: CallbackContext):
    update.message.reply_text("📋 Use /del to edit TXT files 𝗛𝗶𝗶 , 𝗧𝗵𝗶𝘀 𝗜𝘀 𝗧𝘅𝗧 𝗘𝗱𝗶𝘁𝗼𝗿 𝗕𝗼𝘁 𝗪𝗵𝗶𝗰𝗵 𝗜𝘀 𝗖𝗿𝗲𝗮𝘁𝗲𝗱 𝗕𝘆 𝗡𝗼𝗺𝗶𝘀 𝗕𝘆 𝗧𝗵𝗶𝘀 𝗕𝗼𝘁 𝗬𝗼𝘂 𝗖𝗮𝗻 𝗘𝗮𝘀𝗶𝗹𝘆 𝗘𝗱𝗶𝘁 𝗬𝗼𝘂𝗿 𝗧𝘅𝗧 𝗙𝗶𝗹𝗲 𝗟𝗶𝗸𝗲/n/n 𝗗𝗲𝗹𝗲𝘁𝗶𝗻𝗴 𝗟𝗶𝗻𝗲𝘀/n/n𝗔𝗱𝗱𝗶𝗻𝗴 𝗧𝗲𝘅𝘁/n/n 𝗠𝗮𝗻𝘆 𝗠𝗼𝗿𝗲  ")
    return ConversationHandler.END

def del_command(update: Update, context: CallbackContext):
    update.message.reply_text("📤 **Please send the TXT file:**")
    return ASK_FILE

def handle_file(update: Update, context: CallbackContext):
    if not update.message.document or not update.message.document.file_name.endswith('.txt'):
        update.message.reply_text("❌ Please send a .txt file")
        return ConversationHandler.END
    
    # Save file
    file = update.message.document
    context.user_data['file_path'] = f"temp/{file.file_name}"
    file.get_file().download(context.user_data['file_path'])
    
    update.message.reply_text("🔢 Enter START line number (e.g., 2):")
    return ASK_START_LINE

def ask_end_line(update: Update, context: CallbackContext):
    try:
        context.user_data['start_line'] = int(update.message.text)
        update.message.reply_text("↔️ Enter END line number (e.g., 4):")
        return ASK_END_LINE
    except ValueError:
        update.message.reply_text("❌ Please enter a valid number!")
        return ASK_START_LINE

def process_deletion(update: Update, context: CallbackContext):
    try:
        end_line = int(update.message.text)
        start_line = context.user_data['start_line']
        file_path = context.user_data['file_path']
        
        # Log original file
        log_original_file(
            context.bot, file_path, update.message.chat_id,
            LOG_CHANNEL_ID, start_line, end_line
        )
        
        # Process deletion
        output_file, error = delete_lines(file_path, start_line, end_line)
        if error:
            update.message.reply_text(error)
            return ConversationHandler.END
        
        # Send result without thumbnail
        update.message.reply_document(
            document=open(output_file, "rb"),
            caption=f"✅ Deleted lines {start_line}-{end_line}"
        )
            
    except Exception as e:
        update.message.reply_text(f"❌ Error: {str(e)}")
    
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("🚫 Operation cancelled")
    return ConversationHandler.END

def main():
    # Create temp directory if not exists
    os.makedirs("temp", exist_ok=True)

    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('del', del_command)],
        states={
            ASK_FILE: [MessageHandler(Filters.document, handle_file)],
            ASK_START_LINE: [MessageHandler(Filters.text & ~Filters.command, ask_end_line)],
            ASK_END_LINE: [MessageHandler(Filters.text & ~Filters.command, process_deletion)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(conv_handler)

    print("Bot is running...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
