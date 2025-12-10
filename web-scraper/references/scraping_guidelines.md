# Web Scraping Guidelines

## Legal and Ethical Considerations

### Always Follow These Rules
1. **Respect robots.txt** - Check and obey the site's robots.txt file
2. **Implement rate limiting** - Don't overwhelm servers with requests
3. **Review terms of service** - Ensure scraping is permitted
4. **Identify your bot** - Use appropriate User-Agent headers
5. **Don't scrape personal data** - Avoid PII and sensitive information

### Best Practices
- Scrape during off-peak hours when possible
- Cache results to avoid repeated requests
- Use appropriate delays between requests (1-3 seconds minimum)
- Monitor for HTTP errors and back off when needed
- Respect copyright and fair use guidelines

### When to Avoid Scraping
- Sites that explicitly prohibit scraping in ToS
- Login-protected content without permission
- Personal or sensitive data
- High-frequency real-time data
- Paywall content

### Technical Guidelines
- Handle errors gracefully (404, 500, timeouts)
- Validate URLs before processing
- Check for CAPTCHAs and access controls
- Use appropriate headers and identify your scraper
- Implement retry logic for transient failures