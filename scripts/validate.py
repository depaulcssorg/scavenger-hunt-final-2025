import os
import sys
import re
from bs4 import BeautifulSoup

def load_html(path="index.html"):
    try:
        with open(path, "r") as f:
            return BeautifulSoup(f, "lxml")
    except FileNotFoundError:
        print("❌ index.html not found.")
        sys.exit(1)

def check_background_color(soup, expected_color):
    style_tags = soup.find_all("style")
    for style in style_tags:
        match = re.search(r'background-color:\s*(#[0-9a-fA-F]{6})', style.text)
        if match:
            found = match.group(1)
            if found.lower() == expected_color.lower():
                print("✅ Background color matches.")
                return
            else:
                print(f"❌ Background color does not match. Found: {found}")
                sys.exit(1)
    print("❌ No background color found in <style> tags.")
    sys.exit(1)

def check_header_text(soup, expected_text):
    headers = soup.find_all(re.compile(r'h[1-6]'))
    for header in headers:
        if header.get_text(strip=True) == expected_text:
            print("✅ Header text matches.")
            return header.name  # e.g., "h2"
    print("❌ Header text not found.")
    sys.exit(1)

def check_header_size(found_tag, expected_size):
    level = int(found_tag[1]) if found_tag.startswith("h") else None
    if level == int(expected_size):
        print("✅ Header size matches.")
    else:
        print(f"❌ Header size mismatch. Found: h{level}")
        sys.exit(1)

def check_image_tag(soup, expected_name, expected_hash, expected_link):
    print("TODO: Implement image tag validation.")

def check_pr_message(expected_phrase):
    print("TODO: Implement PR message check via GITHUB_EVENT_PATH if needed.")

def check_lockout():
    print("TODO: Implement winner lockout logic.")

def main():
    soup = load_html()

    check_background_color(soup, os.environ["BACKGROUND_COLOR"])

    found_tag = check_header_text(soup, os.environ["HEADER_TEXT"])
    check_header_size(found_tag, os.environ["HEADER_SIZE"])

    check_image_tag(
        soup,
        os.environ["IMAGE_NAME"],
        os.environ["IMAGE_HASH"],
        os.environ["LINK_URL"]
    )

    check_pr_message(os.environ["SECRET_PHRASE"])
    check_lockout()

if __name__ == "__main__":
    main()
