#!/usr/bin/env python3
"""
Facebook Auto React Tool - Fixed Version
Working with latest FB API and supports all post formats
"""

import requests
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from urllib.parse import urlparse, parse_qs

class FBAutoReact:
    def __init__(self, cookie):
        self.cookie = cookie.strip()
        self.session = requests.Session()
        self.user_id = self.extract_user_id()
        self.fb_dtsg = None
        self.jazoest = None
        self.lsd = None
        self.revision = None
        
        self.session.headers.update({
            'authority': 'www.facebook.com',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://www.facebook.com',
            'referer': 'https://www.facebook.com/',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'cookie': self.cookie,
            'x-fb-friendly-name': 'CometUFIFeedbackReactMutation',
            'x-fb-lsd': ''
        })
        
        self.initialized = self.get_payload()
    
    def extract_user_id(self):
        """Extract user ID from cookie"""
        try:
            if 'c_user=' in self.cookie:
                return self.cookie.split('c_user=')[1].split(';')[0]
        except:
            pass
        return None
    
    def get_payload(self):
        """Get payload data (fb_dtsg, jazoest, revision)"""
        if not self.user_id:
            return False
        
        try:
            # Method 1: Get from ajax/dtsg endpoint
            response = self.session.get(
                'https://www.facebook.com/ajax/dtsg/?__a=1',
                timeout=15
            )
            
            if response.status_code == 200:
                text = response.text
                
                # Remove for(;;); prefix
                if 'for (;;);' in text:
                    text = text.replace('for (;;);', '')
                
                try:
                    data = json.loads(text)
                    
                    # Extract token from payload
                    if 'payload' in data and 'token' in data['payload']:
                        self.fb_dtsg = data['payload']['token']
                    
                    # Try alternative paths
                    if not self.fb_dtsg and 'require' in data:
                        for item in data.get('require', []):
                            if isinstance(item, list):
                                for subitem in item:
                                    if isinstance(subitem, dict) and 'token' in subitem:
                                        self.fb_dtsg = subitem['token']
                                        break
                
                except json.JSONDecodeError:
                    pass
            
            # Method 2: Get from main page if Method 1 fails
            if not self.fb_dtsg:
                response = self.session.get('https://www.facebook.com/', timeout=15)
                html = response.text
                
                # Multiple patterns to find fb_dtsg
                patterns = [
                    r'"DTSGInitialData",\[\],{"token":"([^"]+)"',
                    r'"token":"([^"]+)","async_get_token"',
                    r'\["DTSGInitData",\[\],{"token":"([^"]+)"',
                    r'{"name":"fb_dtsg","value":"([^"]+)"'
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, html)
                    if match:
                        self.fb_dtsg = match.group(1)
                        break
                
                # Extract LSD
                lsd_match = re.search(r'"LSD",\[\],{"token":"([^"]+)"', html)
                if lsd_match:
                    self.lsd = lsd_match.group(1)
                
                # Extract revision
                rev_match = re.search(r'"client_revision":(\d+)', html)
                if rev_match:
                    self.revision = rev_match.group(1)
            
            # Generate jazoest from user_id
            if self.user_id:
                self.jazoest = '2' + str(sum(ord(c) for c in self.user_id))
            
            # Update LSD header
            if self.lsd:
                self.session.headers['x-fb-lsd'] = self.lsd
            
            return bool(self.fb_dtsg and self.user_id)
            
        except Exception as e:
            print(f"[!] Payload error: {str(e)}")
            return False
    
    def extract_post_id_from_url(self, url):
        """Extract story_fbid and id from Facebook URL"""
        try:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            
            # Handle different URL formats
            if 'story_fbid' in params and 'id' in params:
                story_fbid = params['story_fbid'][0]
                page_id = params['id'][0]
                return f"{page_id}_{story_fbid}"
            
            # Handle /posts/ format
            if '/posts/' in url:
                post_id = url.split('/posts/')[1].split('/')[0].split('?')[0]
                return post_id
            
            # Handle pfbid format
            if 'pfbid' in url:
                match = re.search(r'pfbid\w+', url)
                if match:
                    return match.group(0)
            
            # Handle direct ID format
            match = re.search(r'(\d{15,})', url)
            if match:
                return match.group(1)
            
        except:
            pass
        
        return url
    
    def react_to_post(self, post_id, reaction_type='LIKE'):
        """React to Facebook post"""
        
        reaction_map = {
            'LIKE': '1635855486666999',
            'LOVE': '1678524932434102',
            'CARE': '613557422527858',
            'HAHA': '115940658764963',
            'WOW': '478547315650144',
            'SAD': '908563459236466',
            'ANGRY': '444813342392137'
        }
        
        reaction_id = reaction_map.get(reaction_type.upper(), reaction_map['LIKE'])
        
        # Build variables for GraphQL
        variables = {
            "input": {
                "attribution_id_v2": f"CometSinglePostRoot.react_relay,comet.single_post.generic,via_cold_start,{int(time.time())},100000,190055527696468,,",
                "feedback_id": post_id,
                "feedback_reaction_id": reaction_id,
                "feedback_source": "OBJECT",
                "is_tracking_encrypted": False,
                "tracking": [],
                "session_id": str(int(time.time() * 1000)),
                "actor_id": self.user_id,
                "client_mutation_id": str(int(time.time() * 1000))
            }
        }
        
        payload = {
            'av': self.user_id,
            '__user': self.user_id,
            '__a': '1',
            '__req': 'h',
            '__hs': str(int(time.time())),
            'dpr': '1',
            '__ccg': 'EXCELLENT',
            '__rev': self.revision or '1007797763',
            '__s': '',
            '__hsi': '',
            '__dyn': '',
            '__csr': '',
            'fb_dtsg': self.fb_dtsg,
            'jazoest': self.jazoest,
            'fb_api_caller_class': 'RelayModern',
            'fb_api_req_friendly_name': 'CometUFIFeedbackReactMutation',
            'variables': json.dumps(variables),
            'server_timestamps': 'true',
            'doc_id': '6360991980619959'
        }
        
        if self.lsd:
            payload['lsd'] = self.lsd
        
        try:
            response = self.session.post(
                'https://www.facebook.com/api/graphql/',
                data=payload,
                timeout=20
            )
            
            if response.status_code == 200:
                text = response.text
                
                # Remove for(;;); if present
                if 'for (;;);' in text:
                    text = text.replace('for (;;);', '')
                
                try:
                    result = json.loads(text)
                    
                    # Check for errors
                    if 'errors' in result:
                        error_msg = result['errors'][0].get('message', 'Unknown error')
                        
                        # Check for scraping detection
                        if 'scraping' in error_msg.lower():
                            return False, "Scraping detected - Try again later"
                        
                        return False, f"Error: {error_msg}"
                    
                    # Check for successful reaction
                    if 'data' in result:
                        return True, f"✓ Reacted with {reaction_type}"
                    
                    return True, "Reaction sent"
                    
                except json.JSONDecodeError:
                    # Sometimes successful reactions don't return JSON
                    if response.status_code == 200:
                        return True, f"✓ Reacted with {reaction_type}"
                    return False, "Invalid response"
            else:
                return False, f"HTTP {response.status_code}"
                
        except requests.exceptions.Timeout:
            return False, "Timeout"
        except Exception as e:
            return False, f"Error: {str(e)[:50]}"

def worker(cookie, post_id, reaction_type, thread_id):
    """Worker function for threading"""
    try:
        fb = FBAutoReact(cookie)
        
        if not fb.user_id:
            return thread_id, False, f"[{thread_id}] Invalid cookie"
        
        if not fb.initialized:
            return thread_id, False, f"[{thread_id}] [{fb.user_id}] Failed to get tokens"
        
        # React to post
        success, message = fb.react_to_post(post_id, reaction_type)
        
        status = f"[{thread_id}] [{fb.user_id}] {message}"
        return thread_id, success, status
        
    except Exception as e:
        return thread_id, False, f"[{thread_id}] Error: {str(e)[:80]}"

def banner():
    print("""
╔════════════════════════════════════════════╗
║     FB Auto React - Fixed Version         ║
║     Latest API with Payload Support       ║
╚════════════════════════════════════════════╝
    """)

def extract_post_id(url_or_id):
    """Extract post ID from various formats"""
    url_or_id = url_or_id.strip()
    
    # Already a post ID
    if url_or_id.isdigit() or '_' in url_or_id:
        return url_or_id
    
    # Parse URL
    try:
        parsed = urlparse(url_or_id)
        params = parse_qs(parsed.query)
        
        # Format: ?story_fbid=X&id=Y
        if 'story_fbid' in params and 'id' in params:
            story_fbid = params['story_fbid'][0]
            page_id = params['id'][0]
            return f"{page_id}_{story_fbid}"
        
        # Format: /posts/X
        if '/posts/' in url_or_id:
            match = re.search(r'/posts/([^/?]+)', url_or_id)
            if match:
                return match.group(1)
        
        # Format: pfbid...
        if 'pfbid' in url_or_id:
            match = re.search(r'pfbid[\w]+', url_or_id)
            if match:
                return match.group(0)
        
        # Try to find any long number
        match = re.search(r'(\d{15,})', url_or_id)
        if match:
            return match.group(1)
    
    except:
        pass
    
    return url_or_id

def get_cookies():
    """Get cookies from user"""
    print("\n[*] Enter cookies (one per line, empty line to finish):")
    print("[*] Format: datr=xxx;sb=xxx;c_user=xxx;xs=xxx")
    print()
    
    cookies = []
    while True:
        cookie = input(f"Cookie #{len(cookies)+1}: ").strip()
        if not cookie:
            if cookies:
                break
            else:
                continue
        
        if 'c_user=' not in cookie:
            print("[!] Invalid cookie - must contain c_user")
            continue
        
        cookies.append(cookie)
        print(f"[+] Added!")
    
    return cookies

def main():
    banner()
    
    # Get cookies
    cookies = get_cookies()
    
    if not cookies:
        print("[!] No cookies provided!")
        return
    
    print(f"\n[+] Loaded {len(cookies)} cookie(s)")
    
    # Get post
    print("\n[*] Paste Facebook post URL or ID:")
    print("   Example: https://www.facebook.com/61569634753113/posts/pfbid02S5uMn/")
    post_input = input("\n[?] Post: ").strip()
    
    if not post_input:
        print("[!] Post required!")
        return
    
    post_id = extract_post_id(post_input)
    print(f"[+] Post ID: {post_id}")
    
    # Reaction selection
    print("\n[*] Reactions:")
    print("1.👍 LIKE  2.❤️ LOVE  3.🤗 CARE  4.😂 HAHA")
    print("5.😮 WOW   6.😢 SAD   7.😡 ANGRY")
    
    choice = input("\n[?] Select (1-7): ").strip() or '1'
    reactions = {
        '1': 'LIKE', '2': 'LOVE', '3': 'CARE',
        '4': 'HAHA', '5': 'WOW', '6': 'SAD', '7': 'ANGRY'
    }
    reaction = reactions.get(choice, 'LIKE')
    
    # Threading
    threads = input("[?] Threads (1-10): ").strip() or '5'
    threads = min(int(threads), 10)
    
    print("\n" + "="*50)
    print(f"[+] Starting...")
    print(f"[+] Post: {post_id}")
    print(f"[+] Reaction: {reaction}")
    print(f"[+] Accounts: {len(cookies)}")
    print(f"[+] Threads: {threads}")
    print("="*50 + "\n")
    
    success = 0
    failed = 0
    
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [
            executor.submit(worker, cookie, post_id, reaction, i)
            for i, cookie in enumerate(cookies, 1)
        ]
        
        for future in as_completed(futures):
            tid, ok, msg = future.result()
            print(msg)
            
            if ok:
                success += 1
            else:
                failed += 1
    
    print("\n" + "="*50)
    print(f"✓ Success: {success}")
    print(f"✗ Failed: {failed}")
    print(f"Total: {len(cookies)}")
    print("="*50)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Stopped by user")
    except Exception as e:
        print(f"\n[!] Error: {str(e)}")
