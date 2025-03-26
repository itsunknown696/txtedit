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
LOG_CHANNEL_ID = -1002669209072

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "*ʜɪɪ ᴛʜᴇʀᴇ , ᴛʜɪs ɪs ᴛxᴛ ғɪʟᴇ ᴇᴅɪᴛᴏʀ ʙᴏᴛ , ᴛʜɪs ʙᴏᴛ ʜᴇʟᴘ ʏᴏᴜ ᴛᴏ ᴇᴅɪᴛ ʏᴏᴜʀ ᴛxᴛ ғɪʟᴇ\n\nɪᴛ ᴄᴏɴᴛᴀɪɴs ʙᴇʟᴏᴡ ғᴇᴀᴛᴜʀᴇs ʟɪᴋᴇ\n\n» ᴅᴇʟᴇᴛɪɴɢ ʟɪɴᴇs\n\n» ᴀᴅᴅɪɴɢ ᴛᴇxᴛ\n\nᴍᴀɴᴀɢᴇᴅ ʙʏ @ItsNomis*",
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
        "🔢 *ᴇɴᴛᴇʀ ᴛʜᴇ ɪɴɪᴛɪᴀʟ ɴᴜᴍʙᴇʀ ʟɪɴᴇ ғʀᴏᴍ ᴡʜᴇʀᴇ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴅᴇʟᴇᴛᴇ:*",
        parse_mode='Markdown'
    )
    return ASK_START_LINE

def ask_end_line(update: Update, context: CallbackContext):
    try:
        context.user_data['start_line'] = int(update.message.text)
        update.message.reply_text(
            "↔️ *ᴇɴᴛᴇʀ ᴛʜᴇ ғɪɴᴀʟ ɴᴜᴍʙᴇʀ ʟɪɴᴇ ᴛᴏ ᴡʜᴇʀᴇ ʏᴏᴜ ʜᴀᴠᴇ ᴛᴏ ᴅᴇʟᴇᴛᴇ:*",
            parse_mode='Markdown'
        )
        return ASK_END_LINE
    except ValueError:
        update.message.reply_text(
            "❌ *Invalid Input*\n"
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
                f"❌ *Error*\n{error}",
                parse_mode='Markdown'
            )
            return ConversationHandler.END
        
        # Send result
        update.message.reply_document(
            document=open(output_file, "rb"),
            caption=f"✅ sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ʟɪɴᴇs*{start_line}-{end_line}*",
            parse_mode='Markdown'
        )
            
    except Exception as e:
        update.message.reply_text(
            f"❌ *Error*\n{str(e)}",
            parse_mode='Markdown'
        )
    
    return ConversationHandler.END

#add.py


def cancel(update: Update, context: CallbackContext):
    update.message.reply_text(
        "🚫 *Operation Cancelled*\n"
        "No changes were made to your file",
        parse_mode='Markdown'
    )
    return ConversationHandler.END

def add_command(update: Update, context: CallbackContext):
    update.message.reply_text(
        "📤 *Please send the TXT file you want to edit:*",
        parse_mode='Markdown'
    )
    return ASK_ADD_FILE

def handle_add_file(update: Update, context: CallbackContext):
    if not update.message.document or not update.message.document.file_name.endswith('.txt'):
        update.message.reply_text(
            "❌ *Invalid File*\n"
            "Please send a valid .txt file",
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    
    # Save file
    file = update.message.document
    context.user_data['add_file_path'] = f"temp/{file.file_name}"
    file.get_file().download(context.user_data['add_file_path'])
    
    update.message.reply_text(
        "🔢 *Enter the initial line number from where you want to add text:*",
        parse_mode='Markdown'
    )
    return ASK_ADD_START

def ask_add_end(update: Update, context: CallbackContext):
    try:
        context.user_data['add_start_line'] = int(update.message.text)
        update.message.reply_text(
            "↔️ *Enter the final line number to where you have to add text:*",
            parse_mode='Markdown'
        )
        return ASK_ADD_END
    except ValueError:
        update.message.reply_text(
            "❌ *Invalid Input*\n"
            "Please enter a valid number (e.g. 2)",
            parse_mode='Markdown'
        )
        return ASK_ADD_START

def ask_add_text(update: Update, context: CallbackContext):
    try:
        context.user_data['add_end_line'] = int(update.message.text)
        update.message.reply_text(
            "🏷️ *Enter the text that you want to add:*",
            parse_mode='Markdown'
        )
        return ASK_ADD_TEXT
    except ValueError:
        update.message.reply_text(
            "❌ *Invalid Input*\n"
            "Please enter a valid number (e.g. 4)",
            parse_mode='Markdown'
        )
        return ASK_ADD_END

def ask_add_position(update: Update, context: CallbackContext):
    context.user_data['add_text'] = update.message.text
    update.message.reply_text(
        "🏷️ *Where do you want to add?*\n\n"
        "ʙᴇғᴏʀᴇ ɴᴀᴍᴇ ᴛʜᴇɴ sᴇɴᴅ /bn\n"
        "ᴀғᴛᴇʀ ɴᴀᴍᴇ ᴛʜᴇɴ sᴇɴᴅ /an",
        parse_mode='Markdown'
    )
    return ASK_ADD_POSITION

def process_addition(update: Update, context: CallbackContext):
    try:
        position = update.message.text
        if position not in ('/bn', '/an'):
            update.message.reply_text(
                "❌ *Invalid Command*\n"
                "Please use /bn or /an",
                parse_mode='Markdown'
            )
            return ASK_ADD_POSITION
        
        output_file, error = add_text_to_file(
            context.user_data['add_file_path'],
            context.user_data['add_start_line'],
            context.user_data['add_end_line'],
            context.user_data['add_text'],
            position
        )
        
        if error:
            update.message.reply_text(
                f"❌ *Error*\n{error}",
                parse_mode='Markdown'
            )
            return ConversationHandler.END
        
        # Send result
        update.message.reply_document(
            document=open(output_file, "rb"),
            caption="✅ Text added successfully!",
            parse_mode='Markdown'
        )
            
    except Exception as e:
        update.message.reply_text(
            f"❌ *Error*\n{str(e)}",
            parse_mode='Markdown'
        )
    
    return ConversationHandler.END

def main():
    os.makedirs("temp", exist_ok=True)

    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Delete conversation handler
    del_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('del', del_command)],
        states={
            ASK_FILE: [MessageHandler(Filters.document, handle_file)],
            ASK_START_LINE: [MessageHandler(Filters.text & ~Filters.command, ask_end_line)],
            ASK_END_LINE: [MessageHandler(Filters.text & ~Filters.command, process_deletion)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # Add conversation handler
    add_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('add', add_command)],
        states={
            ASK_FILE: [MessageHandler(Filters.document, handle_add_file)],
            ASK_ADD_START: [MessageHandler(Filters.text & ~Filters.command, ask_add_end)],
            ASK_ADD_END: [MessageHandler(Filters.text & ~Filters.command, ask_add_text)],
            ASK_ADD_TEXT: [MessageHandler(Filters.text & ~Filters.command, ask_add_position)],
            ASK_ADD_POSITION: [MessageHandler(Filters.text & ~Filters.command, process_addition)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(del_conv_handler)
    dp.add_handler(add_conv_handler)

    print(" Bot is running...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
