import os

def delete_json_files(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            file_path = os.path.join(directory, filename)
            os.remove(file_path)

# Example usage
directory = r"C:\Capstone\data\er"
delete_json_files(directory)