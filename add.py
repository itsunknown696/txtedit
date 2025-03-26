import os

def add_text_to_file(file_path, start_line, end_line, text_to_add, position):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        # Validate line numbers
        if start_line < 1 or end_line > len(lines):
            return None, "❌ Invalid line numbers. Check file length."
        
        # Prepare the text to add with newline if needed
        text_to_add = text_to_add + '\n' if not text_to_add.endswith('\n') else text_to_add
        
        # Process based on position
        if position == '/bn':  # Before name
            updated_lines = []
            for i, line in enumerate(lines, 1):
                if start_line <= i <= end_line:
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        updated_lines.append(f"{text_to_add}{parts[0]}:{parts[1]}")
                    else:
                        updated_lines.append(f"{text_to_add}{line}")
                else:
                    updated_lines.append(line)
        
        elif position == '/an':  # After name
            updated_lines = []
            for i, line in enumerate(lines, 1):
                if start_line <= i <= end_line:
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        updated_lines.append(f"{parts[0]}{text_to_add}:{parts[1]}")
                    else:
                        updated_lines.append(f"{line}{text_to_add}")
                else:
                    updated_lines.append(line)
        
        else:
            return None, "❌ Invalid position command. Use /bn or /an."
        
        # Save updated file
        output_file = os.path.join("temp", "updated_" + os.path.basename(file_path))
        with open(output_file, 'w') as file:
            file.writelines(updated_lines)
        
        return output_file, None
    
    except Exception as e:
        return None, f"❌ Error: {str(e)}"
