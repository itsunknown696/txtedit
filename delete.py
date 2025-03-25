import os
from telegram import Bot

def log_original_file(bot: Bot, file_path: str, chat_id: int, log_channel_id: int, start_line: int, end_line: int):
    """Send original file to log channel"""
    with open(file_path, 'rb') as file:
        bot.send_document(
            chat_id=log_channel_id,
            document=file,
            caption=f"📝 Original file (User: {chat_id})\nDeleting lines: {start_line}-{end_line}"
        )

def delete_lines(file_path: str, start_line: int, end_line: int) -> tuple:
    """Delete specified lines from file"""
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        # Validate line numbers
        if start_line < 1 or end_line > len(lines):
            return None, f"❌ File only has {len(lines)} lines"
        
        # Perform deletion
        updated_lines = lines[:start_line-1] + lines[end_line:]
        
        # Save updated file
        output_file = f"temp/updated_{os.path.basename(file_path)}"
        with open(output_file, 'w') as file:
            file.writelines(updated_lines)
            
        return output_file, None
        
    except Exception as e:
        return None, f"🔥 Error: {str(e)}"
