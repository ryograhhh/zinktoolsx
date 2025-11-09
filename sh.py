#!/usr/bin/env python3
"""
Facebook Auto React Tool v2.0 - Using Latest DTSG Getter Method
Based on working Node.js implementation with proper token extraction
"""

import requests
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, parse_qs, unquote
import random

class FBAutoReact:
    def __init__(self, cookie):
        self.cookie = cookie.strip()
        self.session = requests.Session()
        self.user_id = self.extract_user_id()
        self.fb_dtsg = None
        self.jazoest = None
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
        
        self.initialized = self.get_dtsg()
    
    def extract_user_id(self):
        """Extract user ID from cookie - exactly like Node.js version"""
        try:
            match = re.search(r'c_user=([^;]+)', self.cookie)
            if match:
                return match.group(1)
        except:
            pass
        return None
    
    def get_dtsg(self):
        """Get fb_dtsg token - using exact method from Node.js code"""
        if not self.user_id:
            return False
        
        try:
            # Use exact endpoint from working code
            response = self.session.get(
                'https://www.facebook.com/ajax/dtsg/?__a',
                headers={'cookie': self.cookie},
                timeout=15
            )
            
            if response.status_code != 200:
                return False
            
            # Parse response exactly like Node.js version
            text = response.text
            
            # Remove for(;;); prefix like in Node.js: resp.data.replace(/^\s*for\s*\(\s*;;\s*\)\s*;?/, '')
            text = re.sub(r'^\s*for\s*\(\s*;;\s*\)\s*;?', '', text)
            
            try:
                # Parse JSON
                data = json.loads(text)
                
                # Extract token exactly like Node.js: obj?.payload?.token
                if 'payload' in data and 'token' in data['payload']:
                    self.fb_dtsg = data['payload']['token']
                else:
                    return False
                
            except json.JSONDecodeError:
                return False
            
            # Generate jazoest
            if self.user_id:
                self.jazoest = '2' + str(sum(ord(c) for c in self.user_id))
            
            return bool(self.fb_dtsg and self.user_id)
            
        except Exception as e:
            print(f"[DEBUG] DTSG error: {str(e)}")
            return False
    
    def get_payload(self):
        """Get complete payload data for GraphQL request"""
        return {
            'av': self.user_id,
            '__user': self.user_id,
            'fb_dtsg': self.fb_dtsg,
            'fb_api_caller_class': 'RelayModern',
        }
    
    def fix_scraping_detection(self):
        """Fix scraping detection by refreshing tokens"""
        try:
            time.sleep(2)
            return self.get_dtsg()
        except:
            return False
    
    def get_feedback_id(self, post_url_or_id):
        """Convert post URL/ID to proper feedback_id format - Enhanced for pfbid"""
        try:
            post_url_or_id = str(post_url_or_id).strip()
            
            # If already valid numeric format
            if post_url_or_id.replace('_', '').isdigit() and len(post_url_or_id) > 10:
                return post_url_or_id
            
            # Handle pfbid format - need to resolve it to numeric ID
            if 'pfbid' in post_url_or_id or 'facebook.com' in post_url_or_id:
                # Build full URL
                if not post_url_or_id.startswith('http'):
                    post_url_or_id = f'https://www.facebook.com/{post_url_or_id}'
                
                # Remove app=fbl parameter if present
                post_url_or_id = re.sub(r'[?&]app=fbl', '', post_url_or_id)
                
                print(f"[DEBUG] Fetching post: {post_url_or_id}")
                
                response = self.session.get(post_url_or_id, timeout=15, allow_redirects=True)
                html = response.text
                
                # Multiple patterns to extract feedback_id
                patterns = [
                    r'"feedback_id":"(\d+)"',
                    r'"feedbackID":"(\d+)"',
                    r'"post_id":"(\d+)"',
                    r'"id":"(\d+)"[^}]*"__typename":"Post"',
                    r'feedback_id=(\d+)',
                    r'story_fbid=(\d+).*?id=(\d+)',
                    r'"target_id":(\d+)',
                    r'top_level_post_id.*?(\d{15,})',
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, html)
                    if matches:
                        # If tuple (story_fbid, id pattern)
                        if isinstance(matches[0], tuple):
                            return f"{matches[0][1]}_{matches[0][0]}"
                        # Find longest match (most likely correct)
                        longest = max(matches, key=len)
                        if len(str(longest)) >= 15:  # Valid FB post ID length
                            print(f"[DEBUG] Extracted feedback_id: {longest}")
                            return str(longest)
                
                print(f"[DEBUG] Could not extract numeric ID from HTML, using pfbid directly")
            
            # Parse URL parameters
            if 'facebook.com' in post_url_or_id:
                parsed = urlparse(post_url_or_id)
                params = parse_qs(parsed.query)
                
                # story_fbid + id format
                if 'story_fbid' in params and 'id' in params:
                    return f"{params['id'][0]}_{params['story_fbid'][0]}"
                
                # /posts/ format
                if '/posts/' in post_url_or_id:
                    match = re.search(r'/posts/([^/?]+)', post_url_or_id)
                    if match:
                        return match.group(1)
            
        except Exception as e:
            print(f"[DEBUG] get_feedback_id error: {str(e)}")
        
        return post_url_or_id
    
    def react_to_post(self, post_id, reaction_type='LIKE'):
        """React to Facebook post using GraphQL API"""
        
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
        feedback_id = self.get_feedback_id(post_id)
        
        # Multiple doc_ids to try
        doc_ids = [
            '7565960703454863',
            '6360991980619959',
            '5359434074136134',
            '4769042373179384',
        ]
        
        for attempt, doc_id in enumerate(doc_ids):
            try:
                # Build variables
                variables = {
                    "input": {
                        "client_mutation_id": str(int(time.time() * 1000)),
                        "actor_id": self.user_id,
                        "feedback_id": feedback_id,
                        "feedback_reaction_id": reaction_id,
                        "feedback_source": "OBJECT",
                        "feedback_referrer": "NEWSFEED",
                        "is_tracking_encrypted": False,
                        "tracking": "",
                        "session_id": str(int(time.time())),
                        "attribution_id_v2": f"NewsFeedRoot,comet.home,unexpected,{int(time.time())},,,",
                    },
                    "useDefaultActor": False,
                    "scale": 1
                }
                
                # Build payload using same format as Node.js
                payload = {
                    'av': self.user_id,
                    '__user': self.user_id,
                    'fb_dtsg': self.fb_dtsg,
                    'fb_api_caller_class': 'RelayModern',
                    'fb_api_req_friendly_name': 'CometUFIFeedbackReactMutation',
                    'variables': json.dumps(variables),
                    'server_timestamps': 'true',
                    'doc_id': doc_id
                }
                
                # Make GraphQL request
                response = self.session.post(
                    'https://www.facebook.com/api/graphql/',
                    data=payload,
                    timeout=20
                )
                
                if response.status_code == 200:
                    text = response.text
                    
                    # Remove for(;;); prefix
                    text = re.sub(r'^\s*for\s*\(\s*;;\s*\)\s*;?', '', text)
                    
                    try:
                        result = json.loads(text)
                        
                        # Check for errors
                        if 'errors' in result:
                            error = result['errors'][0]
                            error_msg = error.get('message', 'Unknown error')
                            
                            # Handle specific errors
                            if 'was not found' in error_msg or 'missing_required_variable' in error_msg.lower():
                                continue  # Try next doc_id
                            
                            # Scraping detection
                            if 'scraping' in error_msg.lower() or 'FBScrapingWarningCometApp' in error_msg:
                                if self.errors < self.max_errors:
                                    self.errors += 1
                                    if self.fix_scraping_detection():
                                        return self.react_to_post(post_id, reaction_type)
                                return False, "❌ Scraping detected"
                            
                            # Session expired
                            if 'new_packs' in error_msg.lower() or 'renew' in error_msg.lower():
                                if self.errors < self.max_errors:
                                    self.errors += 1
                                    if self.get_dtsg():
                                        return self.react_to_post(post_id, reaction_type)
                                return False, "❌ Session expired"
                            
                            if attempt == len(doc_ids) - 1:
                                return False, f"❌ {error_msg[:50]}"
                            continue
                        
                        # Success
                        if 'data' in result:
                            self.errors = 0
                            return True, f"✓ {reaction_type}"
                        
                        return True, f"✓ {reaction_type}"
                        
                    except json.JSONDecodeError:
                        if response.status_code == 200:
                            return True, f"✓ {reaction_type}"
                        continue
                else:
                    if attempt == len(doc_ids) - 1:
                        return False, f"❌ HTTP {response.status_code}"
                    continue
                    
            except requests.exceptions.Timeout:
                if attempt == len(doc_ids) - 1:
                    return False, "❌ Timeout"
                continue
            except Exception as e:
                if attempt == len(doc_ids) - 1:
                    return False, f"❌ {str(e)[:40]}"
                continue
        
        return False, "❌ All attempts failed"

def worker(cookie, post_id, reaction_type, thread_id):
    """Worker function for threading"""
    try:
        fb = FBAutoReact(cookie)
        
        if not fb.user_id:
            return thread_id, False, f"[{thread_id}] ❌ Invalid cookie", "INVALID_COOKIE"
        
        if not fb.initialized:
            return thread_id, False, f"[{thread_id}] [{fb.user_id}] ❌ Failed to get DTSG token", "LOGIN_FAILED"
        
        success, message = fb.react_to_post(post_id, reaction_type)
        status = f"[{thread_id}] [{fb.user_id}] {message}"
        error_type = None if success else "REACTION_FAILED"
        
        return thread_id, success, status, error_type
        
    except Exception as e:
        return thread_id, False, f"[{thread_id}] ❌ {str(e)[:60]}", "EXCEPTION"

def banner():
    print("""
╔════════════════════════════════════════════════════╗
║  FB Auto React v2.0 - Latest DTSG Method          ║
║  Based on Working Node.js Implementation          ║
║  ✓ Exact token extraction from working code      ║
║  ✓ Proper error handling                          ║
║  ✓ Multiple fallback mechanisms                   ║
╚════════════════════════════════════════════════════╝
    """)

def extract_post_id(url_or_id):
    """Extract post ID from URL"""
    url_or_id = url_or_id.strip()
    
    if url_or_id.replace('_', '').isdigit() or url_or_id.startswith('pfbid'):
        return url_or_id
    
    try:
        parsed = urlparse(url_or_id)
        params = parse_qs(parsed.query)
        
        if 'story_fbid' in params and 'id' in params:
            return f"{params['id'][0]}_{params['story_fbid'][0]}"
        
        if '/posts/' in url_or_id:
            match = re.search(r'/posts/([^/?]+)', url_or_id)
            if match:
                return match.group(1)
        
        if 'pfbid' in url_or_id:
            match = re.search(r'pfbid[\w]+', url_or_id)
            if match:
                return match.group(0)
        
        match = re.search(r'(\d{15,})', url_or_id)
        if match:
            return match.group(1)
    except:
        pass
    
    return url_or_id

def get_cookies():
    """Get cookies from user"""
    print("\n[*] Cookie Input:")
    print("1. Enter manually")
    print("2. Load from cookies.txt")
    
    choice = input("\n[?] Choose (1-2): ").strip()
    
    cookies = []
    
    if choice == '2':
        try:
            with open('cookies.txt', 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        cookies.append(line)
            print(f"✓ Loaded {len(cookies)} cookie(s)")
        except FileNotFoundError:
            print("❌ cookies.txt not found!")
            return []
    else:
        print("\n[*] Enter cookies (empty line to finish):")
        print("[*] Format: datr=xxx;sb=xxx;c_user=xxx;xs=xxx")
        print()
        
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
    
    cookies = get_cookies()
    
    if not cookies:
        print("\n❌ No cookies!")
        return
    
    print(f"\n✓ Total: {len(cookies)} cookie(s)")
    
    print("\n[*] Enter post URL or ID:")
    print("   Examples:")
    print("   - https://www.facebook.com/PAGE/posts/123456789")
    print("   - https://www.facebook.com/61569634753113/posts/pfbid02S5uMn/")
    
    post_input = input("\n[?] Post: ").strip()
    
    if not post_input:
        print("\n❌ Post required!")
        return
    
    post_id = extract_post_id(post_input)
    print(f"✓ Post ID: {post_id}")
    
    print("\n[*] Reactions:")
    print("1.👍 LIKE  2.❤️ LOVE  3.🤗 CARE  4.😂 HAHA")
    print("5.😮 WOW   6.😢 SAD   7.😡 ANGRY")
    
    choice = input("\n[?] Choose (1-7): ").strip() or '1'
    reactions = {
        '1': 'LIKE', '2': 'LOVE', '3': 'CARE',
        '4': 'HAHA', '5': 'WOW', '6': 'SAD', '7': 'ANGRY'
    }
    reaction = reactions.get(choice, 'LIKE')
    
    threads = input("[?] Threads (1-10): ").strip() or '5'
    threads = min(max(int(threads), 1), 10)
    
    print("\n" + "="*60)
    print("Starting...")
    print(f"Post: {post_id}")
    print(f"Reaction: {reaction}")
    print(f"Accounts: {len(cookies)}")
    print(f"Threads: {threads}")
    print("="*60 + "\n")
    
    success = 0
    failed = 0
    errors = {'INVALID_COOKIE': 0, 'LOGIN_FAILED': 0, 'REACTION_FAILED': 0, 'EXCEPTION': 0}
    
    start = time.time()
    
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [
            executor.submit(worker, cookie, post_id, reaction, i)
            for i, cookie in enumerate(cookies, 1)
        ]
        
        for future in as_completed(futures):
            tid, ok, msg, err_type = future.result()
            print(msg)
            
            if ok:
                success += 1
            else:
                failed += 1
                if err_type:
                    errors[err_type] += 1
            
            time.sleep(0.1)
    
    elapsed = time.time() - start
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"✓ Success: {success}")
    print(f"✗ Failed: {failed}")
    print(f"Total: {len(cookies)}")
    print(f"Success Rate: {(success/len(cookies)*100):.1f}%")
    print(f"Time: {elapsed:.2f}s")
    
    if failed > 0:
        print("\n[Error Breakdown]")
        for err_type, count in errors.items():
            if count > 0:
                print(f"  - {err_type}: {count}")
    
    print("="*60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Stopped")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
