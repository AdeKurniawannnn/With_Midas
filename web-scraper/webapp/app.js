/**
 * Web Scraper - Frontend Application
 * Uses Jina AI Reader API for web scraping
 */

// DOM Elements
const urlInput = document.getElementById('url-input');
const multiPageCheckbox = document.getElementById('multi-page');
const sameDomainCheckbox = document.getElementById('same-domain');
const depthInput = document.getElementById('depth');
const maxPagesInput = document.getElementById('max-pages');
const scrapeBtn = document.getElementById('scrape-btn');
const advancedOptions = document.getElementById('advanced-options');
const progressContainer = document.getElementById('progress-container');
const progressFill = document.getElementById('progress-fill');
const progressText = document.getElementById('progress-text');
const resultsContainer = document.getElementById('results-container');
const resultsMeta = document.getElementById('results-meta');
const resultsOutput = document.getElementById('results-output');
const errorContainer = document.getElementById('error-container');
const errorMessage = document.getElementById('error-message');
const copyBtn = document.getElementById('copy-btn');
const downloadBtn = document.getElementById('download-btn');

// State
let lastScrapedContent = '';
let lastScrapedUrl = '';
let lastScrapedData = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Toggle advanced options
    multiPageCheckbox.addEventListener('change', () => {
        advancedOptions.classList.toggle('show', multiPageCheckbox.checked);
    });

    // Scrape button click
    scrapeBtn.addEventListener('click', startScraping);

    // URL input enter key
    urlInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            startScraping();
        }
    });

    // Copy button
    copyBtn.addEventListener('click', copyToClipboard);

    // Download button
    downloadBtn.addEventListener('click', downloadMarkdown);

    // Smooth scroll for nav links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

/**
 * Validate URL format
 */
function isValidUrl(string) {
    try {
        const url = new URL(string);
        return url.protocol === 'http:' || url.protocol === 'https:';
    } catch (_) {
        return false;
    }
}

/**
 * Show/hide loading state
 */
function setLoading(isLoading) {
    const btnText = scrapeBtn.querySelector('.btn-text');
    const btnLoader = scrapeBtn.querySelector('.btn-loader');

    scrapeBtn.disabled = isLoading;
    btnText.style.display = isLoading ? 'none' : 'inline';
    btnLoader.style.display = isLoading ? 'flex' : 'none';
}

/**
 * Update progress bar
 */
function updateProgress(percent, text) {
    progressContainer.style.display = 'block';
    progressFill.style.width = `${percent}%`;
    progressText.textContent = text;
}

/**
 * Show error message
 */
function showError(message) {
    errorContainer.style.display = 'block';
    errorMessage.textContent = message;
    resultsContainer.style.display = 'none';
}

/**
 * Hide error message
 */
function hideError() {
    errorContainer.style.display = 'none';
}

/**
 * Format scraped data into beautiful HTML
 */
function formatScrapedContent(data) {
    let html = '';

    // Title Section
    if (data.title) {
        html += `<div class="result-section result-title">
            <h2>${escapeHtml(data.title)}</h2>
        </div>`;
    }

    // Description/Summary
    if (data.description) {
        html += `<div class="result-section result-description">
            <div class="section-label">📝 Description</div>
            <p>${escapeHtml(data.description)}</p>
        </div>`;
    }

    // URL
    if (data.url) {
        html += `<div class="result-section result-url">
            <div class="section-label">🔗 Source URL</div>
            <a href="${escapeHtml(data.url)}" target="_blank" rel="noopener">${escapeHtml(data.url)}</a>
        </div>`;
    }

    // Main Content
    if (data.content) {
        const formattedContent = formatMarkdownContent(data.content);
        html += `<div class="result-section result-content">
            <div class="section-label">📄 Content</div>
            <div class="content-body">${formattedContent}</div>
        </div>`;
    }

    // Metadata Table
    if (data.metadata && Object.keys(data.metadata).length > 0) {
        const importantMeta = extractImportantMetadata(data.metadata);
        if (importantMeta.length > 0) {
            html += `<div class="result-section result-metadata">
                <div class="section-label">📊 Page Metadata</div>
                <table class="meta-table">
                    <tbody>
                        ${importantMeta.map(m => `
                            <tr>
                                <td class="meta-key">${escapeHtml(m.key)}</td>
                                <td class="meta-value">${escapeHtml(m.value)}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>`;
        }
    }

    // Token Usage
    if (data.usage && data.usage.tokens) {
        html += `<div class="result-section result-tokens">
            <div class="section-label">⚡ API Usage</div>
            <span class="token-badge">${data.usage.tokens.toLocaleString()} tokens</span>
        </div>`;
    }

    return html;
}

/**
 * Extract important metadata fields
 */
function extractImportantMetadata(metadata) {
    const importantKeys = [
        'author', 'keywords', 'lang', 'description',
        'og:title', 'og:description', 'twitter:title',
        'robots', 'viewport'
    ];

    const result = [];

    for (const key of importantKeys) {
        if (metadata[key] && metadata[key].length < 200) {
            result.push({
                key: formatMetaKey(key),
                value: metadata[key]
            });
        }
    }

    return result.slice(0, 8); // Limit to 8 items
}

/**
 * Format metadata key for display
 */
function formatMetaKey(key) {
    return key
        .replace(/^og:/, 'OpenGraph: ')
        .replace(/^twitter:/, 'Twitter: ')
        .replace(/_/g, ' ')
        .replace(/\b\w/g, l => l.toUpperCase());
}

/**
 * Format markdown content to HTML
 */
function formatMarkdownContent(content) {
    // Clean up the content
    let formatted = escapeHtml(content);

    // Convert markdown headings
    formatted = formatted.replace(/^#{6}\s+(.*)$/gm, '<h6>$1</h6>');
    formatted = formatted.replace(/^#{5}\s+(.*)$/gm, '<h5>$1</h5>');
    formatted = formatted.replace(/^#{4}\s+(.*)$/gm, '<h4>$1</h4>');
    formatted = formatted.replace(/^#{3}\s+(.*)$/gm, '<h3>$1</h3>');
    formatted = formatted.replace(/^#{2}\s+(.*)$/gm, '<h2>$1</h2>');
    formatted = formatted.replace(/^#{1}\s+(.*)$/gm, '<h1>$1</h1>');

    // Convert bold
    formatted = formatted.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');

    // Convert italic
    formatted = formatted.replace(/\*([^*]+)\*/g, '<em>$1</em>');

    // Convert links (basic)
    formatted = formatted.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');

    // Convert horizontal rules
    formatted = formatted.replace(/^---+$/gm, '<hr>');
    formatted = formatted.replace(/^===+$/gm, '<hr>');
    formatted = formatted.replace(/^\*\*\*+$/gm, '<hr>');

    // Convert list items
    formatted = formatted.replace(/^\*\s+(.*)$/gm, '<li>$1</li>');
    formatted = formatted.replace(/^-\s+(.*)$/gm, '<li>$1</li>');

    // Convert line breaks to paragraphs
    formatted = formatted.replace(/\n\n+/g, '</p><p>');
    formatted = '<p>' + formatted + '</p>';

    // Clean up empty paragraphs
    formatted = formatted.replace(/<p>\s*<\/p>/g, '');
    formatted = formatted.replace(/<p>\s*<(h[1-6]|hr|li)/g, '<$1');
    formatted = formatted.replace(/<\/(h[1-6]|hr|li)>\s*<\/p>/g, '</$1>');

    // Remove image tags (they contain broken references)
    formatted = formatted.replace(/!\[Image \d+[^\]]*\]\([^)]+\)/g, '');
    formatted = formatted.replace(/!\[[^\]]*\]\([^)]+\)/g, '');

    return formatted;
}

/**
 * Escape HTML characters
 */
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Show results with formatted display
 */
function showResults(data, url) {
    resultsContainer.style.display = 'block';
    lastScrapedData = data;
    lastScrapedUrl = url;

    // Store raw markdown for copy/download
    lastScrapedContent = data.content || '';

    // Format and display
    const formattedHtml = formatScrapedContent(data);
    resultsOutput.innerHTML = formattedHtml;

    // Build meta info
    const metaItems = [];
    metaItems.push(`📍 ${url}`);
    if (data.title) metaItems.push(`📖 ${data.title.substring(0, 50)}...`);
    if (data.usage?.tokens) metaItems.push(`⚡ ${data.usage.tokens.toLocaleString()} tokens`);
    metaItems.push(`⏱️ ${new Date().toLocaleTimeString()}`);

    resultsMeta.textContent = metaItems.join('  •  ');
}

/**
 * Copy content to clipboard
 */
async function copyToClipboard() {
    if (!lastScrapedContent) return;

    try {
        await navigator.clipboard.writeText(lastScrapedContent);

        // Visual feedback
        const originalHTML = copyBtn.innerHTML;
        copyBtn.innerHTML = '✓';
        copyBtn.style.background = 'rgba(40, 200, 64, 0.3)';

        setTimeout(() => {
            copyBtn.innerHTML = originalHTML;
            copyBtn.style.background = '';
        }, 2000);
    } catch (err) {
        console.error('Failed to copy:', err);
    }
}

/**
 * Download content as markdown file
 */
function downloadMarkdown() {
    if (!lastScrapedContent) return;

    // Create filename from URL
    let filename = 'scraped-content';
    try {
        const url = new URL(lastScrapedUrl);
        filename = url.hostname.replace(/\./g, '-');
    } catch (_) {}

    // Build markdown with metadata
    let markdown = '';
    if (lastScrapedData) {
        if (lastScrapedData.title) {
            markdown += `# ${lastScrapedData.title}\n\n`;
        }
        if (lastScrapedData.description) {
            markdown += `> ${lastScrapedData.description}\n\n`;
        }
        markdown += `**Source:** ${lastScrapedUrl}\n`;
        markdown += `**Scraped:** ${new Date().toISOString()}\n\n`;
        markdown += `---\n\n`;
    }
    markdown += lastScrapedContent;

    const blob = new Blob([markdown], { type: 'text/markdown' });
    const downloadUrl = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = downloadUrl;
    a.download = `${filename}-${Date.now()}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(downloadUrl);
}

/**
 * Main scraping function using Jina AI Reader API
 */
async function startScraping() {
    const url = urlInput.value.trim();

    // Validate URL
    if (!url) {
        showError('Please enter a URL to scrape');
        return;
    }

    if (!isValidUrl(url)) {
        showError('Please enter a valid URL (including http:// or https://)');
        return;
    }

    // Reset UI
    hideError();
    resultsContainer.style.display = 'none';
    setLoading(true);
    updateProgress(10, 'Initializing scraper...');

    try {
        updateProgress(30, 'Connecting to Jina Reader API...');

        const jinaUrl = `https://r.jina.ai/${url}`;

        updateProgress(50, 'Extracting content...');

        const response = await fetch(jinaUrl, {
            method: 'GET',
            headers: {
                'Accept': 'application/json'
            }
        });

        updateProgress(80, 'Processing response...');

        if (!response.ok) {
            throw new Error(`Failed to scrape: ${response.status} ${response.statusText}`);
        }

        // Parse JSON response
        const responseText = await response.text();
        let data;

        try {
            data = JSON.parse(responseText);
            // Handle nested data structure
            if (data.data) {
                data = data.data;
            }
        } catch (e) {
            // If not JSON, treat as plain text
            data = {
                content: responseText,
                url: url
            };
        }

        if (!data.content || data.content.trim().length === 0) {
            throw new Error('No content extracted from the page');
        }

        updateProgress(100, 'Complete!');

        // Show results with formatted display
        setTimeout(() => {
            progressContainer.style.display = 'none';
            showResults(data, url);
            setLoading(false);
        }, 500);

    } catch (error) {
        console.error('Scraping error:', error);
        progressContainer.style.display = 'none';
        showError(error.message || 'Failed to scrape the website. Please try again.');
        setLoading(false);
    }
}

// Console message
console.log(`
🕷️ Web Scraper v2.0
━━━━━━━━━━━━━━━━━━━
Built with ❤️ using Jina AI Reader API

Features:
- Beautiful formatted output
- Metadata extraction
- Copy & Download support

Happy scraping! 🚀
`);
