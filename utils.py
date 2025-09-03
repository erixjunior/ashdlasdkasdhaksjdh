import os
import json
import csv
from typing import Optional, List, Dict, Any
from datetime import datetime


def read_js_script(script_name: str, script_dir: Optional[str] = None) -> str:
    """
    Helper to read a JS file from the script/ directory.
    :param script_name: Filename of the JS script (e.g., 'scroll_by.js')
    :param script_dir: Optional directory path, defaults to 'script' folder next to this file.
    :return: JS script content as string
    """
    try:
        if script_dir is None:
            script_dir = os.path.join(os.path.dirname(__file__), "script")
        script_path = os.path.join(script_dir, script_name)
        with open(script_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"⚠️ JS script file not found: {script_path}")
        return ""
    except Exception as e:
        print(f"❌ Error reading JS script {script_name}: {e}")
        return ""


def save_to_file(
    posts: List[Dict[str, Any]],
    stats: Dict[str, Any],
    filename: str = "facebook_posts_cdp.json",
    source: str = "https://m.facebook.com/me",
):
    """Save posts to JSON file with statistics"""
    try:
        # Create output directory if filename contains output path
        if "/" in filename or "\\" in filename:
            os.makedirs(os.path.dirname(filename), exist_ok=True)

        data = {
            "scrapedAt": datetime.now().isoformat(),
            "totalPosts": len(posts),
            "source": source,
            "method": "CDP Session (Mobile) + Advanced Cleaning",
            "cleaningStats": stats,
            "posts": posts,
        }

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"💾 Clean data berhasil disimpan ke {filename}")

        # Also create CSV file for analysis
        csv_filename = filename.replace(".json", ".csv")
        save_to_csv(posts, csv_filename)

        # Save cleaning report
        report_filename = filename.replace(".json", "_cleaning_report.json")
        save_cleaning_report(stats, report_filename)

    except Exception as error:
        print(f"❌ Error saving to file: {error}")


def save_cleaning_report(stats: Dict[str, Any], filename: str):
    """Save cleaning report to file"""
    try:
        # Create output directory if filename contains output path
        if "/" in filename or "\\" in filename:
            os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        print(f"📊 Cleaning report saved to {filename}")
    except Exception as error:
        print(f"❌ Error saving cleaning report: {error}")


def save_to_csv(posts: List[Dict[str, Any]], filename: str):
    """Save posts to CSV file with sentiment analysis"""
    try:
        # Create output directory if filename contains output path
        if "/" in filename or "\\" in filename:
            os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(
                [
                    "Text",
                    "Timestamp",
                    "Author",
                    "URL",
                    "Status",
                    "Sentiment_Score",
                    "Emotion",
                    "Key_Topics",
                ]
            )

            for post in posts:
                # Convert key_topics list to comma-separated string
                key_topics_str = (
                    ", ".join(post.get("key_topics", []))
                    if post.get("key_topics")
                    else ""
                )

                writer.writerow(
                    [
                        post.get("text", ""),
                        post.get("timestamp", ""),
                        post.get("author", ""),
                        post.get("url", ""),
                        post.get("status", ""),
                        f"{post.get('sentiment_score', 0):.2f}",
                        post.get("emotion", ""),
                        key_topics_str,
                    ]
                )

        print(f"📊 Data CSV berhasil disimpan ke {filename}")
    except Exception as error:
        print(f"❌ Error saat menyimpan CSV: {error}")
