#!/usr/bin/env python3
"""
Download research articles from URLs and try sci-hub as fallback
"""
import os
import re
import time
import requests
from pathlib import Path
from urllib.parse import urlparse, quote

# Configuration
URLS_FILE = "F:/UnderCurrentAppPaxum/urls.txt"
OUTPUT_DIR = "F:/UnderCurrentAppPaxum/research/articles"
SCIHUB_URL = "https://sci-hub.se/"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def clean_filename(url, index):
    """Generate a clean filename from URL"""
    # Extract DOI or PubMed ID if available
    if 'pubmed.ncbi.nlm.nih.gov' in url:
        match = re.search(r'/(\d+)', url)
        if match:
            return f"{index:02d}_PMID_{match.group(1)}.pdf"
    elif 'doi.org' in url or 'doi' in url:
        match = re.search(r'10\.\d{4,}/[^\s]+', url)
        if match:
            doi = match.group(0).replace('/', '_')
            return f"{index:02d}_DOI_{doi}.pdf"
    elif 'nature.com/articles' in url:
        match = re.search(r'/articles/([^?#]+)', url)
        if match:
            return f"{index:02d}_Nature_{match.group(1)}.pdf"
    elif 'arxiv.org' in url:
        match = re.search(r'(\d+\.\d+)', url)
        if match:
            return f"{index:02d}_arXiv_{match.group(1)}.pdf"

    # Generic fallback
    domain = urlparse(url).netloc.replace('www.', '')
    return f"{index:02d}_{domain[:30]}.pdf"

def try_direct_download(url, output_path):
    """Try to download PDF directly from the source"""
    try:
        print(f"  Trying direct download...")
        response = requests.get(url, headers=HEADERS, timeout=30, allow_redirects=True)

        # Check if response is a PDF
        content_type = response.headers.get('Content-Type', '')
        if 'application/pdf' in content_type or response.content[:4] == b'%PDF':
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return True

        # Some sites serve HTML with PDF links
        if 'text/html' in content_type:
            # Look for PDF links in the HTML
            html = response.text
            pdf_patterns = [
                r'href="([^"]+\.pdf[^"]*)"',
                r'content="([^"]+\.pdf[^"]*)"',
                r'(https?://[^\s<>"]+\.pdf)'
            ]

            for pattern in pdf_patterns:
                matches = re.findall(pattern, html, re.IGNORECASE)
                if matches:
                    # Try the first PDF link found
                    pdf_url = matches[0]
                    if not pdf_url.startswith('http'):
                        base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
                        pdf_url = base_url + pdf_url if pdf_url.startswith('/') else base_url + '/' + pdf_url

                    print(f"  Found PDF link: {pdf_url}")
                    pdf_response = requests.get(pdf_url, headers=HEADERS, timeout=30)
                    if pdf_response.content[:4] == b'%PDF':
                        with open(output_path, 'wb') as f:
                            f.write(pdf_response.content)
                        return True

        return False
    except Exception as e:
        print(f"  Direct download failed: {e}")
        return False

def try_scihub_download(url, output_path):
    """Try to download via Sci-Hub"""
    try:
        print(f"  Trying Sci-Hub...")
        scihub_search = f"{SCIHUB_URL}{quote(url)}"
        response = requests.get(scihub_search, headers=HEADERS, timeout=30, allow_redirects=True)

        # Sci-Hub typically redirects to the PDF or embeds it
        if response.content[:4] == b'%PDF':
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return True

        # Look for PDF link in Sci-Hub page
        html = response.text
        pdf_patterns = [
            r'location\.href=\'([^\']+\.pdf[^\']*)\'',
            r'href="([^"]*\.pdf[^"]*)"',
            r'(https?://[^\s<>"]+\.pdf[^\s<>"]*)'
        ]

        for pattern in pdf_patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            if matches:
                pdf_url = matches[0]
                if not pdf_url.startswith('http'):
                    pdf_url = 'https:' + pdf_url if pdf_url.startswith('//') else SCIHUB_URL + pdf_url

                print(f"  Found Sci-Hub PDF: {pdf_url}")
                pdf_response = requests.get(pdf_url, headers=HEADERS, timeout=30)
                if pdf_response.content[:4] == b'%PDF':
                    with open(output_path, 'wb') as f:
                        f.write(pdf_response.content)
                    return True

        return False
    except Exception as e:
        print(f"  Sci-Hub download failed: {e}")
        return False

def download_articles():
    """Main function to download all articles"""
    # Create output directory
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    # Read URLs
    with open(URLS_FILE, 'r') as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    print(f"Found {len(urls)} URLs to process\n")

    results = {
        'success': [],
        'failed': []
    }

    for idx, url in enumerate(urls, 1):
        filename = clean_filename(url, idx)
        output_path = os.path.join(OUTPUT_DIR, filename)

        # Skip if already downloaded
        if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
            print(f"[{idx}/{len(urls)}] SKIP: {filename} (already exists)")
            results['success'].append((url, filename))
            continue

        print(f"[{idx}/{len(urls)}] Downloading: {url}")
        print(f"  Output: {filename}")

        # Try direct download first
        if try_direct_download(url, output_path):
            print(f"  [OK] Success (direct)\n")
            results['success'].append((url, filename))
            time.sleep(2)  # Be polite
            continue

        # Try Sci-Hub as fallback
        if try_scihub_download(url, output_path):
            print(f"  [OK] Success (Sci-Hub)\n")
            results['success'].append((url, filename))
            time.sleep(3)  # Be extra polite to Sci-Hub
            continue

        # Both methods failed
        print(f"  [FAIL] Failed\n")
        results['failed'].append((url, filename))
        time.sleep(1)

    # Print summary
    print("\n" + "="*60)
    print("DOWNLOAD SUMMARY")
    print("="*60)
    print(f"Total URLs: {len(urls)}")
    print(f"Successfully downloaded: {len(results['success'])}")
    print(f"Failed: {len(results['failed'])}")

    if results['failed']:
        print("\nFailed downloads:")
        for url, filename in results['failed']:
            print(f"  - {filename}")
            print(f"    {url}")

    # Save results log
    log_path = os.path.join(OUTPUT_DIR, "_download_log.txt")
    with open(log_path, 'w') as f:
        f.write("DOWNLOAD LOG\n")
        f.write("="*60 + "\n\n")
        f.write("SUCCESSFUL:\n")
        for url, filename in results['success']:
            f.write(f"{filename}\n  {url}\n\n")
        f.write("\nFAILED:\n")
        for url, filename in results['failed']:
            f.write(f"{filename}\n  {url}\n\n")

    print(f"\nLog saved to: {log_path}")

if __name__ == "__main__":
    download_articles()
