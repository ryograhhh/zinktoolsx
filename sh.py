#!/usr/bin/env python3
"""
Facebook Auto React Tool v3.0 - Enhanced & Updated
Fixed token extraction and reaction mechanisms
"""

import requests
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, parse_qs
import random

class FBAutoReact:
    def __init__(self, cookie):
        self.cookie = cookie.strip()
        self.session = requests.Session()
        self.user_id = self.extract_user_id()
        self.fb_dtsg = None
        self.jazoest = None
        self.lsd = None
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
            'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'cookie': self.cookie,
            'x-fb-friendly-name': 'CometUFIFeedbackReactMutation',
            'x-fb-lsd': ''
        })
        
        self.initialized = self.initialize_tokens()
    
    def extract_user_id(self):
        """Extract user ID from cookie"""
        try:
            match = re.search(r'c_user=([^;]+)', self.cookie)
            if match:
                return match.group(1)
        except:
            pass
        return None
    
    def initialize_tokens(self):
        """Initialize all required tokens from Facebook homepage"""
        if not self.user_id:
            return False
        
        try:
            # First, get tokens from main page
            response = self.session.get(
                'https://www.facebook.com/',
                timeout=20,
                allow_redirects=True
            )
            
            if response.status_code != 200:
                return False
            
            html = response.text
            
            # Extract fb_dtsg - multiple patterns
            dtsg_patterns = [
                r'"DTSGInitialData".*?"token":"([^"]+)"',
                r'"dtsg":\{"token":"([^"]+)"',
                r'{"token":"([^"]+)","async_get_token"',
                r'\["DTSGInitialData",\[\],\{"token":"([^"]+)"',
                r'name="fb_dtsg" value="([^"]+)"'
            ]
            
            for pattern in dtsg_patterns:
                match = re.search(pattern, html)
                if match:
                    self.fb_dtsg = match.group(1)
                    break
            
            # Extract LSD token
            lsd_patterns = [
                r'"LSD",\[\],\{"token":"([^"]+)"',
                r'"lsd":"([^"]+)"',
                r'name="lsd" value="([^"]+)"'
            ]
            
            for pattern in lsd_patterns:
                match = re.search(pattern, html)
                if match:
                    self.lsd = match.group(1)
                    self.session.headers['x-fb-lsd'] = self.lsd
                    break
            
            # Generate jazoest from user_id
            if self.user_id:
                self.jazoest = '2' + str(sum(ord(c) for c in self.user_id))
            
            # Fallback: try AJAX endpoint
            if not self.fb_dtsg:
                ajax_response = self.session.get(
                    'https://www.facebook.com/ajax/dtsg/?__a=1',
                    timeout=15
                )
                
                if ajax_response.status_code == 200:
                    text = ajax_response.text
                    text = re.sub(r'^\s*for\s*\(\s*;;\s*\)\s*;?', '', text)
                    
                    try:
                        data = json.loads(text)
                        if 'payload' in data and 'token' in data['payload']:
                            self.fb_dtsg = data['payload']['token']
                    except:
                        pass
            
            return bool(self.fb_dtsg and self.user_id)
            
        except Exception as e:
            print(f"[DEBUG] Token init error: {str(e)}")
            return False
    
    def get_feedback_id(self, post_url_or_id):
        """Enhanced feedback ID extraction with multiple methods"""
        try:
            post_url_or_id = str(post_url_or_id).strip()
            
            # If already numeric format
            if post_url_or_id.replace('_', '').isdigit() and len(post_url_or_id) > 10:
                return post_url_or_id
            
            # Build full URL if needed
            if not post_url_or_id.startswith('http'):
                if 'pfbid' in post_url_or_id:
                    post_url_or_id = f'https://www.facebook.com/permalink.php?story_fbid={post_url_or_id}'
                else:
                    post_url_or_id = f'https://www.facebook.com/{post_url_or_id}'
            
            # Parse URL parameters first
            parsed = urlparse(post_url_or_id)
            params = parse_qs(parsed.query)
            
            if 'story_fbid' in params and 'id' in params:
                return f"{params['id'][0]}_{params['story_fbid'][0]}"
            
            # Fetch page to extract ID
            response = self.session.get(post_url_or_id, timeout=20, allow_redirects=True)
            html = response.text
            
            # Enhanced extraction patterns
            patterns = [
                r'"feedback_id":"(\d+)"',
                r'"feedbackID":"(\d+)"',
                r'"post_id":"(\d+)"',
                r'"id":"(\d+)"[^}]{0,100}"__typename":"Post"',
                r'"top_level_post_id":"(\d+)"',
                r'"legacy_story_hideable_id":"(\d+)"',
                r'feedback_id=(\d+)',
                r'story_fbid=(\d+)&amp;id=(\d+)',
                r'"target_id":(\d+)',
                r'data-ft=.*?"top_level_post_id":"(\d+)"',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, html)
                if matches:
                    if isinstance(matches[0], tuple):
                        return f"{matches[0][1]}_{matches[0][0]}"
                    
                    # Get longest numeric ID
                    longest = max(matches, key=len)
                    if len(str(longest)) >= 15:
                        return str(longest)
            
            # Try to extract from URL path
            if '/posts/' in post_url_or_id:
                match = re.search(r'/posts/([^/?]+)', post_url_or_id)
                if match:
                    return match.group(1)
            
        except Exception as e:
            print(f"[DEBUG] Feedback ID error: {str(e)}")
        
        return post_url_or_id
    
    def react_to_post(self, post_id, reaction_type='LIKE'):
        """React to post with enhanced error handling"""
        
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
        
        # Updated doc_ids for 2025
        doc_ids = [
            '8526943427345374',  # Latest known working
            '7565960703454863',
            '6360991980619959',
            '5359434074136134',
        ]
        
        for attempt, doc_id in enumerate(doc_ids):
            try:
                # Build variables
                variables = {
                    "input": {
                        "attribution_id_v2": f"CometHomeRoot.react,comet.home,unexpected,{int(time.time())},,,",
                        "feedback_id": feedback_id,
                        "feedback_reaction_id": reaction_id,
                        "feedback_source": "OBJECT",
                        "is_tracking_encrypted": False,
                        "tracking": "",
                        "session_id": str(int(time.time() * 1000)),
                        "actor_id": self.user_id,
                        "client_mutation_id": str(random.randint(1, 99))
                    },
                    "useDefaultActor": False,
                    "scale": 1
                }
                
                # Build complete payload
                payload = {
                    'av': self.user_id,
                    '__user': self.user_id,
                    '__a': '1',
                    '__req': hex(random.randint(1, 99))[2:],
                    '__hs': str(int(time.time())),
                    'dpr': '1',
                    '__ccg': 'EXCELLENT',
                    '__rev': str(random.randint(1000000, 9999999)),
                    '__s': '',
                    '__hsi': '',
                    '__comet_req': '15',
                    'fb_dtsg': self.fb_dtsg,
                    'jazoest': self.jazoest,
                    'lsd': self.lsd if self.lsd else '',
                    'fb_api_caller_class': 'RelayModern',
                    'fb_api_req_friendly_name': 'CometUFIFeedbackReactMutation',
                    'variables': json.dumps(variables),
                    'server_timestamps': 'true',
                    'doc_id': doc_id
                }
                
                response = self.session.post(
                    'https://www.facebook.com/api/graphql/',
                    data=payload,
                    timeout=25
                )
                
                if response.status_code == 200:
                    text = response.text
                    text = re.sub(r'^\s*for\s*\(\s*;;\s*\)\s*;?', '', text)
                    
                    try:
                        result = json.loads(text)
                        
                        # Check for errors
                        if 'errors' in result:
                            error = result['errors'][0]
                            error_msg = error.get('message', 'Unknown error')
                            error_code = error.get('code', 0)
                            
                            # Handle specific errors
                            if 'not found' in error_msg.lower() or error_code == 1675030:
                                if attempt < len(doc_ids) - 1:
                                    continue
                                return False, "❌ Post not found"
                            
                            # Scraping detection
                            if 'scraping' in error_msg.lower() or 'security' in error_msg.lower():
                                if self.errors < self.max_errors:
                                    self.errors += 1
                                    time.sleep(3)
                                    if self.initialize_tokens():
                                        return self.react_to_post(post_id, reaction_type)
                                return False, "❌ Security check"
                            
                            # Session/token issues
                            if 'session' in error_msg.lower() or 'token' in error_msg.lower():
                                if self.errors < self.max_errors:
                                    self.errors += 1
                                    if self.initialize_tokens():
                                        return self.react_to_post(post_id, reaction_type)
                                return False, "❌ Session expired"
                            
                            if attempt == len(doc_ids) - 1:
                                return False, f"❌ {error_msg[:45]}"
                            continue
                        
                        # Success check
                        if 'data' in result:
                            data = result.get('data', {})
                            if data and any(key for key in data.keys() if 'react' in key.lower()):
                                self.errors = 0
                                return True, f"✓ {reaction_type}"
                        
                        # Assume success if no errors
                        self.errors = 0
                        return True, f"✓ {reaction_type}"
                        
                    except json.JSONDecodeError:
                        if 'success' in text.lower() or len(text) > 100:
                            return True, f"✓ {reaction_type}"
                        if attempt < len(doc_ids) - 1:
                            continue
                        return False, "❌ Parse error"
                
                elif response.status_code == 400:
                    if attempt < len(doc_ids) - 1:
                        continue
                    return False, "❌ Bad request"
                elif response.status_code == 401:
                    return False, "❌ Unauthorized"
                else:
                    if attempt < len(doc_ids) - 1:
                        continue
                    return False, f"❌ HTTP {response.status_code}"
                    
            except requests.exceptions.Timeout:
                if attempt < len(doc_ids) - 1:
                    time.sleep(1)
                    continue
                return False, "❌ Timeout"
            except Exception as e:
                if attempt < len(doc_ids) - 1:
                    continue
                return False, f"❌ {str(e)[:35]}"
        
        return False, "❌ All attempts failed"

def worker(cookie, post_id, reaction_type, thread_id):
    """Worker function for threading"""
    try:
        fb = FBAutoReact(cookie)
        
        if not fb.user_id:
            return thread_id, False, f"[{thread_id}] ❌ Invalid cookie", "INVALID_COOKIE"
        
        if not fb.initialized:
            return thread_id, False, f"[{thread_id}] [{fb.user_id}] ❌ Failed to initialize", "INIT_FAILED"
        
        success, message = fb.react_to_post(post_id, reaction_type)
        status = f"[{thread_id}] [{fb.user_id}] {message}"
        error_type = None if success else "REACTION_FAILED"
        
        return thread_id, success, status, error_type
        
    except Exception as e:
        return thread_id, False, f"[{thread_id}] ❌ {str(e)[:50]}", "EXCEPTION"

def banner():
    print("""
╔════════════════════════════════════════════════════╗
║     FB Auto React v3.0 - Enhanced Edition         ║
║     ✓ Updated token extraction (2025)             ║
║     ✓ Enhanced error handling                     ║
║     ✓ Multiple fallback mechanisms                ║
║     ✓ Improved post ID detection                  ║
╚════════════════════════════════════════════════════╝
    """)

def extract_post_id(url_or_id):
    """Quick extract post ID from URL"""
    url_or_id = url_or_id.strip()
    
    # Already valid format
    if url_or_id.replace('_', '').isdigit() or url_or_id.startswith('pfbid'):
        return url_or_id
    
    try:
        # Parse URL
        parsed = urlparse(url_or_id)
        params = parse_qs(parsed.query)
        
        # story_fbid format
        if 'story_fbid' in params and 'id' in params:
            return f"{params['id'][0]}_{params['story_fbid'][0]}"
        
        # /posts/ format
        if '/posts/' in url_or_id:
            match = re.search(r'/posts/([^/?&]+)', url_or_id)
            if match:
                return match.group(1)
        
        # pfbid format
        if 'pfbid' in url_or_id:
            match = re.search(r'pfbid[\w]+', url_or_id)
            if match:
                return match.group(0)
        
        # Numeric ID
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
            with open('cookies.txt', 'r', encoding='utf-8') as f:
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
        print("\n❌ No cookies provided!")
        return
    
    print(f"\n✓ Total: {len(cookies)} cookie(s)")
    
    print("\n[*] Enter post URL or ID:")
    print("   Examples:")
    print("   - https://www.facebook.com/PAGE/posts/123456789")
    print("   - https://www.facebook.com/profile/posts/pfbid123")
    print("   - pfbid02S5uMnXYZ123")
    
    post_input = input("\n[?] Post: ").strip()
    
    if not post_input:
        print("\n❌ Post URL/ID required!")
        return
    
    post_id = extract_post_id(post_input)
    print(f"✓ Using Post ID: {post_id}")
    
    print("\n[*] Select Reaction:")
    print("1.👍 LIKE    2.❤️ LOVE    3.🤗 CARE    4.😂 HAHA")
    print("5.😮 WOW     6.😢 SAD     7.😡 ANGRY")
    
    choice = input("\n[?] Choose (1-7, default=1): ").strip() or '1'
    reactions = {
        '1': 'LIKE', '2': 'LOVE', '3': 'CARE',
        '4': 'HAHA', '5': 'WOW', '6': 'SAD', '7': 'ANGRY'
    }
    reaction = reactions.get(choice, 'LIKE')
    
    threads = input("[?] Threads (1-10, default=5): ").strip() or '5'
    try:
        threads = min(max(int(threads), 1), 10)
    except:
        threads = 5
    
    print("\n" + "="*65)
    print("Starting Auto React...")
    print(f"Post: {post_id}")
    print(f"Reaction: {reaction}")
    print(f"Accounts: {len(cookies)}")
    print(f"Threads: {threads}")
    print("="*65 + "\n")
    
    success_count = 0
    failed_count = 0
    errors = {'INVALID_COOKIE': 0, 'INIT_FAILED': 0, 'REACTION_FAILED': 0, 'EXCEPTION': 0}
    
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [
            executor.submit(worker, cookie, post_id, reaction, i)
            for i, cookie in enumerate(cookies, 1)
        ]
        
        for future in as_completed(futures):
            tid, ok, msg, err_type = future.result()
            print(msg)
            
            if ok:
                success_count += 1
            else:
                failed_count += 1
                if err_type:
                    errors[err_type] += 1
            
            time.sleep(0.05)
    
    elapsed_time = time.time() - start_time
    
    print("\n" + "="*65)
    print("FINAL SUMMARY")
    print("="*65)
    print(f"✓ Successful: {success_count}")
    print(f"✗ Failed: {failed_count}")
    print(f"Total Accounts: {len(cookies)}")
    print(f"Success Rate: {(success_count/len(cookies)*100):.1f}%")
    print(f"Time Elapsed: {elapsed_time:.2f}s")
    
    if failed_count > 0:
        print("\n[Error Breakdown]")
        for err_type, count in errors.items():
            if count > 0:
                print(f"  - {err_type}: {count}")
    
    print("="*65)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Interrupted by user")
    except Exception as e:
        print(f"\n❌ Critical Error: {str(e)}")
        import traceback
        traceback.print_exc()
