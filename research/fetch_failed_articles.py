#!/usr/bin/env python3
"""
Improved article fetcher for failed downloads
Uses PubMed API to get DOIs and metadata, then tries multiple sources
"""
import os
import re
import time
import requests
from pathlib import Path
from urllib.parse import quote
import xml.etree.ElementTree as ET

OUTPUT_DIR = "F:/UnderCurrentAppPaxum/research/articles"
SCIHUB_MIRRORS = [
    "https://sci-hub.se/",
    "https://sci-hub.st/",
    "https://sci-hub.ru/"
]
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

FAILED_URLS = [
    ("01_PMID_40806985.pdf", "https://pubmed.ncbi.nlm.nih.gov/40806985"),
    ("02_PMID_40981105.pdf", "https://pubmed.ncbi.nlm.nih.gov/40981105"),
    ("03_researchgate_hydrogen.pdf", "https://www.researchgate.net/publication/391894216"),
    ("04_researchgate_longcovid.pdf", "https://www.researchgate.net/publication/390045237"),
    ("05_PMID_34071326.pdf", "https://pubmed.ncbi.nlm.nih.gov/34071326"),
    ("06_PMID_31957647.pdf", "https://pubmed.ncbi.nlm.nih.gov/31957647"),
    ("07_PMID_31906988.pdf", "https://pubmed.ncbi.nlm.nih.gov/31906988"),
    ("09_PMID_29855991.pdf", "https://pubmed.ncbi.nlm.nih.gov/29855991"),
    ("11_PMC9183184.pdf", "https://pmc.ncbi.nlm.nih.gov/articles/PMC9183184"),
    ("12_PMID_29357332.pdf", "https://pubmed.ncbi.nlm.nih.gov/29357332"),
    ("13_PMC7053003.pdf", "https://pmc.ncbi.nlm.nih.gov/articles/PMC7053003"),
    ("14_PMID_23838093.pdf", "https://pubmed.ncbi.nlm.nih.gov/23838093"),
    ("15_PMID_20502886.pdf", "https://pubmed.ncbi.nlm.nih.gov/20502886"),
    ("16_PMID_17851136.pdf", "https://pubmed.ncbi.nlm.nih.gov/17851136"),
    ("17_PMID_9430800.pdf", "https://pubmed.ncbi.nlm.nih.gov/9430800"),
    ("21_arXiv_2404.04345.pdf", "https://arxiv.org/abs/2404.04345"),
    ("22_PMID_40190996.pdf", "https://pubmed.ncbi.nlm.nih.gov/40190996"),
    ("26_PMID_36938766.pdf", "https://pubmed.ncbi.nlm.nih.gov/36938766"),
    ("27_PMID_33168001.pdf", "https://pubmed.ncbi.nlm.nih.gov/33168001"),
    ("28_PMID_32601613.pdf", "https://pubmed.ncbi.nlm.nih.gov/32601613"),
]

def get_pubmed_doi(pmid):
    """Get DOI from PubMed ID using E-utilities API"""
    try:
        url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&retmode=xml"
        response = requests.get(url, timeout=15)
        root = ET.fromstring(response.content)

        # Extract DOI
        doi_elem = root.find(".//ArticleId[@IdType='doi']")
        if doi_elem is not None:
            return doi_elem.text
        return None
    except Exception as e:
        print(f"    Error getting DOI: {e}")
        return None

def get_pmc_pdf(pmc_id):
    """Try to get PDF from PMC"""
    try:
        pdf_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc_id}/pdf/"
        response = requests.get(pdf_url, headers=HEADERS, timeout=30, allow_redirects=True)
        if response.content[:4] == b'%PDF':
            return response.content
        return None
    except Exception as e:
        print(f"    PMC PDF error: {e}")
        return None

def try_arxiv_pdf(arxiv_id):
    """Download from arXiv"""
    try:
        # Clean arXiv ID
        arxiv_id = re.search(r'(\d+\.\d+)', arxiv_id).group(1)
        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        response = requests.get(pdf_url, headers=HEADERS, timeout=30)
        if response.content[:4] == b'%PDF':
            return response.content
        return None
    except Exception as e:
        print(f"    arXiv error: {e}")
        return None

def try_scihub_with_doi(doi):
    """Try multiple Sci-Hub mirrors with DOI"""
    for mirror in SCIHUB_MIRRORS:
        try:
            print(f"    Trying {mirror}...")
            url = f"{mirror}{doi}"
            response = requests.get(url, headers=HEADERS, timeout=30, allow_redirects=True)

            # Check if response is PDF
            if response.content[:4] == b'%PDF':
                return response.content

            # Look for PDF link in HTML
            html = response.text
            pdf_patterns = [
                r'location\.href=\'([^\']+\.pdf[^\']*)\'',
                r'href="(//[^"]*\.pdf[^"]*)"',
                r'(https?://[^\s<>"]+\.pdf[^\s<>"]*)'
            ]

            for pattern in pdf_patterns:
                matches = re.findall(pattern, html, re.IGNORECASE)
                if matches:
                    pdf_url = matches[0]
                    if pdf_url.startswith('//'):
                        pdf_url = 'https:' + pdf_url

                    pdf_response = requests.get(pdf_url, headers=HEADERS, timeout=30)
                    if pdf_response.content[:4] == b'%PDF':
                        return pdf_response.content

            time.sleep(2)
        except Exception as e:
            print(f"      {mirror} failed: {e}")
            continue

    return None

def fetch_article(filename, url):
    """Try to fetch a single article using multiple methods"""
    output_path = os.path.join(OUTPUT_DIR, filename)

    # Skip if already exists
    if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
        print(f"  SKIP: {filename} (already exists)")
        return True

    print(f"  Attempting: {filename}")
    print(f"    URL: {url}")

    # Handle PubMed articles
    if 'pubmed.ncbi.nlm.nih.gov' in url:
        pmid_match = re.search(r'/(\d+)', url)
        if pmid_match:
            pmid = pmid_match.group(1)
            print(f"    PMID: {pmid}")

            # Get DOI
            doi = get_pubmed_doi(pmid)
            if doi:
                print(f"    DOI: {doi}")

                # Try Sci-Hub with DOI
                pdf_content = try_scihub_with_doi(doi)
                if pdf_content:
                    with open(output_path, 'wb') as f:
                        f.write(pdf_content)
                    print(f"    [OK] Downloaded via Sci-Hub\n")
                    return True

    # Handle PMC articles
    elif 'pmc.ncbi.nlm.nih.gov' in url:
        pmc_match = re.search(r'PMC(\d+)', url)
        if pmc_match:
            pmc_id = f"PMC{pmc_match.group(1)}"
            print(f"    PMC ID: {pmc_id}")

            pdf_content = get_pmc_pdf(pmc_id)
            if pdf_content:
                with open(output_path, 'wb') as f:
                    f.write(pdf_content)
                print(f"    [OK] Downloaded from PMC\n")
                return True

    # Handle arXiv
    elif 'arxiv.org' in url:
        arxiv_match = re.search(r'(\d+\.\d+)', url)
        if arxiv_match:
            arxiv_id = arxiv_match.group(1)
            print(f"    arXiv ID: {arxiv_id}")

            pdf_content = try_arxiv_pdf(arxiv_id)
            if pdf_content:
                with open(output_path, 'wb') as f:
                    f.write(pdf_content)
                print(f"    [OK] Downloaded from arXiv\n")
                return True

    print(f"    [FAIL] Could not download\n")
    return False

def main():
    print(f"Attempting to fetch {len(FAILED_URLS)} failed articles...\n")

    results = {'success': 0, 'failed': 0}

    for filename, url in FAILED_URLS:
        success = fetch_article(filename, url)
        if success:
            results['success'] += 1
        else:
            results['failed'] += 1
        time.sleep(3)  # Be polite

    print("="*60)
    print("RETRY SUMMARY")
    print("="*60)
    print(f"Successfully downloaded: {results['success']}")
    print(f"Still failed: {results['failed']}")

if __name__ == "__main__":
    main()
