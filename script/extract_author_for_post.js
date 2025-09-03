(searchText) => {
    // Search for elements containing the post text
    const textElements = Array.from(document.querySelectorAll('span.f1')).filter(el =>
        el.textContent && el.textContent.trim() === searchText
    );

    for (const textEl of textElements) {
        let container = textEl.closest('[data-mcomponent="MContainer"]') || textEl.closest('.m');

        // Search up the DOM tree for author
        for (let i = 0; i < 5; i++) {
            if (!container) break;

            const authorEl = container.querySelector('span.f2.a[role="link"][data-focusable="true"]');
            if (authorEl) {
                return authorEl.textContent?.trim();
            }

            container = container.parentElement;
        }
    }

    return '';
}
