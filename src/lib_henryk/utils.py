"""
general utilities
"""

def get_file_name_without_extension( file_path: str ):
    file_name = file_path.split("/")[-1] # take last path segment
    file_name_without_extension = ".".join(file_name.split(".")[:-1]) # take everything before ext
    return file_name_without_extension

def get_truncated_string(text:str, max_length=50):
    if len(text) > max_length:
        text = text[0:max_length] + "..." 
    return text

# EOF