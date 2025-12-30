#!/usr/bin/env python3

import re
import os
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import unicodedata
import socket
import subprocess

# Terminal color codes
class Colors:
    BrightRed = "\033[1;91m"
    BrightGreen = "\033[1;92m"
    BrightYellow = "\033[1;93m"
    BrightWhite = "\033[1;97m"
    Cyan = "\033[1;96m"
    BrightBlue = "\033[1;94m"
    BrightMagenta = "\033[1;95m"
    Reset = "\033[0m"

# Display tool banner
def display_banner():
    os.system("clear")
    print(f"{Colors.BrightRed}")
    print(r"""
██╗    ██╗███████╗██████╗ ███████╗██╗   ██╗████████╗███████╗
██║    ██║██╔════╝██╔══██╗╚══███╔╝╚██╗ ██╔╝╚══██╔══╝██╔════╝
██║ █╗ ██║█████╗  ██████╔╝  ███╔╝  ╚████╔╝    ██║   █████╗  
██║███╗██║██╔══╝  ██╔══██╗ ███╔╝    ╚██╔╝     ██║   ██╔══╝  
╚███╔███╔╝███████╗██████╔╝███████╗   ██║      ██║   ███████╗
 ╚══╝╚══╝ ╚══════╝╚═════╝ ╚══════╝   ╚═╝      ╚═╝   ╚══════╝
                Advanced OSINT Web Data Tool
                                                  Developer: MEH         
                                                                  
                          """)
    print(f"{Colors.Cyan}* OSINT Tool for Site Extraction: Emails, Phones, Links, Subdomains, WHOIS {Colors.Reset}")
    print(f"{Colors.BrightYellow}* YouTube-Mastersinethiclhacking WhatsApp-Mastersinethiclhacking !{Colors.Reset}\n")
    # Add some colorful flair
    print(f"{Colors.BrightMagenta}======================================================{Colors.Reset}")
    print(f"{Colors.BrightBlue}Ready to extract intelligence from your target site?{Colors.Reset}")
    print(f"{Colors.BrightMagenta}======================================================{Colors.Reset}\n")

# Check internet connectivity
def check_connection():
    print(f"{Colors.BrightWhite}[{Colors.BrightRed}!{Colors.BrightWhite}] {Colors.BrightRed}Checking internet connection...{Colors.Reset}")
    try:
        requests.get("http://google.com", timeout=10)
        print(f"{Colors.BrightWhite}[{Colors.BrightYellow}*{Colors.BrightWhite}] {Colors.BrightYellow}Connected to the internet.{Colors.Reset}")
    except requests.ConnectionError:
        print(f"{Colors.BrightWhite}[{Colors.BrightRed}!{Colors.BrightWhite}] {Colors.BrightRed}No internet connection detected. Try again later.{Colors.Reset}")
        sys.exit(1)

# URL format validation
def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def clean_text(text):
    text = re.sub(r'[\u200b\u200c\u200d\u200e\u200f\uFEFF]', '', text)
    text = text.replace('\u2024', '.').replace('\u2027', '.')
    text = unicodedata.normalize("NFKC", text)
    return text

# Email extraction using regex
def scrape_emails(text, html):
    text = clean_text(text)
    email_pattern = re.compile(r'[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}', re.IGNORECASE)
    emails = set(email_pattern.findall(text)) | set(email_pattern.findall(html))
    blocked_ext = ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.bmp', '.ico')
    emails = {e for e in emails if not e.lower().endswith(blocked_ext)}
    return list(emails)

# Phone number extraction 
def scrape_phone_numbers(text):
    phone_pattern = re.compile(r'(\+?\d{1,3})?[\s\-\.]?\(?\d{2,4}\)?[\s\-\.]?\d{3,5}[\s\-\.]?\d{3,5}')
    phone_numbers = [match.group().strip() for match in re.finditer(phone_pattern, text) if len(match.group().strip()) >= 7]
    return list(set(phone_numbers))  # Remove duplicates

# Link extraction using regex (links with and without query parameters)
def scrape_links(text):
    link_pattern = re.compile(r'https?://[^\s"\']+', re.IGNORECASE)
    return list(set(link_pattern.findall(text)))

# Subdomain enumeration
def get_subdomains(domain):
    common_subs = [
        'www', 'mail', 'ftp', 'localhost', 'webmail', 'smtp', 'pop', 'ns1', 'webdisk', 'staging',
        'test', 'dev', 'shop', 'blog', 'api', 'forum', 'news', 'vpn', 'ns2', 'store', 'secure',
        'server', 'mx', 'email', 'cloud', 'app', 'web', 'demo', 'portal', 'admin', 'beta', 'info',
        'support', 'cdn', 'docs', 'wiki', 'images', 'assets', 'static', 'login', 'auth'
    ]
    subdomains = []
    for sub in common_subs:
        try:
            host = f"{sub}.{domain}"
            socket.gethostbyname(host)
            subdomains.append(host)
        except socket.gaierror:
            pass
    return subdomains

# Advanced WHOIS lookup using system whois command
def get_whois(domain):
    try:
        result = subprocess.check_output(['whois', domain], timeout=10)
        return result.decode('utf-8').strip()
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return "Error: WHOIS command not found or failed. Ensure 'whois' is installed on your system."

# Main scraping logic
def scrape_website(url, scrape_em, scrape_ph, scrape_ln, scrape_sub, scrape_whois):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        }
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()

        soup = BeautifulSoup(res.text, 'html.parser')
        text = clean_text(soup.get_text())
        html = clean_text(res.text)
        results = {}
        domain = urlparse(url).netloc

        if scrape_em:
            emails = scrape_emails(text, html)
            results['emails'] = emails
            print(f"\n{Colors.BrightYellow}[+] Emails Found:{Colors.Reset}")
            print("\n".join(emails) if emails else "None")

        if scrape_ph:
            phones = scrape_phone_numbers(text)
            results['phones'] = phones
            print(f"\n{Colors.BrightYellow}[+] Phone Numbers Found:{Colors.Reset}")
            print("\n".join(phones) if phones else "None")

        if scrape_ln:
            links = scrape_links(html)
            results['links'] = links
            print(f"\n{Colors.BrightYellow}[+] Links Found:{Colors.Reset}")
            print("\n".join(links) if links else "None")

        if scrape_sub:
            subdomains = get_subdomains(domain)
            results['subdomains'] = subdomains
            print(f"\n{Colors.BrightYellow}[+] Subdomains Found:{Colors.Reset}")
            print("\n".join(subdomains) if subdomains else "None")

        if scrape_whois:
            whois_info = get_whois(domain)
            results['whois'] = whois_info
            print(f"\n{Colors.BrightYellow}[+] Advanced WHOIS Information:{Colors.Reset}")
            print(whois_info if whois_info else "None")

        return results

    except requests.exceptions.RequestException as err:
        print(f"{Colors.BrightRed}[!] Error: {err}{Colors.Reset}")
        return {}

# Save extracted results
def save_results(results, folder):
    try:
        os.makedirs(folder, exist_ok=True)
        if results.get('emails'):
            with open(os.path.join(folder, 'emails.txt'), 'w') as f:
                f.write("\n".join(results['emails']))
        if results.get('phones'):
            with open(os.path.join(folder, 'phones.txt'), 'w') as f:
                f.write("\n".join(results['phones']))
        if results.get('links'):
            with open(os.path.join(folder, 'links.txt'), 'w') as f:
                f.write("\n".join(results['links']))
        if results.get('subdomains'):
            with open(os.path.join(folder, 'subdomains.txt'), 'w') as f:
                f.write("\n".join(results['subdomains']))
        if results.get('whois'):
            with open(os.path.join(folder, 'whois.txt'), 'w') as f:
                f.write(results['whois'])
        print(f"{Colors.BrightGreen}[+] Results saved in '{folder}'{Colors.Reset}")
    except Exception as e:
        print(f"{Colors.BrightRed}[!] Failed to save results: {e}{Colors.Reset}")

# Main function with user interaction
def main():
    display_banner()
    check_connection()

    while True:
        url = input(f"{Colors.BrightGreen}[+] Enter a valid URL: {Colors.Reset}").strip()
        if is_valid_url(url):
            break
        print(f"{Colors.BrightRed}[!] Invalid URL. Try again.{Colors.Reset}")

    scrape_em = input(f"{Colors.BrightYellow}[?] Scrape emails? (y/n): {Colors.Reset}").lower() == 'y'
    scrape_ph = input(f"{Colors.BrightYellow}[?] Scrape phone numbers? (y/n): {Colors.Reset}").lower() == 'y'
    scrape_ln = input(f"{Colors.BrightYellow}[?] Scrape links? (y/n): {Colors.Reset}").lower() == 'y'
    scrape_sub = input(f"{Colors.BrightYellow}[?] Enumerate subdomains? (y/n): {Colors.Reset}").lower() == 'y'
    scrape_whois = input(f"{Colors.BrightYellow}[?] Perform advanced WHOIS? (y/n): {Colors.Reset}").lower() == 'y'

    if not any([scrape_em, scrape_ph, scrape_ln, scrape_sub, scrape_whois]):
        print(f"{Colors.BrightRed}[!] No options selected. Exiting...{Colors.Reset}")
        sys.exit(0)

    results = scrape_website(url, scrape_em, scrape_ph, scrape_ln, scrape_sub, scrape_whois)

    if any(results.values()):
        if input(f"{Colors.BrightGreen}[?] Save results to folder? (y/n): {Colors.Reset}").lower() == 'y':
            while True:
                folder = input(f"{Colors.BrightGreen}[+] Enter folder name: {Colors.Reset}").strip()
                if folder:
                    save_results(results, folder)
                    break
                print(f"{Colors.BrightRed}[!] Folder name cannot be empty.{Colors.Reset}")

    print(f"{Colors.BrightRed}[*] Exiting...{Colors.Reset}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"{Colors.BrightRed} User Aborted {Colors.Reset}");
        sys.exit()