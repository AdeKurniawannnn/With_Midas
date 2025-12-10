# Common Web Scraping Patterns

## Documentation Sites
**Typical structure**: Hierarchical with clear navigation
**Recommended settings**: `--depth 2 --max-pages 50 --same-domain`
**Common challenges**: Multiple related pages, version navigation
**Strategy**: Start from main documentation page, follow topic links

## Blog Platforms
**Typical structure**: Chronological with category/tag organization
**Recommended settings**: `--depth 1 --max-pages 25 --same-domain`
**Common challenges**: Pagination, related posts, comment sections
**Strategy**: Focus on article content, avoid navigation-heavy pages

## E-commerce Sites
**Typical structure**: Category → product → details hierarchy
**Recommended settings**: `--depth 2 --max-pages 100 --same-domain`
**Common challenges**: Product variants, image galleries, dynamic content
**Strategy**: Target product listing and detail pages, skip cart/checkout

## News Sites
**Typical structure**: Section-based with article links
**Recommended settings**: `--depth 1 --max-pages 30 --same-domain`
**Common challenges**: Paywalls, breaking news, multimedia content
**Strategy**: Focus on article body content, respect paywall restrictions

## Academic/Research Sites
**Typical structure**: Department → publication → details
**Recommended settings**: `--depth 2 --max-pages 40 --same-domain`
**Common challenges**: PDF links, citation networks, author pages
**Strategy**: Prioritize HTML content over PDFs when possible

## Corporate Websites
**Typical structure**: Informational with service/product pages
**Recommended settings**: `--depth 2 --max-pages 30 --same-domain`
**Common challenges**: Marketing content, dynamic JavaScript
**Strategy**: Focus on static content and service descriptions