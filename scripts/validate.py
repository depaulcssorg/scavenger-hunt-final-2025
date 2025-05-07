import os
import sys
import re
import hashlib
import json
from bs4 import BeautifulSoup

HASH_FILE = "hashes.json"

def load_html(path="index.html"):
    try:
        with open(path, "r") as f:
            return BeautifulSoup(f, "lxml")
    except FileNotFoundError:
        print("❌ index.html not found.")
        sys.exit(1)

def load_hash(key):
    try:
        with open(HASH_FILE, "r") as f:
            data = json.load(f)
        return data[key]
    except FileNotFoundError:
        print(f"❌ Hash file '{HASH_FILE}' not found.")
    except KeyError:
        print(f"❌ Key '{key}' not found in hash file.")
    sys.exit(1)

def sha256(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()

def check_target_branch():
    expected_hash = load_hash("TARGET_BRANCH")
    event_path = os.environ.get("GITHUB_EVENT_PATH")

    try:
        with open(event_path, "r") as f:
            event = json.load(f)
            actual_branch = event.get("pull_request", {}).get("base", {}).get("ref")
    except Exception as e:
        print(f"❌ Failed to read GitHub event data: {e}")
        sys.exit(1)

    if sha256(actual_branch) == expected_hash:
        print("✅ PR targets the correct branch.")
    else:
        print(f"❌ PR targets the wrong branch: {actual_branch}")
        sys.exit(1)

def check_background_color():
    soup = load_html()
    expected_hash = load_hash("BACKGROUND_COLOR")
    style_tags = soup.find_all("style")

    for style in style_tags:
        match = re.search(r'background(?:-color)?:\s*(#[0-9a-fA-F]{6})', style.text)
        if match:
            found = match.group(1)
            if sha256(found.lower()) == expected_hash:
                print("✅ Background color matches.")
                return
            else:
                print(f"❌ Background color does not match. Found: {found}")
                sys.exit(1)
    print("❌ No background color found in <style> tags.")
    sys.exit(1)

def check_header_text():
    soup = load_html()
    expected_hash = load_hash("HEADER_TEXT")

    headers = soup.find_all(re.compile(r'h[1-6]'))
    for header in headers:
        actual_text = header.get_text(strip=True)
        if sha256(actual_text) == expected_hash:
            print("✅ Header text matches.")
            return

    print("❌ Header text not found.")
    sys.exit(1)

def check_header_size():
    soup = load_html()
    expected_hash = load_hash("HEADER_SIZE")
    header_text_hash = load_hash("HEADER_TEXT")

    headers = soup.find_all(re.compile(r'h[1-6]'))
    for header in headers:
        actual_text = header.get_text(strip=True)
        if sha256(actual_text) == header_text_hash:
            actual_size = int(header.name[1])
            if sha256(str(actual_size)) == expected_hash:
                print("✅ Header size matches.")
                return
            else:
                print(f"❌ Header size mismatch. Found: h{actual_size}")
                sys.exit(1)

    print("❌ Header text not found.")
    sys.exit(1)

def find_img_tag_by_name(soup, expected_name):
    return soup.find("img", {"src": expected_name})

def check_image_name():
    soup = load_html()
    expected_name = "container.png"

    img_tag = find_img_tag_by_name(soup, expected_name)
    if img_tag:
        print("✅ Image tag with correct name found.")
    else:
        print(f"❌ No <img> tag with src='{expected_name}' found.")
        sys.exit(1)

def check_image_link():
    soup = load_html()
    expected_name = "container.png"
    expected_hash = load_hash("LINK_URL")

    img_tag = find_img_tag_by_name(soup, expected_name)
    if not img_tag:
        print(f"❌ No <img> tag with src='{expected_name}' found.")
        sys.exit(1)

    parent = img_tag.find_parent("a", href=True)
    if parent and sha256(parent["href"]) == expected_hash:
        print("✅ Image is wrapped in correct link.")
    else:
        found = parent["href"] if parent else "none"
        print(f"❌ Image link mismatch. Found: {found}")
        sys.exit(1)

def check_image_hash():
    expected_name = "container.png"
    expected_hash = load_hash("IMAGE_HASH")

    try:
        with open(expected_name, "rb") as f:
            image_bytes = f.read()
    except FileNotFoundError:
        print(f"❌ Image file '{expected_name}' not found.")
        sys.exit(1)

    actual_hash = hashlib.sha256(image_bytes).hexdigest()
    if actual_hash == expected_hash:
        print("✅ Image SHA-256 hash matches.")
    else:
        print(f"❌ Image content hash does not match.\nExpected: {expected_hash}\nFound:    {actual_hash}")
        sys.exit(1)

def check_pr_message():
    expected_hash = load_hash("SECRET_PHRASE")
    event_path = os.environ.get("GITHUB_EVENT_PATH")

    if not event_path:
        print("❌ GITHUB_EVENT_PATH not set.")
        sys.exit(1)

    try:
        with open(event_path, "r") as f:
            event = json.load(f)
            pr_body = event.get("pull_request", {}).get("body", "")
    except Exception as e:
        print(f"❌ Failed to load PR body: {e}")
        sys.exit(1)

    if sha256(pr_body.strip()) == expected_hash:
        print("✅ PR message contains the correct secret phrase.")
    else:
        print("❌ PR message does not contain the correct secret phrase.")
        sys.exit(1)

def check_lockout():
    print("TODO: Implement winner lockout logic.")
    sys.exit(0)

def main():
    if len(sys.argv) < 2:
        print("❌ Usage: python validate.py <check-name>")
        sys.exit(1)

    match sys.argv[1]:
        case "check-branch":
            check_target_branch()
        case "check-background":
            check_background_color()
        case "check-header-text":
            check_header_text()
        case "check-header-size":
            check_header_size()
        case "check-image-name":
            check_image_name()
        case "check-image-link":
            check_image_link()
        case "check-image-hash":
            check_image_hash()
        case "check-pr-message":
            check_pr_message()
        case "check-lockout":
            check_lockout()
        case _:
            print(f"❌ Unknown check: {sys.argv[1]}")
            sys.exit(1)

if __name__ == "__main__":
    main()
