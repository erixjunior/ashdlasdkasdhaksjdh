/**
 * Fallback Stealth Script for Facebook Scraper
 * Simple anti-detection script used as fallback when main stealth script is not available
 * Mobile iPhone Portrait simulation
 */

(() => {
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined,
    });

    Object.defineProperty(navigator, 'plugins', {
        get: () => [
            {
                0: {
                    type: 'application/x-google-chrome-pdf',
                    suffixes: 'pdf',
                    description: 'Portable Document Format',
                    __pluginName: 'Chrome PDF Plugin',
                },
                description: 'Portable Document Format',
                filename: 'internal-pdf-viewer',
                length: 1,
                name: 'Chrome PDF Plugin',
            }
        ],
    });

    Object.defineProperty(navigator, 'languages', {
        get: () => ['id-ID', 'id', 'en-US', 'en'],
    });

    Object.defineProperty(screen, 'height', {
        get: () => 667,
    });

    Object.defineProperty(screen, 'width', {
        get: () => 375,
    });
})();
