#!/usr/bin/env python3
"""
Facebook Auto React Tool - Fixed GraphQL & Better Error Handling
With scraping detection fix and error tracking
"""

import requests
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
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
        self.errors = 0
        self.max_errors = 3
        
        self.session.headers.update({
            'authority': 'www.facebook.com',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://www.facebook.com',
            'referer': 'https://www.facebook.com/',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'cookie': self.cookie
        })
        
        self.initialized = self.login()
    
    def extract_user_id(self):
        """Extract user ID from cookie"""
        try:
            if 'c_user=' in self.cookie:
                return self.cookie.split('c_user=')[1].split(';')[0]
        except:
            pass
        return None
    
    def login(self):
        """Login and get all required tokens"""
        if not self.user_id:
            return False
        
        try:
            # Get tokens from ajax/dtsg endpoint
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
                    
                    # Extract fb_dtsg token
                    if 'payload' in data and 'token' in data['payload']:
                        self.fb_dtsg = data['payload']['token']
                    
                except json.JSONDecodeError:
                    pass
            
            # Fallback: Get from main page
            if not self.fb_dtsg:
                response = self.session.get('https://www.facebook.com/', timeout=15)
                html = response.text
                
                patterns = [
                    r'"DTSGInitialData",\[\],{"token":"([^"]+)"',
                    r'"token":"([^"]+)","async_get_token"',
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
            
            # Generate jazoest
            if self.user_id:
                self.jazoest = '2' + str(sum(ord(c) for c in self.user_id))
            
            return bool(self.fb_dtsg and self.user_id)
            
        except Exception as e:
            return False
    
    def fix_scraping_detection(self):
        """Fix scraping detection by refreshing session"""
        try:
            # Visit main page to reset detection
            self.session.get('https://www.facebook.com/', timeout=10)
            time.sleep(1)
            
            # Re-login to get new tokens
            return self.login()
        except:
            return False
    
    def react_to_post(self, post_id, reaction_type='LIKE'):
        """React to Facebook post with error handling"""
        
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
        
        # Try multiple doc_ids (Facebook updates these frequently)
        doc_ids = [
            '6360991980619959',  # Latest
            '5359434074136134',  # Backup 1
            '4769042373179384',  # Backup 2
            '3649573195102428',  # Backup 3
        ]
        
        for doc_id in doc_ids:
            variables = {
                "input": {
                    "attribution_id_v2": f"CometSinglePostRoot.react_relay,comet.single_post,via_cold_start,{int(time.time())},100000,190055527696468,,",
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
                '__ccg': 'EXCELLENT',
                '__rev': self.revision or '1007797763',
                'fb_dtsg': self.fb_dtsg,
                'jazoest': self.jazoest,
                'fb_api_caller_class': 'RelayModern',
                'fb_api_req_friendly_name': 'CometUFIFeedbackReactMutation',
                'variables': json.dumps(variables),
                'server_timestamps': 'true',
                'doc_id': doc_id
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
                            error = result['errors'][0]
                            error_msg = error.get('message', 'Unknown error')
                            error_code = error.get('code', 0)
                            
                            # Handle specific errors
                            if 'was not found' in error_msg or 'doc_id' in error_msg.lower():
                                # Try next doc_id
                                continue
                            
                            # Scraping detection
                            if 'scraping' in error_msg.lower() or 'FBScrapingWarningCometApp' in error_msg:
                                if self.fix_scraping_detection():
                                    return self.react_to_post(post_id, reaction_type)
                                return False, "❌ Scraping detected - Account flagged"
                            
                            # New packs error (needs login refresh)
                            if 'new_packs' in error_msg.lower() or 'renew_values' in error_msg.lower():
                                if self.errors < self.max_errors:
                                    self.errors += 1
                                    if self.login():
                                        return self.react_to_post(post_id, reaction_type)
                                return False, f"❌ Login failed: {error_msg}"
                            
                            return False, f"❌ FB Error: {error_msg}"
                        
                        # Check for successful reaction
                        if 'data' in result:
                            self.errors = 0  # Reset error count on success
                            return True, f"✓ {reaction_type}"
                        
                        return True, "✓ Sent"
                        
                    except json.JSONDecodeError:
                        # Sometimes successful reactions don't return JSON
                        if response.status_code == 200:
                            return True, f"✓ {reaction_type}"
                        return False, "❌ Invalid response"
                else:
                    return False, f"❌ HTTP {response.status_code}"
                    
            except requests.exceptions.Timeout:
                return False, "❌ Timeout"
            except Exception as e:
                return False, f"❌ {str(e)[:40]}"
        
        return False, "❌ All doc_ids failed"

def worker(cookie, post_id, reaction_type, thread_id):
    """Worker function with error tracking"""
    try:
        fb = FBAutoReact(cookie)
        
        if not fb.user_id:
            return thread_id, False, f"[{thread_id}] ❌ Invalid cookie - No user ID", "INVALID_COOKIE"
        
        if not fb.initialized:
            return thread_id, False, f"[{thread_id}] [{fb.user_id}] ❌ Login failed", "LOGIN_FAILED"
        
        # React to post
        success, message = fb.react_to_post(post_id, reaction_type)
        
        status = f"[{thread_id}] [{fb.user_id}] {message}"
        error_type = None if success else "REACTION_FAILED"
        
        return thread_id, success, status, error_type
        
    except Exception as e:
        return thread_id, False, f"[{thread_id}] ❌ Exception: {str(e)[:60]}", "EXCEPTION"

def banner():
    print("""
╔════════════════════════════════════════════╗
║  FB Auto React - Fixed GraphQL Doc ID     ║
║  With Scraping Detection Handler          ║
║  Error Tracking & Auto-Recovery           ║
╚════════════════════════════════════════════╝
    """)

def extract_post_id(url_or_id):
    """Extract post ID from various formats"""
    url_or_id = url_or_id.strip()
    
    # Already a post ID
    if url_or_id.isdigit() or '_' in url_or_id:
        return url_or_id
    
    try:
        parsed = urlparse(url_or_id)
        params = parse_qs(parsed.query)
        
        # Format: ?story_fbid=X&id=Y
        if 'story_fbid' in params and 'id' in params:
            return f"{params['id'][0]}_{params['story_fbid'][0]}"
        
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
    print("\n[*] Enter cookies (empty line when done):")
    print("[*] Format: datr=xxx;sb=xxx;c_user=xxx;xs=xxx")
    print()
    
    cookies = []
    while True:
        cookie = input(f"Cookie #{len(cookies)+1}: ").strip()
        if not cookie:
            if cookies:
                break
            continue
        
        if 'c_user=' not in cookie:
            print("   ❌ Invalid - must contain c_user")
            continue
        
        cookies.append(cookie)
        print("   ✓ Added!")
    
    return cookies

def main():
    banner()
    
    # Get cookies
    cookies = get_cookies()
    
    if not cookies:
        print("\n❌ No cookies provided!")
        return
    
    print(f"\n✓ Loaded {len(cookies)} cookie(s)")
    
    # Get post
    print("\n[*] Enter Facebook post URL or ID:")
    print("   Example: https://www.facebook.com/61569634753113/posts/pfbid02S5uMn/")
    post_input = input("\n[?] Post: ").strip()
    
    if not post_input:
        print("\n❌ Post required!")
        return
    
    post_id = extract_post_id(post_input)
    print(f"✓ Post ID: {post_id}")
    
    # Reaction selection
    print("\n[*] Select Reaction:")
    print("1.👍 LIKE  2.❤️ LOVE  3.🤗 CARE  4.😂 HAHA")
    print("5.😮 WOW   6.😢 SAD   7.😡 ANGRY")
    
    choice = input("\n[?] Choose (1-7): ").strip() or '1'
    reactions = {
        '1': 'LIKE', '2': 'LOVE', '3': 'CARE',
        '4': 'HAHA', '5': 'WOW', '6': 'SAD', '7': 'ANGRY'
    }
    reaction = reactions.get(choice, 'LIKE')
    
    # Threading
    threads = input("[?] Threads (1-10): ").strip() or '5'
    threads = min(int(threads), 10)
    
    print("\n" + "="*60)
    print(f"Starting Auto React...")
    print(f"Post: {post_id}")
    print(f"Reaction: {reaction}")
    print(f"Accounts: {len(cookies)}")
    print(f"Threads: {threads}")
    print("="*60 + "\n")
    
    success = 0
    failed = 0
    errors = {
        'INVALID_COOKIE': 0,
        'LOGIN_FAILED': 0,
        'REACTION_FAILED': 0,
        'EXCEPTION': 0
    }
    
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [
            executor.submit(worker, cookie, post_id, reaction, i)
            for i, cookie in enumerate(cookies, 1)
        ]
        
        for future in as_completed(futures):
            tid, ok, msg, error_type = future.result()
            print(msg)
            
            if ok:
                success += 1
            else:
                failed += 1
                if error_type:
                    errors[error_type] += 1
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"✓ Success: {success}")
    print(f"✗ Failed: {failed}")
    print(f"Total: {len(cookies)}")
    print(f"Success Rate: {(success/len(cookies)*100):.1f}%")
    
    if failed > 0:
        print("\n[Error Breakdown]")
        for error_type, count in errors.items():
            if count > 0:
                print(f"  - {error_type}: {count}")
    
    print("="*60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Stopped by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
