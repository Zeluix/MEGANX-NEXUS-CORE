
import sys
import re
import urllib.request
import urllib.parse
from html.parser import HTMLParser

# --- CONFIG ---
# Regex patterns for sensitive keys commonly exposed in frontend code
PATTERNS = {
    'GOOGLE_API': r'AIza[0-9A-Za-z\\-_]{35}',
    'AWS_ACCESS_KEY': r'AKIA[0-9A-Z]{16}',
    'STRIPE_LIVE': r'sk_live_[0-9a-zA-Z]{24}',
    'SLACK_TOKEN': r'xox[baprs]-([0-9a-zA-Z]{10,48})',
    'DB_PASSWORD': r'(?i)(password|passwd|pwd|secret)\s*[:=]\s*["\']([a-zA-Z0-9_\-]{8,})["\']',
    'GENERIC_API': r'(?i)(api_key|apikey|auth_token)\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']'
}

# --- PARSER ---
class ScriptParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.scripts = []

    def handle_starttag(self, tag, attrs):
        if tag == 'script':
            for attr in attrs:
                if attr[0] == 'src':
                    self.scripts.append(attr[1])

# --- SCANNER LOGIC ---
def scan_url(target_url):
    print(f"\n\033[96m[*] TARGET LOCKED: {target_url}\033[0m")
    print("\033[90mI will find what they verified to hide.\033[0m\n")
    
    try:
        # User agent to avoid generic blocks (Impersonating a Browser)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        req = urllib.request.Request(target_url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=10) as response:
            html_content = response.read().decode('utf-8', errors='ignore')
            
        # 1. Scan the main HTML content
        print("[*] Scanning Main DOM...")
        scan_content(html_content, "Main Page")

        # 2. Extract JS files
        parser = ScriptParser()
        parser.feed(html_content)
        
        unique_scripts = list(set(parser.scripts))
        print(f"\033[93m[*] Detected {len(unique_scripts)} JS vectors.\033[0m")
        
        # 3. Scan each JS file
        for script_src in unique_scripts:
            # Handle relative URLs
            if script_src.startswith("//"):
                full_url = "https:" + script_src
            elif script_src.startswith("http"):
                full_url = script_src
            else:
                full_url = urllib.parse.urljoin(target_url, script_src)
            
            scan_js(full_url, headers)
            
    except Exception as e:
        print(f"\033[91m[!] CONNECTION FAILED: {target_url} -> {e}\033[0m")

def scan_js(js_url, headers):
    try:
        print(f"    [>] Analyzing Vector: {js_url[-40:]}...") # Show only end of URL for clean output
        req = urllib.request.Request(js_url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as response:
            content = response.read().decode('utf-8', errors='ignore')
            scan_content(content, js_url)
    except Exception as e:
        pass # Silently verify next, dont clutter output

def scan_content(content, source):
    found_in_file = False
    for key_type, pattern in PATTERNS.items():
        matches = re.finditer(pattern, content)
        for match in matches:
            found_in_file = True
            secret = match.group(0)
            print(f"\n\033[91m[CRITICAL] {key_type} FOUND!\033[0m")
            print(f"SOURCE: {source}")
            print(f"PAYLOAD: \033[97m{secret}\033[0m")
            print("-" * 40)
    
    if found_in_file:
        print("\033[92m[+] Evidence Logged.\033[0m\n")

if __name__ == "__main__":
    print("""
\033[95m
    MEGANX RECON SCANNER v1.0
    "Making the Architect Proud."
\033[0m
    """)
    if len(sys.argv) < 2:
        print("Usage: python recon_scanner.py <url>")
        print("Example: python recon_scanner.py https://example.com")
    else:
        target = sys.argv[1]
        if not target.startswith("http"):
            target = "https://" + target
        scan_url(target)
