#!/usr/bin/env python3
import time
import sys
import os
from cdp_facebook_scraper import CDPFacebookScraper
from console import Console
import utils


def main():
    """Main function to run the Facebook scraper"""
    scraper = CDPFacebookScraper()
    try:
        Console.log(
            "🎯 Facebook Status Scraper - CDP Stealth Version (Mobile iPhone Portrait)"
        )
        Console.log("================================================\n")
        # Initialize browser with CDP
        scraper.init()
        # Login to Facebook with CDP
        login_success = scraper.login()
        if not login_success:
            Console.error("❌ Tidak bisa melanjutkan tanpa login")
            Console.warning("💡 Kemungkinan penyebab:")
            Console.warning("   - Kredensial Facebook salah")
            Console.warning("   - Ada captcha atau verifikasi 2FA")
            Console.warning("   - Facebook mendeteksi aktivitas otomatis")
            Console.warning("   - Koneksi internet lambat")
            Console.info(
                "\n🔍 Cek file login_failed.png atau login_error.png untuk detail lebih lanjut"
            )
            return
        Console.success(
            "\n🎉 Login berhasil dengan CDP (Mobile iPhone Portrait)! Sekarang akan melakukan scraping...\n"
        )
        # Wait a bit after login
        time.sleep(5)

        # Scrape status from home/feed
        Console.debug("🏠 Scraping status dari beranda/feed...")
        feed_posts = scraper.scrape_status()
        if feed_posts:
            Console.success(
                f"\n📋 Berhasil scrape {len(feed_posts)} status dari beranda/feed"
            )
            # Save results
            scraper.save_posts(feed_posts, "facebook_feed_posts_cdp.json")
            # Show preview
            Console.info("\n Preview hasil scraping:")
            for index, post in enumerate(feed_posts[:5]):
                Console.log(f"\n--- Post {index + 1} ---")
                Console.log(f"Author: {post.get('author', 'Unknown')}")
                text = post.get("text", "")
                truncated_text = text[:150] + ("..." if len(text) > 150 else "")
                Console.log(f"Text: {truncated_text}")
                Console.log(f"Timestamp: {post.get('timestamp', 'Unknown')}")
                Console.log(f"Selector: {post.get('selector', '')}")
            if len(feed_posts) > 5:
                Console.info(f"\n... dan {len(feed_posts) - 5} post lainnya")
        else:
            Console.error("❌ Tidak ada post yang berhasil di-scrape")
        Console.success("\n✅ Scraping selesai dengan CDP!")
        Console.info("📁 File hasil scraping:")
        Console.info("   - facebook_feed_posts_cdp.json (dan .csv)")
        Console.info("\n🔒 Keunggulan CDP Scraper (Mobile iPhone Portrait):")
        Console.info("   - Menggunakan m.facebook.com untuk kompatibilitas mobile")
        Console.info("   - Simulasi perangkat iPhone 8 dengan orientasi portrait")
        Console.info("   - Viewport 375x667 pixels untuk responsive design")
        Console.info("   - 📏 Dimensions bar untuk monitoring ukuran real-time")
        Console.info("   - Anti-deteksi bot yang lebih kuat")
        Console.info("   - Stealth mode dengan human behavior simulation")
        Console.info("   - CDP session untuk kontrol browser yang lebih dalam")
        Console.info("   - Request interception dan modification")
        Console.info("   - Random delays dan movements")
    except Exception as error:
        Console.error(f"\n❌ Error utama: {error}")
        import traceback

        Console.error(f"Stack trace: {traceback.format_exc()}")
    finally:
        scraper.close()
        Console.info("\n🔒 CDP Scraper ditutup")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        Console.warning("\n🛑 Scraping dibatalkan oleh user")
    except Exception as e:
        Console.error(f"❌ Uncaught Exception: {e}")
        sys.exit(1)
