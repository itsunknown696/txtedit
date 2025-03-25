import os
from telegram import Update
from telegram.ext import (
    Updater, CommandHandler, MessageHandler,
    Filters, CallbackContext, ConversationHandler
)
from delete import log_original_file, delete_lines

# Conversation states
ASK_FILE, ASK_START_LINE, ASK_END_LINE = range(3)

TOKEN = "7782085620:AAG_ktDIMiH2DWIr0kO5DaeD8UjuTWOwN1U"
LOG_CHANNEL_ID = -1002669209072  # Replace with your channel ID

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "*ʜɪɪ ᴛʜᴇʀᴇ , ᴛʜɪs ɪs ᴛxᴛ ғɪʟᴇ ᴇᴅɪᴛᴏʀ ʙᴏᴛ , ᴛʜɪs ʙᴏᴛ ʜᴇʟᴘ ʏᴏᴜ ᴛᴏ ᴇᴅɪᴛ ʏᴏᴜʀ ᴛxᴛ ғɪʟᴇ\n\nɪᴛ ᴄᴏɴᴛᴀɪɴs ʙᴇʟᴏᴡ ғᴇᴀᴛᴜʀᴇs ʟɪᴋᴇ\n\n» ᴅᴇʟᴇᴛɪɴɢ ʟɪɴᴇs\n\n» ᴀᴅᴅɪɴɢ ᴛᴇxᴛ\n\nᴍᴀɴᴀɢᴇᴅ ʙʏ @ItsNomis***",
        parse_mode='Markdown'
    )
    return ConversationHandler.END

def del_command(update: Update, context: CallbackContext):
    update.message.reply_text(
        "📤 *ᴘʟᴇᴀsᴇ sᴇɴᴅ ʏᴏᴜʀ ᴛxᴛ ғɪʟᴇ ɪɴ ᴡʜɪᴄʜ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴅᴇʟᴇᴛᴇ ʟɪɴᴇs:\n\nᴍᴀɴᴀɢᴇᴅ ʙʏ @ItsNomis*",
        parse_mode='Markdown'
    )
    return ASK_FILE

def handle_file(update: Update, context: CallbackContext):
    if not update.message.document or not update.message.document.file_name.endswith('.txt'):
        update.message.reply_text(
            "❌ *ɪɴᴠᴀʟɪᴅ ғɪʟᴇ*\n\n"
            "*ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴀ ᴠᴀʟɪᴅ ᴛxᴛ ғɪʟᴇ*",
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    
    # Save file
    file = update.message.document
    context.user_data['file_path'] = f"temp/{file.file_name}"
    file.get_file().download(context.user_data['file_path'])
    
    update.message.reply_text(
        "🔢 *ᴇɴᴛᴇʀ ᴛʜᴇ ɪɴɪᴛɪᴀʟ ɴᴜᴍʙᴇʀ ʟɪɴᴇ ғʀᴏᴍ ᴡʜᴇʀᴇ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴅᴇᴋᴇᴛᴇ:*\n\n",
        parse_mode='Markdown'
    )
    return ASK_START_LINE

def ask_end_line(update: Update, context: CallbackContext):
    try:
        context.user_data['start_line'] = int(update.message.text)
        update.message.reply_text(
            "↔️ *ᴇɴᴛᴇʀ ᴛʜᴇ ғɪɴᴀʟ ɴᴜᴍʙᴇʀ ʟɪɴᴇ ᴛᴏ ᴡʜᴇʀᴇ ʏᴏᴜ ʜᴀᴠᴇ ᴛᴏ ᴅᴇʟᴇᴛᴇ:*\n\n"
            ,
            parse_mode='Markdown'
        )
        return ASK_END_LINE
    except ValueError:
        update.message.reply_text(
            "❌ *ɪɴᴠᴀʟɪᴅ ɪɴᴜᴛ*\n\n"
            "*ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ᴛʜᴇ ᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ*",
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
                f"❌ *ᴇʀʀᴏʀ*\n\n{error}",
                parse_mode='Markdown'
            )
            return ConversationHandler.END
        
        # Send result
        update.message.reply_document(
            document=open(output_file, "rb"),
            caption=f"*✅ sᴜᴄᴄᴇssғᴜʟʏ ᴅᴇʟᴇᴛᴇᴅ ʟɪɴᴇs *{start_line}-{end_line}*",
            parse_mode='Markdown'
        )
            
    except Exception as e:
        update.message.reply_text(
            f"❌ *ᴇʀʀᴏʀ 404 , ᴛʀʏ ᴀɢᴀɪɴ*\n\n{str(e)}",
            parse_mode='Markdown'
        )
    
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext):
    update.message.reply_text(
        "🚫 *ᴏᴘᴇʀᴀᴛɪᴏɴ ᴄᴏɴᴄᴇʟʟᴇᴅ*\n\n"
        "*ɴᴏ ᴄʜᴀɴɢᴇ ᴡᴇʀᴇ ᴍᴀᴅᴇ ɪɴᴛᴏ ʏᴏᴜʀ ᴛxᴛ ғɪʟᴇ*",
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
