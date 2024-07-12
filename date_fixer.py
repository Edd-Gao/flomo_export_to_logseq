import os
import re

def fix_dates(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                with open(file_path, "r") as f:
                    content = f.read()
                updated_content = re.sub(r"\[\[(\d{2})/(\d{2})/(\d{4})\]\]", r"[[\3/\1/\2]]", content)
                with open(file_path, "w") as f:
                    f.write(updated_content)

# Usage example
directory = "/path"
fix_dates(directory)