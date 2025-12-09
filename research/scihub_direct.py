#!/usr/bin/env python3
"""
Direct Sci-Hub download using POST request
"""
import requests

OUTPUT_DIR = "F:/UnderCurrentAppPaxum/research/articles"
SCIHUB_URL = "https://sci-hub.se/"

# Article to download
doi = "10.1016/j.autneu.2007.08.002"
filename = "16_PMID_17851136.pdf"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# POST request to Sci-Hub
print(f"Sending POST request to Sci-Hub with DOI: {doi}")
response = requests.post(SCIHUB_URL, data={'request': doi}, headers=headers, timeout=30, allow_redirects=True)

print(f"Response status: {response.status_code}")
print(f"Content type: {response.headers.get('Content-Type', 'unknown')}")

# Check if we got a PDF directly
if response.content[:4] == b'%PDF':
    output_path = f"{OUTPUT_DIR}/{filename}"
    with open(output_path, 'wb') as f:
        f.write(response.content)
    print(f"SUCCESS! PDF saved to {output_path}")
    print(f"File size: {len(response.content)} bytes")
else:
    # We got HTML, need to find the PDF link
    import re
    html = response.text

    # Look for PDF URL patterns
    patterns = [
        r'location\.href\s*=\s*["\']([^"\']+)["\']',
        r'<iframe[^>]+src=["\']([^"\']+\.pdf[^"\']*)["\']',
        r'<embed[^>]+src=["\']([^"\']+\.pdf[^"\']*)["\']',
        r'href=["\']([^"\']*\.pdf[^"\']*)["\']',
        r'(https?://[^\s<>"]+\.pdf[^\s<>"]*)',
    ]

    pdf_url = None
    for pattern in patterns:
        matches = re.findall(pattern, html, re.IGNORECASE)
        if matches:
            pdf_url = matches[0]
            break

    if pdf_url:
        print(f"Found PDF URL: {pdf_url}")

        # Handle protocol-relative URLs
        if pdf_url.startswith('//'):
            pdf_url = 'https:' + pdf_url
        elif not pdf_url.startswith('http'):
            pdf_url = 'https://sci-hub.se' + pdf_url

        # Download the PDF
        print(f"Downloading from: {pdf_url}")
        pdf_response = requests.get(pdf_url, headers=headers, timeout=30)

        if pdf_response.content[:4] == b'%PDF':
            output_path = f"{OUTPUT_DIR}/{filename}"
            with open(output_path, 'wb') as f:
                f.write(pdf_response.content)
            print(f"SUCCESS! PDF saved to {output_path}")
            print(f"File size: {len(pdf_response.content)} bytes")
        else:
            print("ERROR: Downloaded file is not a PDF")
    else:
        print("ERROR: Could not find PDF URL in response")
        # Save HTML for debugging
        with open(f"{OUTPUT_DIR}/debug_response.html", 'w', encoding='utf-8') as f:
            f.write(html[:5000])  # First 5000 chars
        print("Saved first 5000 chars of response to debug_response.html")
