from bs4 import BeautifulSoup
import os
import argparse
from bs4 import BeautifulSoup
import os
import argparse

def filter_function(tag):
    return (tag not in ['', "from", "person", "book", "event", "author", "authors", "paper", "podcast", "web"])

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('input_dir', help='Path to the input directory')
args = parser.parse_args()

# Read local HTML file.

# Find the HTML file in the input directory
html_files = [file for file in os.listdir(args.input_dir) if file.endswith('.html')]
if len(html_files) == 0:
    print("No HTML files found in the input directory.")
    exit()

# Assuming there is only one HTML file, select the first one
input_file = os.path.join(args.input_dir, html_files[0])
with open(input_file, 'r', encoding='utf-8') as f:
    html_content = f.read()

soup = BeautifulSoup(html_content, 'html.parser')

# Find all divs that meet the criteria.
memos = soup.find_all('div', {'class': 'memo'})

# Create a directory to save Markdown files.
os.makedirs('markdown_files', exist_ok=True)


for memo in memos:
    # Get the time and format it as a date.
    time_div = memo.find('div', {'class': 'time'})
    date_str = time_div.text

    # Get content
    content_div = memo.find('div', {'class': 'content'})
    content = content_div.text if content_div else ''
    # Convert HTML content to plain text
    text_content = ''
    paragraphs = content_div.find_all('p')
    for paragraph in paragraphs:
        text_content += paragraph.text + '\n'
    

    # Find tags in the content.
    tags = [word[1:].split("/") for word in text_content.split() if word.startswith('#')]
    # Remove tags from the content.
    for tag in tags:
        text_content = text_content.replace("#" + "/".join(tag), '')

    # Remove leading and trailing whitespaces.
    text_content = text_content.strip()
    # Flatten the tags into a 1-dimensional list.
    tags_flat = [tag for sublist in tags for tag in sublist]

    # Convert the list to a set to remove duplicates.
    tags_set = set(tags_flat)
    # filter out empty strings
    tags_set = set(filter(filter_function, tags_set))
    # remove any # in tags_set
    tags_set = {tag.replace("#", '') for tag in tags_set}
    tags_set = {tag.replace("_", ' ') for tag in tags_set}
    tags_set = {tag.replace("Vision-Pro", 'Vision Pro') for tag in tags_set}
    for tag in tags_set:
        if tag.count(',') or tag.count('，')> 0:
            tags_set.remove(tag)
            tags_set.add("[[" + tag + "]]")
    tags_set.add("flomo")
    tags_set.add("card")

    # Get header
    header_date_list = date_str.split(' ')[0].split("-")
    header_date = f"[[{header_date_list[1]}/{header_date_list[2]}/{header_date_list[0]}]]"
    header = f"date:: {header_date}\ntags:: {', '.join(tags_set)}\n"

    # Get file
    files_div = memo.find('div', {'class': 'files'})
    files_content = ''
    if files_div:
        img_tags = files_div.find_all('img')
        for img in img_tags:
            src = img.get('src', '')
            files_content += f'![image.png](../../assets/flomo/{src.replace("file/", "")})\n'
    
    if files_content is not "":
        header += "with_images:: true\n"
    else:
        header += "with_images:: false\n"

    # Merge content and files.
    full_content = header + "\n" + text_content + '\n' + files_content

    # Create a Markdown file and write content into it.
    with open(f'markdown_files/{date_str.replace(":", "%3A")}.md', 'w', encoding='utf-8') as f:
        f.write(full_content)

print("Markdown files have been created.")
