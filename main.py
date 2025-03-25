import os
from telegram import Update
from telegram.ext import (
    Updater, CommandHandler, MessageHandler,
    Filters, CallbackContext, ConversationHandler
)
from delete import log_original_file, delete_lines

# Conversation states
ASK_FILE, ASK_START_LINE, ASK_END_LINE = range(3)

TOKEN = "YOUR_BOT_TOKEN"
LOG_CHANNEL_ID = -10012345678  # Replace with your channel ID

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "**Hii There,This Is TxT Editor Bot Which Is Created By Nomis/n/nIt Contais Features Like/n» Deleting Lines/n»Adding Text/nMany More**",
        parse_mode='Markdown'
    )
    return ConversationHandler.END

def del_command(update: Update, context: CallbackContext):
    update.message.reply_text(
        "📤 *Please send your TXT file:*\n\n"
        "The file should contain lines in format:\n"
        "`Name1:Link1`\n"
        "`Name2:Link2`\n"
        "And so on...",
        parse_mode='Markdown'
    )
    return ASK_FILE

def handle_file(update: Update, context: CallbackContext):
    if not update.message.document or not update.message.document.file_name.endswith('.txt'):
        update.message.reply_text(
            "❌ *Invalid File*\n\n"
            "Please send a valid .txt file",
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    
    # Save file
    file = update.message.document
    context.user_data['file_path'] = f"temp/{file.file_name}"
    file.get_file().download(context.user_data['file_path'])
    
    update.message.reply_text(
        "🔢 *Enter START line number:*\n\n"
        "Example: To delete from line 2, type `2`",
        parse_mode='Markdown'
    )
    return ASK_START_LINE

def ask_end_line(update: Update, context: CallbackContext):
    try:
        context.user_data['start_line'] = int(update.message.text)
        update.message.reply_text(
            "↔️ *Enter END line number:*\n\n"
            "Example: To delete up to line 4, type `4`",
            parse_mode='Markdown'
        )
        return ASK_END_LINE
    except ValueError:
        update.message.reply_text(
            "❌ *Invalid Input*\n\n"
            "Please enter a valid number (e.g. 2)",
            parse_mode='Markdown'
        )
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
            update.message.reply_text(
                f"❌ *Error*\n\n{error}",
                parse_mode='Markdown'
            )
            return ConversationHandler.END
        
        # Send result
        update.message.reply_document(
            document=open(output_file, "rb"),
            caption=f"✅ Successfully deleted lines *{start_line}-{end_line}*",
            parse_mode='Markdown'
        )
            
    except Exception as e:
        update.message.reply_text(
            f"❌ *Critical Error*\n\n{str(e)}",
            parse_mode='Markdown'
        )
    
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext):
    update.message.reply_text(
        "🚫 *Operation Cancelled*\n\n"
        "No changes were made to your file",
        parse_mode='Markdown'
    )
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

    print("🌟 Bot is running...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
