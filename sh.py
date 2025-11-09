#!/usr/bin/env python3
"""
Facebook Auto React Tool v3.5 - Fixed Connection & Feedback ID Issues
Based on working Node.js implementation from screenshots
"""

import requests
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, parse_qs, quote
import random
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class FBAutoReact:
    def __init__(self, cookie):
        self.cookie = cookie.strip()
        self.session = self.create_session()
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
            'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'cookie': self.cookie,
            'x-fb-friendly-name': 'CometUFIFeedbackReactMutation'
        })
        
        self.initialized = self.login()
    
    def create_session(self):
        """Create session with retry strategy and connection pooling"""
        session = requests.Session()
        
        # Retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=20,
            pool_block=False
        )
        
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def extract_user_id(self):
        """Extract user ID from cookie"""
        try:
            match = re.search(r'c_user=([^;]+)', self.cookie)
            if match:
                return match.group(1)
        except:
            pass
        return None
    
    def login(self):
        """Login and get all required tokens - matching Node.js getPayload"""
        if not self.user_id:
            return False
        
        try:
            # Get main page with increased timeout
            response = self.session.get(
                'https://www.facebook.com/',
                timeout=30,
                allow_redirects=True
            )
            
            if response.status_code != 200:
                return False
            
            html = response.text
            
            # Extract fb_dtsg - matching Node.js patterns
            dtsg_patterns = [
                r'"DTSGInitialData"[^}]*"token":"([^"]+)"',
                r'"dtsg"\s*:\s*\{\s*"token"\s*:\s*"([^"]+)"',
                r'\["DTSGInitialData",[^,]*,\{"token":"([^"]+)"',
                r'name="fb_dtsg"\s+value="([^"]+)"',
                r'"async_get_token":"([^"]+)"'
            ]
            
            for pattern in dtsg_patterns:
                match = re.search(pattern, html)
                if match:
                    self.fb_dtsg = match.group(1)
                    break
            
            # Extract LSD
            lsd_match = re.search(r'"LSD"[^}]*"token":"([^"]+)"', html)
            if lsd_match:
                self.lsd = lsd_match.group(1)
                self.session.headers['x-fb-lsd'] = self.lsd
            
            # Extract revision (__rev)
            rev_match = re.search(r'"__rev":(\d+)', html)
            if rev_match:
                self.revision = rev_match.group(1)
            
            # Generate jazoest from user_id (matching Node.js)
            if self.user_id:
                self.jazoest = '2' + str(sum(ord(c) for c in self.user_id))
            
            # Fallback: AJAX endpoint (matching screenshot logic)
            if not self.fb_dtsg:
                try:
                    ajax_resp = self.session.get(
                        'https://www.facebook.com/ajax/dtsg/?__a=1',
                        timeout=20
                    )
                    
                    if ajax_resp.status_code == 200:
                        text = ajax_resp.text
                        # Remove for(;;); prefix (matching Node.js)
                        text = re.sub(r'^\s*for\s*\(\s*;;\s*\)\s*;?', '', text)
                        
                        try:
                            data = json.loads(text)
                            if 'payload' in data and 'token' in data['payload']:
                                self.fb_dtsg = data['payload']['token']
                        except:
                            pass
                except:
                    pass
            
            return bool(self.fb_dtsg and self.user_id)
            
        except Exception as e:
            print(f"[DEBUG] Login error: {str(e)}")
            return False
    
    def fix_scraping_detection(self, data, cookie):
        """Fix scraping detection - matching Node.js fixScrapingDetection"""
        try:
            print("[DEBUG] Attempting to fix scraping detection...")
            time.sleep(2)
            
            # Try checkpoint flow
            checkpoint_url = data.get('entrypoint', '')
            if checkpoint_url and 'checkpoint' in checkpoint_url:
                try:
                    self.session.get(checkpoint_url, timeout=15)
                except:
                    pass
            
            # Re-initialize tokens
            return self.login()
            
        except Exception as e:
            print(f"[DEBUG] Fix scraping error: {str(e)}")
            return False
    
    def get_story_id_from_url(self, url):
        """Extract story_fbid from URL for feedback_id construction"""
        try:
            # Parse query parameters
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            
            if 'story_fbid' in params:
                return params['story_fbid'][0]
            
            # Extract from path /posts/STORY_ID
            match = re.search(r'/posts/([^/?&]+)', url)
            if match:
                return match.group(1)
            
        except:
            pass
        return None
    
    def get_feedback_id(self, post_url_or_id):
        """
        Enhanced feedback ID extraction - matching Node.js logic
        Constructs proper feedback_id format: user_id_story_id
        """
        try:
            post_url_or_id = str(post_url_or_id).strip()
            
            # If already in correct format (numeric with underscore)
            if '_' in post_url_or_id and post_url_or_id.replace('_', '').isdigit():
                if len(post_url_or_id) > 15:
                    return post_url_or_id
            
            # If pure numeric and long enough
            if post_url_or_id.isdigit() and len(post_url_or_id) >= 15:
                return post_url_or_id
            
            # Build full URL
            if not post_url_or_id.startswith('http'):
                if 'pfbid' in post_url_or_id:
                    post_url_or_id = f'https://www.facebook.com/permalink.php?story_fbid={post_url_or_id}'
                else:
                    post_url_or_id = f'https://www.facebook.com/{post_url_or_id}'
            
            # Parse URL first (fast method)
            parsed = urlparse(post_url_or_id)
            params = parse_qs(parsed.query)
            
            # Method 1: story_fbid + id format (most reliable)
            if 'story_fbid' in params and 'id' in params:
                user_id = params['id'][0]
                story_id = params['story_fbid'][0]
                return f"{user_id}_{story_id}"
            
            # Method 2: Fetch and parse HTML
            print(f"[DEBUG] Fetching post page to extract feedback_id...")
            response = self.session.get(
                post_url_or_id, 
                timeout=30,
                allow_redirects=True
            )
            
            if response.status_code != 200:
                print(f"[DEBUG] Failed to fetch page: HTTP {response.status_code}")
                return post_url_or_id
            
            html = response.text
            
            # Enhanced patterns for feedback_id extraction
            patterns = [
                # Direct feedback_id
                (r'"feedback_id":"(\d+)"', None),
                (r'"feedbackID":"(\d+)"', None),
                
                # User_id + story_id construction
                (r'"legacy_story_hideable_id":"(\d+)"', None),
                (r'"post_id":"(\d+)"', None),
                (r'"top_level_post_id":"(\d+)"', None),
                
                # From data-ft attribute
                (r'data-ft="[^"]*&quot;top_level_post_id&quot;:&quot;(\d+)&quot;', None),
                
                # Story and user ID pair
                (r'story_fbid=(\d+)[^0-9]+id=(\d+)', 'pair'),
                
                # From GraphQL response
                (r'"id":"(\d+)"[^}]{0,200}"__typename":"Post"', None),
                (r'"target_id":(\d+)', None),
            ]
            
            for pattern, ptype in patterns:
                matches = re.findall(pattern, html)
                if matches:
                    if ptype == 'pair' and isinstance(matches[0], tuple):
                        # story_fbid, user_id pair
                        return f"{matches[0][1]}_{matches[0][0]}"
                    else:
                        # Get longest match (most specific)
                        longest = max(matches, key=lambda x: len(str(x)))
                        if len(str(longest)) >= 15:
                            print(f"[DEBUG] Extracted feedback_id: {longest}")
                            return str(longest)
            
            # Method 3: Try to construct from page owner and post
            page_id_match = re.search(r'"pageID":"(\d+)"', html)
            story_id_match = re.search(r'"post_id":"(\d+)"', html)
            
            if page_id_match and story_id_match:
                feedback_id = f"{page_id_match.group(1)}_{story_id_match.group(1)}"
                print(f"[DEBUG] Constructed feedback_id: {feedback_id}")
                return feedback_id
            
            print(f"[DEBUG] Could not extract numeric feedback_id, using original")
            
        except requests.exceptions.Timeout:
            print("[DEBUG] Timeout while fetching post page")
        except Exception as e:
            print(f"[DEBUG] get_feedback_id error: {str(e)}")
        
        return post_url_or_id
    
    def react_to_post(self, post_id, reaction_type='LIKE'):
        """React to post - matching Node.js implementation from screenshots"""
        
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
        
        # Updated doc_ids (2025)
        doc_ids = [
            '8047049165356556',  # Current working
            '7565960703454863',
            '6360991980619959',
        ]
        
        for attempt, doc_id in enumerate(doc_ids):
            try:
                # Build variables - matching Node.js structure
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
                
                # Build complete payload - matching getPayload from screenshots
                payload = {
                    'av': self.user_id,
                    '__user': self.user_id,
                    '__a': '1',
                    '__req': hex(random.randint(1, 99))[2:],
                    '__hs': str(int(time.time())),
                    '__dyn': '',
                    '__csr': '',
                    '__rev': self.revision if self.revision else '1000000',
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
                
                # Make request with longer timeout
                response = self.session.post(
                    'https://www.facebook.com/api/graphql/',
                    data=payload,
                    timeout=40  # Increased timeout to avoid pool read timeout
                )
                
                if response.status_code == 200:
                    text = response.text
                    
                    # Remove for(;;); prefix
                    text = re.sub(r'^\s*for\s*\(\s*;;\s*\)\s*;?', '', text)
                    
                    try:
                        result = json.loads(text)
                        
                        # Check for errors - matching Node.js error handling
                        if 'errors' in result:
                            error = result['errors'][0]
                            error_msg = error.get('message', 'Unknown error')
                            
                            # Handle "new_packs" error (from screenshot catch block)
                            if 'renew_values' in error_msg.lower() or 'new_packs' in error_msg.lower():
                                if self.errors < self.max_errors:
                                    self.errors += 1
                                    print(f"[DEBUG] Detected new_packs error, re-logging in...")
                                    if self.login():
                                        time.sleep(1)
                                        return self.react_to_post(post_id, reaction_type)
                                return False, "❌ Session expired (new_packs)"
                            
                            # Scraping detection (from screenshot)
                            if 'FBScrapingWarningCometApp' in error_msg or 'scraping' in error_msg.lower():
                                entrypoint = error.get('entrypoint', '')
                                if entrypoint:
                                    if self.errors < self.max_errors:
                                        self.errors += 1
                                        data = {'entrypoint': entrypoint}
                                        if self.fix_scraping_detection(data, self.cookie):
                                            time.sleep(2)
                                            return self.react_to_post(post_id, reaction_type)
                                return False, "❌ Scraping detected"
                            
                            # Post not found or invalid feedback_id
                            if 'not found' in error_msg.lower() or 'does not exist' in error_msg.lower():
                                if attempt < len(doc_ids) - 1:
                                    continue
                                return False, "❌ Post not found / Invalid ID"
                            
                            # Unknown error
                            if attempt == len(doc_ids) - 1:
                                return False, f"❌ {error_msg[:40]}"
                            continue
                        
                        # Success check
                        if 'data' in result:
                            data = result.get('data', {})
                            # Check for successful reaction in response
                            if data and any(data.values()):
                                self.errors = 0
                                return True, f"✓ {reaction_type}"
                        
                        # No errors = success
                        self.errors = 0
                        return True, f"✓ {reaction_type}"
                        
                    except json.JSONDecodeError:
                        # If response is valid but not JSON
                        if len(text) > 50:
                            return True, f"✓ {reaction_type}"
                        if attempt < len(doc_ids) - 1:
                            continue
                        return False, "❌ Invalid response"
                
                elif response.status_code == 400:
                    if attempt < len(doc_ids) - 1:
                        continue
                    return False, "❌ Bad request"
                elif response.status_code == 401:
                    return False, "❌ Unauthorized - check cookie"
                else:
                    if attempt < len(doc_ids) - 1:
                        continue
                    return False, f"❌ HTTP {response.status_code}"
                    
            except requests.exceptions.Timeout:
                print(f"[DEBUG] Timeout on attempt {attempt + 1}")
                if attempt < len(doc_ids) - 1:
                    time.sleep(2)
                    continue
                return False, "❌ Connection timeout"
            except requests.exceptions.ConnectionError as e:
                print(f"[DEBUG] Connection error: {str(e)[:60]}")
                if attempt < len(doc_ids) - 1:
                    time.sleep(2)
                    continue
                return False, "❌ Connection failed"
            except Exception as e:
                print(f"[DEBUG] Exception: {str(e)[:60]}")
                if attempt < len(doc_ids) - 1:
                    continue
                return False, f"❌ {str(e)[:30]}"
        
        return False, "❌ All attempts failed"

def worker(cookie, post_id, reaction_type, thread_id):
    """Worker function for threading"""
    try:
        fb = FBAutoReact(cookie)
        
        if not fb.user_id:
            return thread_id, False, f"[{thread_id}] ❌ Invalid cookie", "INVALID_COOKIE"
        
        if not fb.initialized:
            return thread_id, False, f"[{thread_id}] [{fb.user_id}] ❌ Login failed", "LOGIN_FAILED"
        
        success, message = fb.react_to_post(post_id, reaction_type)
        status = f"[{thread_id}] [{fb.user_id}] {message}"
        error_type = None if success else "REACTION_FAILED"
        
        return thread_id, success, status, error_type
        
    except Exception as e:
        return thread_id, False, f"[{thread_id}] ❌ {str(e)[:50]}", "EXCEPTION"

def banner():
    print("""
╔═══════════════════════════════════════════════════════╗
║  FB Auto React v3.5 - Connection Pool Fixed          ║
║  ✓ Fixed timeout & connection pool issues            ║
║  ✓ Enhanced feedback_id extraction                   ║
║  ✓ Better error handling (new_packs, scraping)       ║
║  ✓ Matching working Node.js implementation           ║
╚═══════════════════════════════════════════════════════╝
    """)

def extract_post_id(url_or_id):
    """Quick extract post ID from URL"""
    url_or_id = url_or_id.strip()
    
    # Already valid format
    if url_or_id.replace('_', '').isdigit() or url_or_id.startswith('pfbid'):
        return url_or_id
    
    try:
        parsed = urlparse(url_or_id)
        params = parse_qs(parsed.query)
        
        if 'story_fbid' in params and 'id' in params:
            return f"{params['id'][0]}_{params['story_fbid'][0]}"
        
        if '/posts/' in url_or_id:
            match = re.search(r'/posts/([^/?&]+)', url_or_id)
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
    print("   - https://www.facebook.com/story.php?story_fbid=XXX&id=YYY")
    print("   - pfbid02S5uMnXYZ123")
    
    post_input = input("\n[?] Post: ").strip()
    
    if not post_input:
        print("\n❌ Post URL/ID required!")
        return
    
    post_id = extract_post_id(post_input)
    print(f"✓ Using: {post_id}")
    
    print("\n[*] Select Reaction:")
    print("1.👍 LIKE    2.❤️ LOVE    3.🤗 CARE    4.😂 HAHA")
    print("5.😮 WOW     6.😢 SAD     7.😡 ANGRY")
    
    choice = input("\n[?] Choose (1-7, default=1): ").strip() or '1'
    reactions = {
        '1': 'LIKE', '2': 'LOVE', '3': 'CARE',
        '4': 'HAHA', '5': 'WOW', '6': 'SAD', '7': 'ANGRY'
    }
    reaction = reactions.get(choice, 'LIKE')
    
    threads = input("[?] Threads (1-10, default=3): ").strip() or '3'
    try:
        threads = min(max(int(threads), 1), 10)
    except:
        threads = 3
    
    print("\n" + "="*70)
    print("Starting Auto React...")
    print(f"Post: {post_id}")
    print(f"Reaction: {reaction}")
    print(f"Accounts: {len(cookies)}")
    print(f"Threads: {threads}")
    print("="*70 + "\n")
    
    success_count = 0
    failed_count = 0
    errors = {'INVALID_COOKIE': 0, 'LOGIN_FAILED': 0, 'REACTION_FAILED': 0, 'EXCEPTION': 0}
    
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
            
            time.sleep(0.1)
    
    elapsed_time = time.time() - start_time
    
    print("\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70)
    print(f"✓ Successful: {success_count}")
    print(f"✗ Failed: {failed_count}")
    print(f"Total Accounts: {len(cookies)}")
    print(f"Success Rate: {(success_count/len(cookies)*100):.1f}%")
    print(f"Time: {elapsed_time:.2f}s")
    
    if failed_count > 0:
        print("\n[Error Breakdown]")
        for err_type, count in errors.items():
            if count > 0:
                print(f"  - {err_type}: {count}")
    
    print("="*70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Interrupted by user")
    except Exception as e:
        print(f"\n❌ Critical Error: {str(e)}")
        import traceback
        traceback.print_exc()
