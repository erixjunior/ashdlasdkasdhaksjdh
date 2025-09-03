/**
 * Stealth Script for Facebook Scraper
 * Mobile iPhone Portrait Simulation
 * Anti-Detection and Browser Fingerprinting Protection
 */

(() => {
    // Remove webdriver property
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined,
    });

    // Override plugins dengan data yang lebih realistis
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
            },
            {
                0: {
                    type: 'application/pdf',
                    suffixes: 'pdf',
                    description: 'Portable Document Format',
                    __pluginName: 'Chrome PDF Viewer',
                },
                description: 'Portable Document Format',
                filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai',
                length: 1,
                name: 'Chrome PDF Viewer',
            },
        ],
    });
    // ...existing code...
})();
