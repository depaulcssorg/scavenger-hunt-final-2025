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

def check_background_color():
    soup = load_html()
    expected_color = os.environ["BACKGROUND_COLOR"]
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

def check_header_text():
    soup = load_html()
    expected_text = os.environ["HEADER_TEXT"]

    headers = soup.find_all(re.compile(r'h[1-6]'))
    for header in headers:
        if header.get_text(strip=True) == expected_text:
            print("✅ Header text matches.")
            return

    print("❌ Header text not found.")
    sys.exit(1)


def check_header_size():
    soup = load_html()
    expected_text = os.environ["HEADER_TEXT"]
    expected_size = int(os.environ["HEADER_SIZE"])

    headers = soup.find_all(re.compile(r'h[1-6]'))
    for header in headers:
        if header.get_text(strip=True) == expected_text:
            actual_size = int(header.name[1])
            if actual_size == expected_size:
                print("✅ Header size matches.")
                return
            else:
                print(f"❌ Header size mismatch. Found: h{actual_size}")
                sys.exit(1)

    print("❌ Header text not found.")
    sys.exit(1)


def check_image_tag():
    print("TODO: Implement image tag validation.")
    sys.exit(0)

def check_pr_message():
    print("TODO: Implement PR message check via GITHUB_EVENT_PATH.")
    sys.exit(0)

def check_lockout():
    print("TODO: Implement winner lockout logic.")
    sys.exit(0)

def main():
    if len(sys.argv) < 2:
        print("❌ Usage: python validate.py <check-name>")
        sys.exit(1)

    match sys.argv[1]:
        case "check-background":
            check_background_color()
        case "check-header-text":
            check_header_text()
        case "check-header-size":
            check_header_size()
        case "check-image":
            check_image_tag()
        case "check-pr-message":
            check_pr_message()
        case "check-lockout":
            check_lockout()
        case _:
            print(f"❌ Unknown check: {sys.argv[1]}")
            sys.exit(1)

if __name__ == "__main__":
    main()
