from utils import read_js_script, save_to_file, save_cleaning_report, save_to_csv
from console import Console

#!/usr/bin/env python3
"""
CDP Facebook Scraper - Python Version
Advanced Facebook scraper using CDP (Chrome DevTools Protocol) with stealth mode
Mobile iPhone Portrait simulation for better compatibility
"""

import time
import re
import os
import random
from config import Env
from datetime import datetime
from typing import List, Dict, Any, Optional
from playwright.sync_api import sync_playwright, Browser, Page, BrowserContext


class CDPFacebookScraper:
    """
    Advanced Facebook scraper using CDP with stealth mode and mobile simulation
    """

    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.context: Optional[BrowserContext] = None
        self.cdp_session = None
        self.is_logged_in = False
        self.posts: List[Dict[str, Any]] = []
        self.cleaned_posts: List[Dict[str, Any]] = []

        # Initialize cleaning patterns
        self._init_cleaning_patterns()

    def _init_cleaning_patterns(self):
        """Initialize patterns for filtering noise/UI elements"""
        # Patterns untuk filtering noise/UI elements
        self.noise_patterns = [
            # UI elements
            re.compile(r"^(Like|Comment|Share|Follow|More)$", re.IGNORECASE),
            re.compile(r"^\d+[KM]?\s*(Comments?|Like|Share|Follow)$", re.IGNORECASE),
            re.compile(
                r"^(People You May Know|Suggested for you|See all)$", re.IGNORECASE
            ),
            re.compile(r"^\d+\s*mutual friends?$", re.IGNORECASE),
            re.compile(r"^(Add Friend|Remove|Block|Report)$", re.IGNORECASE),
            re.compile(r"^(What's on your mind\?|Photo|Video|Live)$", re.IGNORECASE),
            re.compile(r"^(Home|Search|Notifications|Menu|Profile)$", re.IGNORECASE),
            re.compile(r"^(News Feed|Stories|Groups|Pages|Events)$", re.IGNORECASE),
            # Navigation and interaction elements
            re.compile(r"^(󰍸|󰍹|󰍺|󰞋)"),  # Facebook reaction icons
            re.compile(r"^[\U0001F300-\U0001F6FF]+$"),  # Emoji-only content
            re.compile(r"^\d+$"),  # Numbers only (like counts)
            re.compile(r"^\d+[KM]$"),  # Like counts (1K, 2M, etc)
            re.compile(r"^(󱘋|🎥|📷|📸|🎵)"),  # Media icons
            # Time stamps and metadata
            re.compile(r"^\d+[hmdHMD]$"),  # 1h, 2d, 3m ago
            re.compile(r"^(Just now|Yesterday|Today)$", re.IGNORECASE),
            re.compile(r"^(Sponsored|Promoted|Advertisement)$", re.IGNORECASE),
            re.compile(r"^(Privacy|Public|Friends|Custom)$", re.IGNORECASE),
            # Translation metadata
            re.compile(r"^Translated from \w+$", re.IGNORECASE),
            re.compile(r"^See translation$", re.IGNORECASE),
            re.compile(r"^Original text$", re.IGNORECASE),
            # Generic short noise
            re.compile(r"^[\.]{3,}$"),  # Three dots or more
            re.compile(r"^[…]+$"),  # Ellipsis
            re.compile(r"^[\s\n\r]*$"),  # Whitespace only
        ]

        # Patterns untuk identifying real post content
        self.post_content_patterns = [
            # Text that looks like real posts (longer than 20 chars, contains meaningful words)
            re.compile(
                r"[a-zA-Z]{3,}.*[a-zA-Z]{3,}"
            ),  # Contains at least 2 words of 3+ letters
            re.compile(r"[.!?]{1}"),  # Contains sentence endings
            re.compile(r"[,:;]"),  # Contains punctuation
        ]

    def init(self):
        """Initialize browser with CDP enabled for mobile simulation"""
        Console.log("🚀 Memulai CDP Facebook Scraper (Mobile Mode)...")
        # Launch browser with CDP enabled for mobile simulation
        playwright = sync_playwright().start()
        self.browser = playwright.chromium.launch(
            headless=Env.HEADLESS,
            slow_mo=Env.SLOW_MO_MS,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
                "--disable-web-security",
                "--disable-features=VizDisplayCompositor",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-default-apps",
                "--disable-extensions",
                "--disable-plugins",
                "--disable-javascript-harmony-shipping",
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding",
                "--disable-features=TranslateUI",
                "--disable-ipc-flooding-protection",
                "--enable-features=NetworkService,NetworkServiceLogging",
                "--force-color-profile=srgb",
                "--metrics-recording-only",
                "--no-zygote",
                "--disable-gpu",
                "--disable-software-rasterizer",
                "--disable-background-networking",
                "--disable-sync",
                "--disable-translate",
                "--hide-scrollbars",
                "--mute-audio",
                "--safebrowsing-disable-auto-update",
                "--ignore-certificate-errors",
                "--ignore-ssl-errors",
                "--ignore-certificate-errors-spki-list",
                # Mobile-specific args (user agent set in context)
                "--window-size=375,667",
                "--mobile-emulation=device=iPhone 8",
                "--enable-touch-events",
                "--disable-touch-adjustment",
            ],
        )
        # Create context with mobile user agent
        self.context = self.browser.new_context(
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1",
            viewport={"width": 375, "height": 667},
        )
        self.page = self.context.new_page()
        # Get CDP session
        self.cdp_session = self.context.new_cdp_session(self.page)
        # Enable CDP domains
        self.cdp_session.send("Page.enable")
        self.cdp_session.send("Network.enable")
        self.cdp_session.send("Runtime.enable")
        # Set stealth properties
        self._setup_stealth()
        Console.success(
            "✅ CDP Browser berhasil diinisialisasi dengan stealth mode (Mobile iPhone Portrait)"
        )
        Console.info(
            "📏 Dimensions bar aktif - Double-click untuk toggle, Ctrl+Shift+D untuk hide/show"
        )

    def _setup_stealth(self):
        """Setup stealth properties to avoid detection"""
        try:
            # Load stealth script from external file
            script_path = os.path.join(
                os.path.dirname(__file__), "script", "stealth_script.js"
            )
            try:
                with open(script_path, "r", encoding="utf-8") as f:
                    stealth_script = f.read()
                self.page.add_init_script(stealth_script)
                Console.success("✅ Stealth script loaded from external file")
            except FileNotFoundError:
                Console.warning(f"⚠️ Stealth script file not found: {script_path}")
                # Fallback to inline script if file doesn't exist
                self._setup_stealth_inline()
                return

            # Set extra headers for mobile
            self.page.set_extra_http_headers(
                {
                    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                    "Cache-Control": "max-age=0",
                    "Pragma": "no-cache",
                    "Sec-Ch-Ua": '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
                    "Sec-Ch-Ua-Mobile": "?1",
                    "Sec-Ch-Ua-Platform": '"iOS"',
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                    "Sec-Fetch-User": "?1",
                    "Upgrade-Insecure-Requests": "1",
                    "DNT": "1",
                }
            )

            # Intercept and modify requests
            def handle_route(route):
                request = route.request
                # Skip images, fonts, dan media untuk mempercepat loading
                if request.resource_type in ["image", "font", "media", "websocket"]:
                    route.abort()
                    return
                # Modify headers untuk request Facebook mobile
                if "facebook.com" in request.url:
                    headers = dict(request.headers)
                    headers.update(
                        {
                            "Referer": "https://m.facebook.com/",
                            "Origin": "https://m.facebook.com",
                            "Sec-Fetch-Site": (
                                "same-origin" if "login" in request.url else "same-site"
                            ),
                            "Sec-Fetch-Mode": "cors",
                            "Sec-Fetch-Dest": "empty",
                        }
                    )
                    route.continue_(headers=headers)
                else:
                    route.continue_()

            self.page.route("**/*", handle_route)

            Console.success(
                "✅ Stealth mode berhasil diaktifkan dengan pengaturan lengkap"
            )

        except Exception as error:
            Console.warning(f"⚠️ Warning: Stealth setup tidak sempurna: {error}")

    def _setup_stealth_inline(self):
        """Fallback method for stealth setup using external fallback script"""
        try:
            # Load fallback stealth script from external file
            fallback_stealth_script = read_js_script("stealth_fallback.js")
            self.page.add_init_script(fallback_stealth_script)
            Console.success("✅ Fallback stealth script loaded from external file")
        except Exception as error:
            Console.warning(f"⚠️ Warning: Fallback stealth setup failed: {error}")

    def login(self) -> bool:
        """Login to Facebook with CDP mobile mode"""
        try:
            Console.log(
                "🔐 Mencoba login ke Facebook dengan CDP (Mobile iPhone Portrait)..."
            )
            # Open Facebook mobile login page
            self.page.goto(
                "https://m.facebook.com/login",
                wait_until="domcontentloaded",
                timeout=60000,
            )
            # Wait for login form to appear
            self.page.wait_for_load_state("networkidle", timeout=10000)

            # Try multiple selectors for email field
            email_selectors = [
                '[name="email"]',
                'input[type="email"]',
                'input[placeholder*="email"]',
            ]
            email_found = False

            for selector in email_selectors:
                try:
                    self.page.wait_for_selector(selector, timeout=5000)
                    Console.debug(
                        f"📧 Email field ditemukan dengan selector: {selector}"
                    )

                    # Simulate human behavior before input
                    self._simulate_human_behavior()

                    # Clear and input email with natural delay
                    self.page.click(selector)
                    self.page.keyboard.press("Control+a")
                    self.page.keyboard.press("Delete")
                    self.page.keyboard.type(
                        Env.FACEBOOK_EMAIL, delay=random.randint(15, 25)
                    )
                    Console.success("📧 Email berhasil diinput")
                    email_found = True
                    break
                except Exception:
                    Console.warning(
                        f"⚠️ Selector {selector} tidak ditemukan, mencoba yang lain..."
                    )

            if not email_found:
                Console.error("❌ Tidak dapat menemukan field email")
                return False

                # Wait a bit before password input - removed time.sleep(1) as wait_for_selector below handles it
            self.page.wait_for_selector(selector, timeout=5000)

            # Try multiple selectors for password field
            password_selectors = [
                '[name="pass"]',
                'input[type="password"]',
                'input[placeholder*="password"]',
            ]
            password_found = False

            for selector in password_selectors:
                try:
                    self.page.wait_for_selector(selector, timeout=5000)
                    Console.debug(
                        f"🔑 Password field ditemukan dengan selector: {selector}"
                    )

                    # Clear and input password
                    self.page.click(selector)
                    self.page.keyboard.press("Control+a")
                    self.page.keyboard.press("Delete")
                    self.page.keyboard.type(
                        Env.FACEBOOK_PASSWORD, delay=random.randint(15, 25)
                    )
                    Console.success("🔑 Password berhasil diinput")
                    password_found = True
                    break
                except Exception:
                    Console.warning(
                        f"⚠️ Selector {selector} tidak ditemukan, mencoba yang lain..."
                    )

            if not password_found:
                Console.error("❌ Tidak dapat menemukan field password")
                return False

            # Wait for page to be ready for login button interaction
            self.page.wait_for_load_state("domcontentloaded", timeout=5000)

            # Try to click login button
            login_clicked = False
            try:
                login_button = self.page.wait_for_selector(
                    '[role="button"]:has-text("Login")', timeout=5000
                )
                if login_button:
                    login_button.click()
                    Console.success("✅ Tombol login diklik")
                    login_clicked = True
            except Exception:
                Console.warning("⚠️ Gagal klik tombol login")

            if not login_clicked:
                Console.error("❌ Tidak dapat menemukan tombol login")
                return False

            # Wait for login process with network activity check
            Console.log("⏳ Menunggu proses login...")
            try:
                self.page.wait_for_load_state("networkidle", timeout=60000)
                Console.debug("✅ Login selesai Normal")
            except Exception:
                # Fallback if networkidle doesn't work
                self.page.wait_for_load_state("domcontentloaded", timeout=60000)
                Console.debug("✅ Login selesai Exception")

            # Handle post-login dialogs and skip buttons
            self._handle_post_login_dialog("Lain Kali")

            # Check login status
            is_logged_in = self._check_login_status()

            if is_logged_in:
                self.is_logged_in = True
                Console.success("✅ Login berhasil dengan CDP (Mobile iPhone)!")
                return True
            else:
                Console.error(
                    "❌ Login gagal, cek kredensial atau ada captcha/verifikasi"
                )
                # Screenshot for debugging
                try:
                    self.page.screenshot(path="login_failed.png", full_page=True)
                    Console.info("📸 Screenshot disimpan sebagai login_failed.png")
                except Exception:
                    Console.warning("⚠️ Gagal menyimpan screenshot")
                return False

        except Exception as error:
            Console.error(f"❌ Error saat login: {error}")
            # Screenshot for debugging
            try:
                self.page.screenshot(path="login_error.png", full_page=True)
                Console.info("📸 Screenshot error disimpan sebagai login_error.png")
            except Exception:
                Console.warning("⚠️ Gagal menyimpan screenshot error")
            return False

    def _simulate_human_behavior(self):
        """Simulate human behavior with random mouse movements and scroll"""
        try:
            # Random mouse movements
            viewport = self.page.viewport_size
            for _ in range(3):
                x = random.randint(0, viewport["width"])
                y = random.randint(0, viewport["height"])
                self.page.mouse.move(x, y)
                time.sleep(random.uniform(0.2, 0.7))

            # Random scroll
            random_scroll_script = read_js_script("random_scroll.js")
            self.page.evaluate(random_scroll_script)
            time.sleep(random.uniform(0.5, 1.5))
        except Exception:
            # Ignore errors in human simulation
            pass

    def _handle_post_login_dialog(self, text: str):
        Console.debug("🔄 Menangani dialog dan tombol setelah login...")
        try:
            selector = f'[role="button"]:has-text("{text}")'
            button = self.page.wait_for_selector(selector, timeout=5000)
            if button and button.is_visible():
                button.click()
                Console.success(f"✅ Berhasil klik tombol: {selector}")
                # Wait a bit for the dialog to disappear
                self.page.wait_for_timeout(1000)
        except Exception as e:
            Console.warning(f"⚠️ Error handling text parameter: {e}")
        finally:
            self.page.wait_for_timeout(5000)

    def _handle_post_login_dialogs(self):
        """Handle various post-login dialogs and skip buttons that Facebook shows"""
        Console.debug("🔄 Menangani dialogs dan tombol...")

        # List of common post-login buttons/dialogs to dismiss
        list_buttons = [
            # "Lain Kali" button (Later button)
            '[role="button"]:has-text("Lain Kali")',
            '[role="button"]:has-text("Later")',
            # Skip buttons for notifications, contacts sync, etc.
            '[role="button"]:has-text("Skip")',
            '[role="button"]:has-text("Lewati")',
            '[role="button"]:has-text("Not Now")',
            '[role="button"]:has-text("Tidak Sekarang")',
            # Close buttons for popups
            '[role="button"][aria-label="Close"]',
            '[role="button"][aria-label="Tutup"]',
            # Dismiss buttons
            '[role="button"]:has-text("Dismiss")',
            '[role="button"]:has-text("Abaikan")',
            # Cancel buttons for setup prompts
            '[role="button"]:has-text("Cancel")',
            '[role="button"]:has-text("Batal")',
            # OK buttons to acknowledge
            '[role="button"]:has-text("OK")',
        ]

        # Try each button type with timeout
        for button_selector in list_buttons:
            try:
                button = self.page.wait_for_selector(button_selector, timeout=3000)
                if button and button.is_visible():
                    button.click()
                    Console.success(f"✅ Berhasil klik tombol: {button_selector}")
                    # Wait a bit for the dialog to disappear
                    self.page.wait_for_timeout(1000)
                    # Continue checking for more dialogs
            except Exception:
                # No button found or click failed, continue to next
                continue

        # Special handling for mobile Facebook save login info dialog
        try:
            # Look for "Save Login Info" or similar dialogs
            save_info_selectors = [
                '[role="button"]:has-text("Save")',
                '[role="button"]:has-text("Simpan")',
                '[role="button"]:has-text("Don\'t Save")',
                '[role="button"]:has-text("Jangan Simpan")',
            ]

            for selector in save_info_selectors:
                button = self.page.query_selector(selector)
                if button and button.is_visible():
                    # Prefer "Don't Save" to avoid saving login info
                    if "Don't" in selector or "Jangan" in selector:
                        button.click()
                        Console.success(f"✅ Klik 'Don't Save' login info")
                        break
                    elif "Save" in selector or "Simpan" in selector:
                        button.click()
                        Console.success(f"✅ Klik 'Save' login info")
                        break
        except Exception:
            Console.debug("ℹ️ Tidak ada dialog save login info")

        Console.debug("✅ Selesai menangani post-login dialogs")

    def _check_login_status(self) -> bool:
        """Check if login was successful"""
        try:
            # Check several login indicators for mobile
            login_button = self.page.query_selector('[role="button"]:has-text("Login")')
            menu_button = self.page.query_selector(
                '[role="button"][aria-label*="Facebook Menu"]'
            )
            home_link = self.page.query_selector(
                '[role=button][aria-label="Facebook logo"]'
            )
            profile_link = self.page.query_selector(
                '[role=button][aria-label*="Go to profile"]'
            )
            search_box = self.page.query_selector(
                '[role=button][aria-label="Search Facebook"]'
            )

            # If no login button and has elements showing logged in
            return not login_button and (
                profile_link or home_link or search_box or menu_button
            )
        except Exception:
            return False

    def scrape_status(self, target_url: Optional[str] = None) -> List[Dict[str, Any]]:
        """Scrape status posts from Facebook feed"""
        if not self.is_logged_in:
            Console.error("❌ Harus login terlebih dahulu")
            return []

        try:
            url = target_url or "https://m.facebook.com/"
            Console.debug(f"📱 Membuka halaman: {url}")

            if self.page.url != url:
                self.page.goto(url, wait_until="networkidle", timeout=30000)

            # Wait for initial content to load
            try:
                self.page.wait_for_selector(
                    '[data-mcomponent="MContainer"], [role="main"], [data-testid="post_message"]',
                    timeout=10000,
                )
            except Exception:
                Console.warning(
                    "⚠️ Initial content selector not found, using load state wait"
                )
                self.page.wait_for_load_state("domcontentloaded", timeout=5000)

            # Wait for additional content to settle
            try:
                self.page.wait_for_load_state("networkidle", timeout=10000)
            except Exception:
                Console.warning(
                    "⚠️ Network idle timeout, continuing with available content"
                )

            # Scroll to load more posts
            self._auto_scroll()

            # Scrape status posts with advanced cleaning
            posts = self._extract_posts_with_advanced_cleaning()

            Console.success(f"✅ Berhasil scrape {len(posts)} clean status")
            self.posts = posts
            self.cleaned_posts = posts
            return posts

        except Exception as error:
            Console.error(f"❌ Error saat scraping status: {error}")
            return []

    def _auto_scroll(self):
        """Auto-scroll to load more posts"""
        Console.debug("📜 Melakukan auto-scroll untuk memuat lebih banyak post...")

        max_posts = Env.MAX_POSTS_TO_SCRAPE
        loaded_posts = 0
        previous_height = 0
        scroll_attempts = 0
        max_scroll_attempts = 25

        while loaded_posts < max_posts and scroll_attempts < max_scroll_attempts:
            # Scroll with smooth scroll and random distance
            scroll_distance = random.randint(600, 1000)
            scroll_script = read_js_script("scroll_by.js")
            scroll_script = scroll_script.replace(
                "SCROLL_DISTANCE", str(scroll_distance)
            )
            self.page.evaluate(scroll_script)

            # Wait for new content to load after scroll
            delay = random.randint(1000, 2000) + Env.SCRAPE_DELAY_MS
            try:
                # Wait for potential new content to appear
                self.page.wait_for_function(
                    f"""() => {{
                        return new Promise(resolve => {{
                            let initialCount = document.querySelectorAll('[data-mcomponent="MContainer"]').length;
                            setTimeout(() => {{
                                let newCount = document.querySelectorAll('[data-mcomponent="MContainer"]').length;
                                resolve(true); // Always resolve after delay
                            }}, {delay});
                        }});
                    }}""",
                    timeout=delay + 2000,
                )
            except Exception:
                # Fallback to time-based delay if wait_for_function fails
                delay_seconds = delay / 1000
                time.sleep(min(delay_seconds, 3.0))  # Cap at 3 seconds max

            # Count loaded posts
            current_posts = self.page.query_selector_all(
                '[data-mcomponent="MContainer"]:has([data-mcomponent="TextArea"]), '
                '[data-testid="post_message"], [data-testid="post_text"], '
                '.userContent, .post-content, [data-nt="NT:TEXT"]'
            )
            loaded_posts = len(current_posts)

            # Check if we've reached the bottom
            current_height = self.page.evaluate("document.body.scrollHeight")
            if current_height == previous_height:
                scroll_attempts += 1
            else:
                scroll_attempts = 0

            previous_height = current_height
            Console.debug(
                f"📊 Post yang sudah dimuat: {loaded_posts}, Scroll attempt: {scroll_attempts}"
            )

            # If scrolled 3 times without change, stop
            if scroll_attempts >= 3:
                Console.info(
                    "📄 Sudah mencapai akhir halaman atau tidak ada content baru"
                )
                break

    def _extract_posts_advanced(self) -> List[Dict[str, Any]]:
        """Extract posts using advanced filtering"""
        try:
            # Filter elements based on containers
            selector = '[data-mcomponent="MContainer"]'
            container_elements = self.page.query_selector_all(selector)
            Console.debug(
                f'🔍 Found {len(container_elements)} valid post containers with role="button"'
            )

            posts = []
            processed_containers = set()

            for i, container in enumerate(container_elements):
                try:
                    # Get container identifier to avoid duplicate processing
                    container_id = container.get_attribute("id") or f"container_{i}"
                    if container_id in processed_containers:
                        continue
                    processed_containers.add(container_id)

                    # Extract post data from this specific container
                    extract_container_js = read_js_script(
                        "extract_container_post_data.js"
                    )
                    post_data = container.evaluate(extract_container_js, i)

                    if post_data and post_data.get("text"):
                        posts.append(post_data)
                        Console.debug(
                            f"📝 Extracted from valid container {i}: \"{post_data['text'][:50]}...\" (Author: {post_data.get('author', 'N/A')})"
                        )

                except Exception as error:
                    Console.warning(f"⚠️ Error processing container {i}: {error}")

            Console.success(
                f"✅ Extracted {len(posts)} posts from {len(container_elements)} valid containers"
            )
            return posts

        except Exception as error:
            Console.error(f"❌ Error saat extract posts: {error}")
            return []

    def _is_noise_content(self, text: str) -> bool:
        """Check if text is noise/UI content"""
        if not text or not isinstance(text, str):
            return True

        clean_text = text.strip()

        # Check length - too short is likely noise
        if len(clean_text) < 10:
            return True

        # Check against noise patterns
        for pattern in self.noise_patterns:
            if pattern.search(clean_text):
                return True

        return False

    def _is_real_post_content(self, text: str) -> bool:
        """Check if text is real post content"""
        if not text or not isinstance(text, str):
            return False

        clean_text = text.strip()

        # Must be at least 15 characters
        if len(clean_text) < 15:
            return False

        # Check if it contains meaningful content patterns
        for pattern in self.post_content_patterns:
            if pattern.search(clean_text):
                return True

        # If no pattern matches, it's not real content
        return False

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""

        # Normalize whitespace and remove zero-width characters
        cleaned = re.sub(r"\s+", " ", text.strip())
        cleaned = re.sub(r"[\u200B-\u200D\uFEFF]", "", cleaned)
        cleaned = re.sub(r"[^\S\r\n]+", " ", cleaned)

        return cleaned.strip()

    def _calculate_confidence(self, text: str) -> float:
        """Calculate confidence score for text content"""
        confidence = 0.0

        # Length bonus
        if len(text) > 50:
            confidence += 0.3
        if len(text) > 100:
            confidence += 0.2

        # Sentence structure bonus
        if any(char in text for char in ".!?"):
            confidence += 0.2

        # Multiple sentences bonus
        sentences = [s.strip() for s in re.split(r"[.!?]+", text) if len(s.strip()) > 5]
        if len(sentences) > 1:
            confidence += 0.2

        # Pattern matching bonus
        for pattern in self.post_content_patterns:
            if pattern.search(text):
                confidence += 0.1
                break  # Only add bonus once

        return min(confidence, 1.0)  # Cap at 1.0

    def _extract_posts_with_advanced_cleaning(self) -> List[Dict[str, Any]]:
        """Extract posts with advanced cleaning and filtering"""
        try:
            Console.debug("🧹 Starting advanced post extraction with cleaning...")

            raw_posts = self._extract_posts_advanced()
            Console.info(f"📝 Extracted {len(raw_posts)} raw posts")

            if not raw_posts:
                Console.warning("⚠️  No raw posts found")
                return []

            # Clean posts with advanced filtering
            cleaned_posts = []
            duplicate_tracker = set()

            for i, post in enumerate(raw_posts):
                original_text = post.get("text", "")

                # Skip if it's noise content
                if self._is_noise_content(original_text):
                    Console.debug(f'⏭️  Skipped noise: "{original_text[:50]}..."')
                    continue

                # Check if it's real post content
                if not self._is_real_post_content(original_text):
                    Console.debug(f'⏭️  Skipped non-content: "{original_text[:50]}..."')
                    continue

                # Clean the text
                clean_text = self._clean_text(original_text)

                # Simple duplicate detection based on clean text
                if clean_text.lower() in duplicate_tracker:
                    Console.debug(f'⏭️  Skipped duplicate: "{clean_text[:50]}..."')
                    continue
                duplicate_tracker.add(clean_text.lower())

                # Enhanced author extraction
                enhanced_author = post.get("author", "")
                if not enhanced_author or len(enhanced_author) < 2:
                    try:
                        enhanced_author = self._extract_author_for_post(clean_text)
                    except Exception as error:
                        Console.warning(
                            f"⚠️  Could not enhance author for post: {error}"
                        )

                # Skip post if no author found
                if not enhanced_author or not enhanced_author.strip():
                    Console.debug(f'⏭️  Skipped no author: "{clean_text[:50]}..."')
                    continue

                # Filter out unwanted selectors from being saved
                clean_selector = post.get("selector", "")
                unwanted_selectors = [
                    'div[data-mcomponent="MContainer"] [data-mcomponent="TextArea"] div[dir="auto"]'
                ]

                if any(selector in clean_selector for selector in unwanted_selectors):
                    clean_selector = ""  # Don't save unwanted selectors

                # Create cleaned post object
                cleaned_post = {
                    "id": f"clean_post_{len(cleaned_posts) + 1}",
                    "originalId": post.get("id"),
                    "text": clean_text,
                    "author": enhanced_author,
                    "timestamp": post.get("timestamp") or datetime.now().isoformat(),
                    "url": post.get("url", ""),
                    "selector": clean_selector,
                    "confidence": self._calculate_confidence(clean_text),
                    "originalIndex": i,
                }

                cleaned_posts.append(cleaned_post)
                Console.success(
                    f'✅ Added clean post {len(cleaned_posts)}: "{clean_text[:60]}..." (Author: {enhanced_author or "N/A"}) [Confidence: {cleaned_post["confidence"]:.2f}]'
                )

            self.cleaned_posts = cleaned_posts
            Console.success(
                f"\n🎉 Advanced cleaning complete! Found {len(cleaned_posts)} clean posts out of {len(raw_posts)} raw posts."
            )

            return cleaned_posts

        except Exception as error:
            Console.error(f"❌ Error in advanced post extraction: {error}")
            return []

    def _extract_author_for_post(self, post_text: str) -> str:
        """Extract author for specific post text"""
        try:
            # Try to find author context for specific post text
            extract_author_js = read_js_script("extract_author_for_post.js")
            author_info = self.page.evaluate(extract_author_js, post_text[:100])

            if author_info and isinstance(author_info, str) and author_info.strip():
                return author_info.strip()
            return ""

        except Exception as error:
            Console.error(f"❌ Error extracting author for post: {error}")
            return ""

    def _calculate_cleaning_stats(
        self, cleaned_posts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate cleaning statistics"""
        total_cleaned = len(cleaned_posts)

        quality_distribution = {
            "highConfidence": len(
                [p for p in cleaned_posts if p.get("confidence", 0) >= 0.8]
            ),
            "mediumConfidence": len(
                [p for p in cleaned_posts if 0.5 <= p.get("confidence", 0) < 0.8]
            ),
            "lowConfidence": len(
                [p for p in cleaned_posts if p.get("confidence", 0) < 0.5]
            ),
        }

        top_posts = sorted(
            cleaned_posts, key=lambda x: x.get("confidence", 0), reverse=True
        )[:10]
        top_posts_formatted = []
        for i, post in enumerate(top_posts):
            text = post.get("text", "")
            truncated_text = text[:100] + ("..." if len(text) > 100 else "")
            top_posts_formatted.append(
                {
                    "rank": i + 1,
                    "confidence": f"{post.get('confidence', 0):.2f}",
                    "text": truncated_text,
                    "author": post.get("author", ""),
                    "timestamp": post.get("timestamp") or datetime.now().isoformat(),
                }
            )

        return {
            "summary": {
                "cleanedPosts": total_cleaned,
                "processingDate": datetime.now().isoformat(),
                "method": "CDP Session (Mobile) + Advanced Cleaning",
            },
            "topPosts": top_posts_formatted,
            "qualityDistribution": quality_distribution,
            "authorStats": self._calculate_author_stats(cleaned_posts),
        }

    def _calculate_author_stats(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate author statistics"""
        author_counts = {}
        posts_with_author = 0

        for post in posts:
            author = post.get("author", "")
            if author and author.strip():
                posts_with_author += 1
                author_counts[author] = author_counts.get(author, 0) + 1

        top_authors = sorted(author_counts.items(), key=lambda x: x[1], reverse=True)[
            :10
        ]
        top_authors_formatted = [
            {"author": author, "postCount": count} for author, count in top_authors
        ]

        return {
            "totalAuthors": len(author_counts),
            "postsWithAuthor": posts_with_author,
            "postsWithoutAuthor": len(posts) - posts_with_author,
            "authorCoverage": (
                f"{(posts_with_author / len(posts) * 100):.1f}%" if posts else "0.0%"
            ),
            "topAuthors": top_authors_formatted,
        }

    def save_posts(
        self, posts: List[Dict[str, Any]], filename: str = "facebook_posts_cdp.json"
    ):
        """Save posts using utils helper function"""
        try:
            stats = self._calculate_cleaning_stats(posts)
            source = (
                Env.TARGET_PROFILE_URL
                if hasattr(Env, "TARGET_PROFILE_URL")
                else "https://m.facebook.com/me"
            )
            save_to_file(posts, stats, filename, source)
        except Exception as error:
            Console.error(f"❌ Error in save_posts: {error}")

    def close(self):
        """Close browser and cleanup"""
        if self.browser:
            try:
                self.browser.close()
                Console.success("🔒 Browser berhasil ditutup")
            except Exception as error:
                Console.warning(f"⚠️ Error saat menutup browser: {error}")
