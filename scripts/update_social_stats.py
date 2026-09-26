#!/usr/bin/env python3
import os
import re
import urllib.request
import json

def format_count(count_num):
    if count_num >= 1_000_000:
        return f"{count_num / 1_000_000:.2f}".rstrip('0').rstrip('.') + "M"
    if count_num >= 10_000:
        return f"{count_num / 1_000:.1f}".rstrip('0').rstrip('.') + "K"
    if count_num >= 1_000:
        return f"{count_num / 1_000:.2f}".rstrip('0').rstrip('.') + "K"
    return str(count_num)

def get_youtube_subs():
    # 1. Try YouTube Data API if key exists in env
    api_key = os.environ.get("YOUTUBE_API_KEY")
    channel_id = "UC9a6twL0Sz8YFf992vfzKLQ"
    if api_key:
        try:
            url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={channel_id}&key={api_key}"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                sub_count = int(data["items"][0]["statistics"]["subscriberCount"])
                return format_count(sub_count)
        except Exception as e:
            print(f"YouTube API failed: {e}")

    # 2. Scraping fallback
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9'
        }
        url = "https://www.youtube.com/@macstudyroom"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            matches = re.findall(r'(\d+[\d\.,]*[KkMmBb]?)\s*subscribers', html)
            if matches:
                return matches[0].upper()
    except Exception as e:
        print(f"YouTube scrape failed: {e}")

    return None

def get_tiktok_followers():
    # 1. Public counter API
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request("https://countik.com/api/exist/mac_knight141", headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if "followerCount" in data:
                return format_count(int(data["followerCount"]))
    except Exception as e:
        print(f"TikTok countik failed: {e}")

    return None

def update_readme():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    readme_path = os.path.join(script_dir, "..", "README.md")

    if not os.path.exists(readme_path):
        print(f"README not found at {readme_path}")
        return

    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    yt_subs = get_youtube_subs()
    tiktok_followers = get_tiktok_followers()

    print(f"YouTube Subscribers: {yt_subs}")
    print(f"TikTok Followers: {tiktok_followers}")

    updated = content

    if yt_subs:
        # Match any YouTube Sub Count badge in README
        updated = re.sub(
            r'img\.shields\.io/badge/YouTube%20Sub%20Count-[^-\s]+-FF0000',
            f'img.shields.io/badge/YouTube%20Sub%20Count-{yt_subs}-FF0000',
            updated
        )

    if tiktok_followers:
        # Match any TikTok Followers badge in README
        updated = re.sub(
            r'img\.shields\.io/badge/TikTok%20Followers-[^-\s]+-000000',
            f'img.shields.io/badge/TikTok%20Followers-{tiktok_followers}-000000',
            updated
        )

    if updated != content:
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(updated)
        print("README.md successfully updated!")
    else:
        print("No changes needed in README.md")

if __name__ == "__main__":
    update_readme()
