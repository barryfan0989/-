from bs4 import BeautifulSoup
import re

file_path = "C:/Users/USER/Desktop/專題/專題/.gemini/antigravity-ide/brain/d148131d-0ddc-483c-aa74-8f2028fd9fe6/scratch/ibon_page.html"
with open(file_path, "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
# Find the element that contains "博麗"
target = None
for el in soup.find_all(string=re.compile("博麗")):
    target = el
    break

if target:
    print("Found target string!")
    # Find the first parent that has attributes or classes
    parent = target.parent
    for _ in range(5):
        if parent:
            print(f"Parent tag: <{parent.name} class='{parent.get('class')}' attrs={parent.attrs}>")
            parent = parent.parent
else:
    print("Target string not found!")

