
## What is a URL?

A **Uniform Resource Locator (URL)** is the address used to access resources on the internet. It consists of multiple parts that define how and where the resource is located.

### URL Structure Example:

```
https://support.example.com/docs/tutorial.html
```

- `https://` - Protocol
    
- `support.` - Subdomain
    
- `example.com` - Domain name
    
- `/docs/tutorial.html` - Path (file location on the server)
    

## Protocols: HTTP vs. HTTPS

- **HTTP (HyperText Transfer Protocol)**: Standard protocol for transferring web pages.
    
- **HTTPS (HyperText Transfer Protocol Secure)**: Secure version using encryption (TLS/SSL) to protect data.
    
- Always prefer **HTTPS** for security reasons.
    

## Subdomains

Subdomains are prefixes to the main domain, often used for different services:

- `mail.example.com` - Mail service
    
- `support.example.com` - Customer support
    
- `blog.example.com` - Company blog
    

## Types of Top-Level Domains (TLDs)

TLDs are the highest level in the domain name system.

### Generic TLDs (gTLDs)

Commonly used extensions:

- `.com` - Commercial
    
- `.org` - Organizations (often non-profits)
    
- `.net` - Networks
    
- `.edu` - Educational institutions
    
- `.gov` - Government agencies
    
- `.mil` - Military use
    

### Country Code TLDs (ccTLDs)

Assigned to specific countries:

- `.us` - United States
    
- `.uk` - United Kingdom
    
- `.ca` - Canada
    
- `.au` - Australia
    
- `.de` - Germany
    

### Sponsored TLDs (sTLDs)

Restricted-use domains controlled by organizations:

- `.museum` - Museums
    
- `.aero` - Aviation industry
    
- `.coop` - Cooperatives
    
- `.jobs` - Employment-related sites
    

### New TLDs

Recently introduced extensions:

- `.tech` - Technology websites
    
- `.blog` - Blogs
    
- `.app` - Applications
    
- `.xyz` - General-purpose
    
- `.guru` - Expertise-related sites
    

## How Domains Lead to Webpages

A domain name points to a server's **IP address**, which serves website files organized in a folder structure.

Example:

```
https://example.com/products/shoes/index.html
```

- `products/` - Directory (folder) on the server
    
- `shoes/` - Subdirectory
    
- `index.html` - HTML file (webpage)
    

This folder structure mirrors how files are stored on a web server, making it possible to organize and access web pages efficiently.

## What is robots.txt?

A **robots.txt** file is a text file used by websites to instruct web crawlers and search engine bots on which pages they can or cannot access. It is placed in the root directory of a website.

### Example robots.txt:

```
User-agent: *
Disallow: /private/
Allow: /public/
```

- `User-agent: *` - Applies to all web crawlers.
    
- `Disallow: /private/` - Blocks access to the `/private/` directory.
    
- `Allow: /public/` - Allows access to the `/public/` directory.
    

This file helps control how search engines index a website and prevent bots from accessing sensitive areas.