# Facebook CDP Scraper - Python Version

Advanced Facebook scraper menggunakan CDP (Chrome DevTools Protocol) dengan stealth mode dan simulasi mobile iPhone Portrait.

## Features

- 🎯 **CDP Integration**: Menggunakan Chrome DevTools Protocol untuk kontrol browser yang lebih dalam
- 📱 **Mobile Simulation**: Simulasi iPhone 8 dengan orientasi portrait (375x667px)
- 🔒 **Stealth Mode**: Anti-deteksi bot dengan human behavior simulation
- 🧹 **Advanced Cleaning**: Filtering noise dan UI elements dengan pattern matching
- 📊 **Quality Scoring**: Confidence scoring untuk setiap post yang di-extract
- 📁 **Multiple Output**: JSON dan CSV output dengan cleaning statistics

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install Playwright browsers:
```bash
playwright install chromium
```

3. Copy dan edit file environment:
```bash
cp .env.example .env
# Edit .env dengan kredensial Facebook Anda
```

## Usage

### Basic Usage

```bash
python main.py
```

### Import dalam script lain

```python
from cdp_facebook_scraper import CDPFacebookScraper

async def scrape_facebook():
    scraper = CDPFacebookScraper()
    
    await scraper.init()
    
    if await scraper.login():
        posts = await scraper.scrape_status()
        await scraper.save_to_file(posts)
    
    await scraper.close()

# Run with asyncio
import asyncio
asyncio.run(scrape_facebook())
```

## Configuration

Environment variables yang bisa dikonfigurasi:

- `FACEBOOK_EMAIL`: Email Facebook
- `FACEBOOK_PASSWORD`: Password Facebook  
- `HEADLESS`: true/false - Mode headless browser
- `SLOW_MO_MS`: Delay antar action (ms)
- `MAX_POSTS_TO_SCRAPE`: Maksimal post yang di-scrape
- `SCRAPE_DELAY_MS`: Delay antar scroll (ms)
- `TARGET_PROFILE_URL`: URL profil target (opsional)

## Output Files

Scraper akan menghasilkan file:

- `facebook_feed_posts_cdp.json`: Data utama dengan metadata
- `facebook_feed_posts_cdp.csv`: Data dalam format CSV
- `facebook_feed_posts_cdp_report.json`: Laporan cleaning statistics

## Architecture

### Class Structure

- `CDPFacebookScraper`: Main class dengan semua functionality
- `_init_cleaning_patterns()`: Inisialisasi regex patterns untuk filtering
- `init()`: Setup browser dengan CDP dan stealth mode
- `login()`: Login ke Facebook dengan deteksi anti-bot
- `scrape_status()`: Main scraping function dengan auto-scroll
- `_extract_posts_with_advanced_cleaning()`: Advanced post extraction dan cleaning

### Cleaning Pipeline

1. **Raw Extraction**: Extract semua element dengan selector yang ditentukan
2. **Noise Filtering**: Filter UI elements, buttons, timestamps, dll
3. **Content Validation**: Validasi apakah text adalah konten post yang valid
4. **Duplicate Detection**: Deteksi dan hapus duplikasi
5. **Author Enhancement**: Extract author dengan fallback methods
6. **Confidence Scoring**: Hitung confidence score berdasarkan berbagai faktor

## Stealth Features

- User agent iPhone mobile
- Custom screen resolution 375x667
- Request interception dan header modification
- Random delays dan mouse movements
- Anti-fingerprinting properties
- Dimensions bar untuk monitoring real-time

## Troubleshooting

### Login Issues

- Pastikan kredensial benar di file `.env`
- Cek apakah ada 2FA atau captcha
- Lihat screenshot `login_failed.png` atau `login_error.png`

### Scraping Issues

- Periksa selector apakah masih valid
- Cek apakah Facebook mengubah struktur HTML
- Adjust delay di environment variables

## Development

Untuk development dan debugging:

1. Set `HEADLESS=false` untuk melihat browser
2. Increase `SLOW_MO_MS` untuk debugging
3. Gunakan screenshot function untuk debugging

## Differences from JavaScript Version

- Menggunakan Playwright Python async API
- Type hints untuk better code documentation
- Async/await pattern dengan proper exception handling
- More Pythonic code structure dan naming conventions
- Built-in CSV writer untuk better CSV handling
