(containerEl, index) => {

    // Look for text content in this container only - take first one only
    const textAreas = containerEl.querySelectorAll('[data-mcomponent="TextArea"]');

    if (textAreas.length === 0) return null;

    // Get first TextArea that contains span.f1 with valid content
    let text = '';
    let validTextArea = null;

    for (const textArea of textAreas) {
        const spanF1 = textArea.querySelector('span.f1');
        if (spanF1) {
            const candidateText = spanF1.textContent?.trim();
            // Skip if this is translation text or metadata
            if (candidateText &&
                candidateText.length > 10 &&
                !candidateText.includes('Translated from') &&
                !candidateText.includes('See translation') &&
                !candidateText.includes('Original text') &&
                !candidateText.match(/^\d+[hmdHMD](\s+(ago|lalu))?$/i) && // Skip timestamp like "2h ago"
                !candidateText.match(/^(Like|Comment|Share|Follow|More)$/i)) {

                text = candidateText;
                validTextArea = textArea;
                break; // Take first valid, skip others
            }
        }
    }

    if (!text || !validTextArea) return null;

    // Find author in this container
    let author = '';
    const authorElements = containerEl.querySelectorAll('span.f2.a, h3 a, h4 a');
    for (const authorEl of authorElements) {
        const candidateAuthor = authorEl.textContent?.trim();
        if (candidateAuthor && candidateAuthor.length > 0) {
            author = candidateAuthor;
            break;
        }
    }

    // Find timestamp
    let timestamp = '';
    const timeElement = containerEl.querySelector('time, abbr');
    if (timeElement) {
        timestamp = timeElement.getAttribute('datetime') ||
            timeElement.getAttribute('title') ||
            timeElement.textContent || '';
    }

    return {
        id: `container_post_${index}`,
        text: text,
        author: author,
        timestamp: timestamp,
        url: window.location.href,
        selector: 'MContainer[role-button-child]'
    };
}
