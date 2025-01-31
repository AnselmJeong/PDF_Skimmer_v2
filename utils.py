import re

def paragraph_to_markdown_list(paragraph):
    # Split the paragraph into sentences using regex
    sentences = re.split(r'(?<=[.!?]) +', paragraph)
    
    # Convert each sentence into a Markdown list item
    markdown_list = "\n".join(f"* {sentence}" for sentence in sentences)
    
    return markdown_list