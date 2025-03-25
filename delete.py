import os
from telegram import InputMediaDocument

def delete_lines(input_file, start_line, end_line, bot, chat_id, log_channel_id):
    try:
        # 1. Log original file to channel
        with open(input_file, 'rb') as orig_file:
            bot.send_document(
                chat_id=log_channel_id,
                document=orig_file,
                caption=f"🗂️ ORIGINAL FILE\nUser: {chat_id}\nLines to delete: {start_line}-{end_line}"
            )

        # 2. Process deletion
        with open(input_file, 'r') as file:
            lines = file.readlines()
        
        # Validate line numbers
        if start_line < 1 or end_line > len(lines):
            return None, f"❌ File has only {len(lines)} lines!"
        
        # Delete the range
        updated_lines = lines[:start_line-1] + lines[end_line:]
        
        # Save updated file
        output_file = os.path.join("temp", "updated_" + os.path.basename(input_file))
        with open(output_file, 'w') as file:
            file.writelines(updated_lines)
        
        return output_file, None

    except Exception as e:
        return None, f"🔥 Error: {str(e)}"
