#!/usr/bin/env python3
"""
Facebook Auto React Tool v4.2 - Fixed Post Not Found Issue
Enhanced feedback_id extraction with better pfbid handling
"""

import requests
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, parse_qs, unquote
import random
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class FBAutoReact:
    def __init__(self, cookie):
        self.cookie = cookie.strip()
        self.session = self.create_session()
        self.user_id = self.extract_user_id()
        self.user_name = None
        self.fb_dtsg = None
        self.jazoest = None
        self.lsd = None
        self.revision = None
        self.api_packs = None
        self.errors = 0
        self.max_errors = 3
        
        self.session.headers.update({
            'authority': 'www.facebook.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'no-cache',
            'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'cookie': self.cookie
        })
        
        self.initialized = self.login()
    
    def create_session(self):
        """Create session with retry strategy"""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=15,
            pool_maxsize=30,
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
    
    def extract_user_name(self, html):
        """Extract user name from Facebook page"""
        try:
            patterns = [
                r'"NAME":"([^"]+)"',
                r'"name":"([^"]+)"[^}]*"__typename":"User"',
                r'"short_name":"([^"]+)"',
                r'"full_name":"([^"]+)"',
                r',"name":"([^"]+)","firstName"',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, html)
                if match:
                    name = match.group(1)
                    try:
                        name = name.encode().decode('unicode_escape')
                    except:
                        pass
                    return name
            
            meta_match = re.search(r'<title>([^<]+)</title>', html)
            if meta_match:
                title = meta_match.group(1)
                name = title.replace(' | Facebook', '').strip()
                if name and len(name) < 100:
                    return name
            
        except Exception as e:
            print(f"[DEBUG] Extract name error: {str(e)}")
        
        return "Unknown User"
    
    def login(self):
        """Login and get tokens + user info"""
        if not self.user_id:
            print("[DEBUG] ❌ No c_user in cookie")
            return False
        
        try:
            print(f"[DEBUG] Loading cookie for UID: {self.user_id}...")
            
            response = self.session.get(
                'https://www.facebook.com/',
                timeout=30,
                allow_redirects=True
            )
            
            if response.status_code != 200:
                print(f"[DEBUG] ❌ HTTP {response.status_code}")
                return False
            
            html = response.text
            
            if 'login' in response.url.lower() or 'checkpoint' in response.url.lower():
                print(f"[DEBUG] ❌ Cookie expired or checkpoint")
                return False
            
            self.user_name = self.extract_user_name(html)
            print(f"[DEBUG] ✓ Found user: {self.user_name}")
            
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
                    print(f"[DEBUG] ✓ Got fb_dtsg: {self.fb_dtsg[:20]}...")
                    break
            
            if not self.fb_dtsg:
                print("[DEBUG] ❌ Failed to extract fb_dtsg")
                return self.fallback_token_extraction()
            
            lsd_patterns = [
                r'"LSD"[^}]*"token":"([^"]+)"',
                r'"lsd":"([^"]+)"',
                r'name="lsd"\s+value="([^"]+)"'
            ]
            
            for pattern in lsd_patterns:
                match = re.search(pattern, html)
                if match:
                    self.lsd = match.group(1)
                    self.session.headers['x-fb-lsd'] = self.lsd
                    print(f"[DEBUG] ✓ Got LSD token")
                    break
            
            rev_match = re.search(r'"__rev":(\d+)', html)
            if rev_match:
                self.revision = rev_match.group(1)
                print(f"[DEBUG] ✓ Got revision: {self.revision}")
            
            if self.user_id:
                self.jazoest = '2' + str(sum(ord(c) for c in self.user_id))
                print(f"[DEBUG] ✓ Generated jazoest")
            
            self.session.headers.update({
                'content-type': 'application/x-www-form-urlencoded',
                'x-fb-friendly-name': 'CometUFIFeedbackReactMutation'
            })
            
            success = bool(self.fb_dtsg and self.user_id)
            
            if success:
                print(f"[DEBUG] ✅ Login successful!")
                print(f"[DEBUG] UID: {self.user_id}")
                print(f"[DEBUG] Name: {self.user_name}")
            
            return success
            
        except requests.exceptions.Timeout:
            print("[DEBUG] ❌ Timeout during login")
            return False
        except Exception as e:
            print(f"[DEBUG] ❌ Login error: {str(e)}")
            return False
    
    def fallback_token_extraction(self):
        """Fallback method using AJAX endpoint"""
        try:
            print("[DEBUG] Trying fallback token extraction...")
            
            response = self.session.get(
                'https://www.facebook.com/ajax/dtsg/?__a=1',
                timeout=20
            )
            
            if response.status_code == 200:
                text = response.text
                text = re.sub(r'^\s*for\s*\(\s*;;\s*\)\s*;?', '', text)
                
                try:
                    data = json.loads(text)
                    if 'payload' in data and 'token' in data['payload']:
                        self.fb_dtsg = data['payload']['token']
                        print(f"[DEBUG] ✓ Got fb_dtsg from fallback: {self.fb_dtsg[:20]}...")
                        
                        if self.user_id:
                            self.jazoest = '2' + str(sum(ord(c) for c in self.user_id))
                        
                        return True
                except:
                    pass
            
            print("[DEBUG] ❌ Fallback extraction failed")
            return False
            
        except Exception as e:
            print(f"[DEBUG] Fallback error: {str(e)}")
            return False
    
    def handle_new_packs_error(self, api_packs):
        """Handle new_packs error"""
        try:
            print(f"[DEBUG] Handling new_packs error...")
            self.api_packs = api_packs
            self.errors = 0
            
            if self.login():
                print("[DEBUG] ✓ Re-logged in successfully")
                return True
            
            return False
            
        except Exception as e:
            print(f"[DEBUG] handle_new_packs error: {str(e)}")
            return False
    
    def get_feedback_id(self, post_url_or_id):
        """
        ENHANCED feedback ID extraction
        Handles pfbid format properly by using it directly as feedback_id
        """
        try:
            post_url_or_id = str(post_url_or_id).strip()
            
            print(f"[DEBUG] Processing post ID: {post_url_or_id[:50]}...")
            
            # If it's a pfbid, use it directly!
            if post_url_or_id.startswith('pfbid'):
                print(f"[DEBUG] Using pfbid directly as feedback_id: {post_url_or_id}")
                return post_url_or_id
            
            # If numeric with underscore (already proper format)
            if '_' in post_url_or_id and post_url_or_id.replace('_', '').isdigit():
                if len(post_url_or_id) > 15:
                    print(f"[DEBUG] Using numeric feedback_id: {post_url_or_id}")
                    return post_url_or_id
            
            # If pure numeric and long enough
            if post_url_or_id.isdigit() and len(post_url_or_id) >= 15:
                print(f"[DEBUG] Using numeric ID: {post_url_or_id}")
                return post_url_or_id
            
            # Build full URL if needed
            if not post_url_or_id.startswith('http'):
                post_url_or_id = f'https://www.facebook.com/{post_url_or_id}'
            
            # Parse URL parameters first (fastest method)
            parsed = urlparse(post_url_or_id)
            params = parse_qs(parsed.query)
            
            # Check for story_fbid in URL
            if 'story_fbid' in params:
                story_fbid = params['story_fbid'][0]
                
                # If story_fbid is pfbid, use it directly
                if story_fbid.startswith('pfbid'):
                    print(f"[DEBUG] Extracted pfbid from URL: {story_fbid}")
                    return story_fbid
                
                # If numeric story_fbid with user id
                if 'id' in params:
                    feedback_id = f"{params['id'][0]}_{story_fbid}"
                    print(f"[DEBUG] Constructed feedback_id: {feedback_id}")
                    return feedback_id
            
            # Extract pfbid from URL path
            pfbid_match = re.search(r'pfbid[\w\-]+', post_url_or_id)
            if pfbid_match:
                pfbid = pfbid_match.group(0)
                print(f"[DEBUG] Extracted pfbid from path: {pfbid}")
                return pfbid
            
            # Fetch page to extract feedback_id
            print(f"[DEBUG] Fetching post page to extract feedback_id...")
            response = self.session.get(post_url_or_id, timeout=30, allow_redirects=True)
            
            if response.status_code != 200:
                print(f"[DEBUG] Failed to fetch page: HTTP {response.status_code}")
                return post_url_or_id
            
            html = response.text
            
            # Try to extract pfbid from HTML first
            pfbid_patterns = [
                r'"post_id":"(pfbid[\w\-]+)"',
                r'"feedback_id":"(pfbid[\w\-]+)"',
                r'"id":"(pfbid[\w\-]+)"[^}]{0,100}"__typename":"Post"',
                r'story_fbid=(pfbid[\w\-]+)',
            ]
            
            for pattern in pfbid_patterns:
                match = re.search(pattern, html)
                if match:
                    pfbid = match.group(1)
                    print(f"[DEBUG] Found pfbid in HTML: {pfbid}")
                    return pfbid
            
            # Fallback to numeric ID extraction
            numeric_patterns = [
                r'"feedback_id":"(\d{15,})"',
                r'"feedbackID":"(\d{15,})"',
                r'"legacy_story_hideable_id":"(\d{15,})"',
                r'"post_id":"(\d{15,})"',
                r'"top_level_post_id":"(\d{15,})"',
                r'story_fbid=(\d+)[^0-9]+id=(\d+)',
                r'"id":"(\d{15,})"[^}]{0,200}"__typename":"Post"',
            ]
            
            for pattern in numeric_patterns:
                matches = re.findall(pattern, html)
                if matches:
                    if isinstance(matches[0], tuple):
                        feedback_id = f"{matches[0][1]}_{matches[0][0]}"
                        print(f"[DEBUG] Constructed from tuple: {feedback_id}")
                        return feedback_id
                    
                    longest = max(matches, key=lambda x: len(str(x)))
                    if len(str(longest)) >= 15:
                        print(f"[DEBUG] Extracted numeric ID: {longest}")
                        return str(longest)
            
            print(f"[DEBUG] ⚠️ Could not extract feedback_id, using original")
            
        except Exception as e:
            print(f"[DEBUG] get_feedback_id error: {str(e)}")
        
        return post_url_or_id
    
    def react_to_post(self, post_id, reaction_type='LIKE'):
        """React to post with proper error handling"""
        
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
        
        print(f"[DEBUG] Using feedback_id: {feedback_id}")
        
        # Latest working doc_ids
        doc_ids = [
            '8047049165356556',
            '7565960703454863',
            '6360991980619959',
            '5359434074136134',
        ]
        
        for attempt, doc_id in enumerate(doc_ids):
            try:
                print(f"[DEBUG] Attempt {attempt + 1}/{len(doc_ids)} with doc_id: {doc_id}")
                
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
                        "client_mutation_id": str(random.randint(1, 999))
                    },
                    "useDefaultActor": False,
                    "scale": 1
                }
                
                # Build payload
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
                
                response = self.session.post(
                    'https://www.facebook.com/api/graphql/',
                    data=payload,
                    timeout=40
                )
                
                print(f"[DEBUG] Response status: {response.status_code}")
                
                if response.status_code == 200:
                    text = response.text
                    text = re.sub(r'^\s*for\s*\(\s*;;\s*\)\s*;?', '', text)
                    
                    try:
                        result = json.loads(text)
                        
                        # Error handling
                        if 'errors' in result:
                            error = result['errors'][0]
                            error_msg = error.get('message', '')
                            error_code = error.get('code', 0)
                            
                            print(f"[DEBUG] Error: {error_msg} (code: {error_code})")
                            
                            if error_code == 1357004:
                                if attempt < len(doc_ids) - 1:
                                    continue
                                return False, "❌ Invalid request"
                            
                            # Handle renew_values / new_packs
                            if 'renew_values' in error_msg.lower() or 'new_packs' in error_msg.lower():
                                if self.errors < self.max_errors:
                                    self.errors += 1
                                    api_packs = error.get('packs', None)
                                    
                                    if self.handle_new_packs_error(api_packs):
                                        time.sleep(1)
                                        return self.react_to_post(post_id, reaction_type)
                                
                                return False, "❌ Session expired"
                            
                            if 'scraping' in error_msg.lower():
                                return False, "❌ Scraping detected"
                            
                            # Post not found - try next doc_id
                            if 'not found' in error_msg.lower() or 'does not exist' in error_msg.lower():
                                if attempt < len(doc_ids) - 1:
                                    print(f"[DEBUG] Post not found with this doc_id, trying next...")
                                    continue
                                return False, "❌ Post not found / Invalid feedback_id"
                            
                            if attempt == len(doc_ids) - 1:
                                return False, f"❌ {error_msg[:40]}"
                            continue
                        
                        # Success
                        if 'data' in result:
                            print(f"[DEBUG] ✓ Reaction successful!")
                            self.errors = 0
                            return True, f"✓ {reaction_type}"
                        
                        self.errors = 0
                        return True, f"✓ {reaction_type}"
                        
                    except json.JSONDecodeError:
                        if len(text) > 50:
                            return True, f"✓ {reaction_type}"
                        if attempt < len(doc_ids) - 1:
                            continue
                        return False, "❌ Invalid response"
                
                elif response.status_code == 401:
                    return False, "❌ Unauthorized"
                else:
                    if attempt < len(doc_ids) - 1:
                        continue
                    return False, f"❌ HTTP {response.status_code}"
                    
            except requests.exceptions.Timeout:
                print(f"[DEBUG] Timeout on attempt {attempt + 1}")
                if attempt < len(doc_ids) - 1:
                    time.sleep(2)
                    continue
                return False, "❌ Timeout"
            except Exception as e:
                print(f"[DEBUG] Exception: {str(e)}")
                if attempt < len(doc_ids) - 1:
                    continue
                return False, f"❌ {str(e)[:30]}"
        
        return False, "❌ All attempts failed"

def worker(cookie, post_id, reaction_type, thread_id):
    """Worker function"""
    try:
        fb = FBAutoReact(cookie)
        
        if not fb.user_id:
            return thread_id, False, f"[{thread_id}] ❌ Invalid cookie (no c_user)", "INVALID_COOKIE", None, None
        
        if not fb.initialized:
            return thread_id, False, f"[{thread_id}] [{fb.user_id}] ❌ Login failed", "LOGIN_FAILED", fb.user_id, fb.user_name
        
        success, message = fb.react_to_post(post_id, reaction_type)
        status = f"[{thread_id}] [{fb.user_id}] [{fb.user_name}] {message}"
        error_type = None if success else "REACTION_FAILED"
        
        return thread_id, success, status, error_type, fb.user_id, fb.user_name
        
    except Exception as e:
        return thread_id, False, f"[{thread_id}] ❌ {str(e)[:50]}", "EXCEPTION", None, None

def banner():
    print("""
╔═══════════════════════════════════════════════════════╗
║  FB Auto React v4.2 - Fixed Post Not Found Issue     ║
║  ✓ Enhanced pfbid support                            ║
║  ✓ Multiple doc_id fallback attempts                 ║
║  ✓ Better feedback_id extraction                     ║
╚═══════════════════════════════════════════════════════╝
    """)

def extract_post_id(url_or_id):
    """Extract post ID from URL - preserving pfbid format"""
    url_or_id = url_or_id.strip()
    
    # If already pfbid or numeric, return as-is
    if url_or_id.startswith('pfbid') or (url_or_id.replace('_', '').isdigit() and len(url_or_id) > 10):
        return url_or_id
    
    try:
        parsed = urlparse(url_or_id)
        params = parse_qs(parsed.query)
        
        # Extract story_fbid (could be pfbid)
        if 'story_fbid' in params:
            story_fbid = params['story_fbid'][0]
            # If pfbid, return directly
            if story_fbid.startswith('pfbid'):
                return story_fbid
            # If numeric with id param
            if 'id' in params:
                return f"{params['id'][0]}_{story_fbid}"
            return story_fbid
        
        # Extract from path
        if '/posts/' in url_or_id:
            match = re.search(r'/posts/([^/?&]+)', url_or_id)
            if match:
                return match.group(1)
        
        # Extract pfbid from anywhere in URL
        pfbid_match = re.search(r'pfbid[\w\-]+', url_or_id)
        if pfbid_match:
            return pfbid_match.group(0)
        
        # Extract numeric ID
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
    
    # Test first cookie
    print("\n[*] Testing first cookie...")
    print("="*70)
    test_fb = FBAutoReact(cookies[0])
    if test_fb.initialized:
        print(f"✅ Cookie loaded successfully!")
        print(f"   UID: {test_fb.user_id}")
        print(f"   Name: {test_fb.user_name}")
    else:
        print(f"❌ First cookie failed to load. Please check your cookies!")
        return
    print("="*70)
    
    print("\n[*] Enter post URL or ID:")
    print("   Examples:")
    print("   - https://www.facebook.com/PAGE/posts/pfbid0XYZ...")
    print("   - pfbid0SwNibUBSrr2L5t4qgQCZka9iJQFxRe8k1GwSiYAjnAmK...")
    print("   - https://www.facebook.com/story.php?story_fbid=XXX&id=YYY")
    
    post_input = input("\n[?] Post: ").strip()
    
    if not post_input:
        print("\n❌ Post URL/ID required!")
        return
    
    post_id = extract_post_id(post_input)
    print(f"✓ Extracted Post ID: {post_id[:60]}...")
    
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
    print(f"Post: {post_id[:60]}...")
    print(f"Reaction: {reaction}")
    print(f"Accounts: {len(cookies)}")
    print(f"Threads: {threads}")
    print("="*70 + "\n")
    
    success_count = 0
    failed_count = 0
    errors = {'INVALID_COOKIE': 0, 'LOGIN_FAILED': 0, 'REACTION_FAILED': 0, 'EXCEPTION': 0}
    loaded_users = []
    
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [
            executor.submit(worker, cookie, post_id, reaction, i)
            for i, cookie in enumerate(cookies, 1)
        ]
        
        for future in as_completed(futures):
            tid, ok, msg, err_type, uid, name = future.result()
            print(msg)
            
            if uid and name:
                loaded_users.append((uid, name))
            
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
    
    if loaded_users:
        print(f"\n[Loaded Users: {len(loaded_users)}]")
        for uid, name in loaded_users[:5]:
            print(f"  • {uid} - {name}")
        if len(loaded_users) > 5:
            print(f"  ... and {len(loaded_users) - 5} more")
    
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
