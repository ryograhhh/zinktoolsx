#!/usr/bin/env python3
"""
Facebook Auto React Tool for Termux - Improved Version
Direct cookie input with better error handling
"""

import requests
import json
import threading
import time
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

class FBAutoReact:
    def __init__(self, cookie):
        self.cookie = cookie.strip()
        self.session = requests.Session()
        self.user_id = self.extract_user_id()
        self.fb_dtsg = None
        self.jazoest = None
        self.lsd = None
        
        # Setup session headers
        self.session.headers.update({
            'authority': 'www.facebook.com',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://www.facebook.com',
            'referer': 'https://www.facebook.com/',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Linux; Android 11; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            'cookie': self.cookie
        })
        
        # Initialize tokens
        self.initialized = self.initialize_tokens()
    
    def extract_user_id(self):
        """Extract user ID from cookie"""
        try:
            if 'c_user=' in self.cookie:
                user_id = self.cookie.split('c_user=')[1].split(';')[0]
                return user_id
        except:
            pass
        return None
    
    def initialize_tokens(self):
        """Get all required tokens from Facebook"""
        if not self.user_id:
            return False
            
        try:
            # Get tokens from main page
            response = self.session.get('https://www.facebook.com/', timeout=15)
            
            if response.status_code != 200:
                return False
            
            html = response.text
            
            # Extract fb_dtsg
            dtsg_patterns = [
                r'"DTSGInitialData",\[\],{"token":"([^"]+)"',
                r'{"name":"fb_dtsg","value":"([^"]+)"',
                r'"token":"([^"]+)","async_get_token"'
            ]
            
            for pattern in dtsg_patterns:
                match = re.search(pattern, html)
                if match:
                    self.fb_dtsg = match.group(1)
                    break
            
            # Extract LSD
            lsd_patterns = [
                r'"LSD",\[\],{"token":"([^"]+)"',
                r'{"name":"lsd","value":"([^"]+)"'
            ]
            
            for pattern in lsd_patterns:
                match = re.search(pattern, html)
                if match:
                    self.lsd = match.group(1)
                    break
            
            # Generate jazoest
            if self.user_id:
                self.jazoest = '2' + str(sum(ord(c) for c in self.user_id))
            
            return bool(self.fb_dtsg and self.user_id)
            
        except Exception as e:
            print(f"[!] Token initialization error: {str(e)}")
            return False
    
    def validate_cookie(self):
        """Validate if cookie is working"""
        try:
            response = self.session.get('https://www.facebook.com/me', timeout=10, allow_redirects=False)
            return response.status_code == 200 or response.status_code == 302
        except:
            return False
    
    def get_post_info(self, post_id):
        """Get post information to validate post ID"""
        try:
            url = f'https://www.facebook.com/{post_id}'
            response = self.session.get(url, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def react_to_post(self, post_id, reaction_type='LIKE'):
        """
        React to Facebook post using GraphQL API
        Supports: LIKE, LOVE, CARE, HAHA, WOW, SAD, ANGRY
        """
        
        # Reaction type IDs
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
        
        # Prepare GraphQL variables
        variables = {
            'input': {
                'attribution_id_v2': f'FeedbackReactMutation.react_story,{post_id},{int(time.time())}',
                'feedback_id': post_id,
                'feedback_reaction_id': reaction_id,
                'feedback_source': 'OBJECT',
                'is_tracking_encrypted': False,
                'tracking': [],
                'session_id': str(int(time.time())),
                'actor_id': self.user_id,
                'client_mutation_id': str(int(time.time() * 1000))
            }
        }
        
        # Payload
        payload = {
            'fb_dtsg': self.fb_dtsg,
            'jazoest': self.jazoest,
            'fb_api_req_friendly_name': 'FeedbackReactMutation',
            'variables': json.dumps(variables),
            'server_timestamps': 'true',
            'doc_id': '5359434074136134'
        }
        
        # Add LSD if available
        if self.lsd:
            payload['lsd'] = self.lsd
        
        try:
            response = self.session.post(
                'https://www.facebook.com/api/graphql/',
                data=payload,
                timeout=20
            )
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    
                    # Check for errors
                    if 'errors' in result:
                        error_msg = result['errors'][0].get('message', 'Unknown error')
                        return False, f"API Error: {error_msg}"
                    
                    # Check for successful reaction
                    if 'data' in result:
                        return True, f"Successfully reacted with {reaction_type}"
                    
                    return True, "Reaction sent (no confirmation)"
                    
                except json.JSONDecodeError:
                    # Some successful reactions don't return JSON
                    if 'for (;;);' in response.text:
                        return True, f"Reacted with {reaction_type}"
                    return False, "Invalid response format"
            else:
                return False, f"HTTP {response.status_code}"
                
        except requests.exceptions.Timeout:
            return False, "Request timeout"
        except Exception as e:
            return False, f"Exception: {str(e)[:50]}"

def extract_post_id(url_or_id):
    """Extract post ID from various Facebook URL formats"""
    url_or_id = url_or_id.strip()
    
    # If it's already just numbers, return it
    if url_or_id.isdigit():
        return url_or_id
    
    # Try different URL patterns
    patterns = [
        r'facebook\.com/[^/]+/posts/(\d+)',
        r'facebook\.com/photo\.php\?fbid=(\d+)',
        r'facebook\.com/permalink\.php\?story_fbid=(\d+)',
        r'story_fbid=(\d+)',
        r'/posts/(\d+)',
        r'fbid=(\d+)',
        r'(\d{15,})'  # Long number
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    
    return url_or_id

def worker(cookie, post_id, reaction_type, thread_id):
    """Worker function for threading"""
    try:
        fb = FBAutoReact(cookie)
        
        if not fb.user_id:
            return thread_id, False, f"[Thread-{thread_id}] Invalid cookie - no user ID found"
        
        if not fb.initialized:
            return thread_id, False, f"[Thread-{thread_id}] [{fb.user_id}] Failed to get tokens"
        
        # Validate cookie
        if not fb.validate_cookie():
            return thread_id, False, f"[Thread-{thread_id}] [{fb.user_id}] Cookie expired or invalid"
        
        # React to post
        success, message = fb.react_to_post(post_id, reaction_type)
        
        if success:
            status = f"[Thread-{thread_id}] ✓ [{fb.user_id}] {message}"
        else:
            status = f"[Thread-{thread_id}] ✗ [{fb.user_id}] {message}"
        
        return thread_id, success, status
        
    except Exception as e:
        return thread_id, False, f"[Thread-{thread_id}] Error: {str(e)[:100]}"

def banner():
    """Display banner"""
    print("""
╔════════════════════════════════════════════╗
║     FB Auto React Tool - Termux           ║
║     Multi-Account Cookie Input            ║
║     GraphQL API - Improved Version        ║
╚════════════════════════════════════════════╝
    """)

def get_cookies():
    """Get cookies from user input"""
    print("\n[*] Cookie Input Methods:")
    print("1. Enter cookies manually (one by one)")
    print("2. Load from file (cookies.txt)")
    
    choice = input("\n[?] Select method (1 or 2): ").strip()
    
    cookies = []
    
    if choice == '2':
        try:
            with open('cookies.txt', 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        cookies.append(line)
            print(f"[+] Loaded {len(cookies)} cookie(s) from file")
        except FileNotFoundError:
            print("[!] cookies.txt not found!")
            return []
    else:
        print("\n[*] Enter cookies (one per line, press Enter twice when done):")
        print("[*] Cookie format: datr=xxx;sb=xxx;c_user=xxx;xs=xxx;fr=xxx")
        print()
        
        while True:
            cookie = input("Cookie: ").strip()
            if not cookie:
                if cookies:
                    break
                else:
                    continue
            
            # Validate cookie has c_user
            if 'c_user=' not in cookie:
                print("[!] Invalid cookie - must contain c_user")
                continue
            
            cookies.append(cookie)
            print(f"[+] Added cookie #{len(cookies)}")
    
    return cookies

def main():
    banner()
    
    # Get cookies
    cookies = get_cookies()
    
    if not cookies:
        print("[!] No cookies provided. Exiting...")
        return
    
    print(f"\n[+] Total cookies loaded: {len(cookies)}")
    
    # Get post ID
    print("\n[*] Enter Post ID or URL:")
    print("   Examples:")
    print("   - 123456789012345")
    print("   - https://facebook.com/username/posts/123456789012345")
    print("   - https://facebook.com/photo.php?fbid=123456789012345")
    
    post_input = input("\n[?] Post ID/URL: ").strip()
    
    if not post_input:
        print("[!] Post ID/URL required!")
        return
    
    post_id = extract_post_id(post_input)
    print(f"[+] Extracted Post ID: {post_id}")
    
    # Select reaction type
    print("\n[*] Select Reaction Type:")
    print("1. 👍 LIKE")
    print("2. ❤️  LOVE")
    print("3. 🤗 CARE")
    print("4. 😂 HAHA")
    print("5. 😮 WOW")
    print("6. 😢 SAD")
    print("7. 😡 ANGRY")
    
    choice = input("\n[?] Select reaction (1-7, default: 1): ").strip() or '1'
    
    reactions = {
        '1': 'LIKE', '2': 'LOVE', '3': 'CARE',
        '4': 'HAHA', '5': 'WOW', '6': 'SAD', '7': 'ANGRY'
    }
    reaction_type = reactions.get(choice, 'LIKE')
    
    # Threading settings
    max_threads = input("\n[?] Max threads (1-20, default: 5): ").strip() or '5'
    max_threads = min(int(max_threads), 20)
    
    # Delay between requests
    delay = input("[?] Delay between accounts in seconds (default: 2): ").strip() or '2'
    delay = float(delay)
    
    print("\n" + "="*50)
    print(f"[+] Starting Auto-React...")
    print(f"[+] Post ID: {post_id}")
    print(f"[+] Reaction: {reaction_type}")
    print(f"[+] Accounts: {len(cookies)}")
    print(f"[+] Threads: {max_threads}")
    print(f"[+] Delay: {delay}s")
    print("="*50 + "\n")
    
    # Execute with threading
    success_count = 0
    failed_count = 0
    results = []
    
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = []
        
        for i, cookie in enumerate(cookies, 1):
            future = executor.submit(worker, cookie, post_id, reaction_type, i)
            futures.append(future)
            time.sleep(0.2)  # Small delay between submissions
        
        for future in as_completed(futures):
            thread_id, success, status = future.result()
            print(status)
            results.append((success, status))
            
            if success:
                success_count += 1
            else:
                failed_count += 1
            
            time.sleep(delay)  # Rate limiting
    
    # Summary
    print("\n" + "="*50)
    print("[+] SUMMARY")
    print("="*50)
    print(f"✓ Success: {success_count}")
    print(f"✗ Failed: {failed_count}")
    print(f"Total: {len(cookies)}")
    print(f"Success Rate: {(success_count/len(cookies)*100):.1f}%")
    print("="*50)
    
    # Save results
    save = input("\n[?] Save results to file? (y/n): ").strip().lower()
    if save == 'y':
        filename = f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w') as f:
            f.write(f"Post ID: {post_id}\n")
            f.write(f"Reaction: {reaction_type}\n")
            f.write(f"Success: {success_count}/{len(cookies)}\n\n")
            for success, status in results:
                f.write(f"{status}\n")
        print(f"[+] Results saved to {filename}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!] Interrupted by user. Exiting...")
    except Exception as e:
        print(f"\n[!] Fatal Error: {str(e)}")
        import traceback
        traceback.print_exc()
