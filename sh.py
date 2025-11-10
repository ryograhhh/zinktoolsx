#!/usr/bin/env python3
"""
Facebook Auto React Tool v5.0 - Multiple Methods Approach
Uses different APIs and fallback mechanisms to ensure it works
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
        self.user_name = None
        self.fb_dtsg = None
        self.jazoest = None
        self.lsd = None
        self.revision = None
        self.hsi = None
        self.spin_r = None
        self.spin_b = None
        self.spin_t = None
        self.errors = 0
        self.max_errors = 3
        
        self.session.headers.update({
            'authority': 'www.facebook.com',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'no-cache',
            'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
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
            pool_connections=20,
            pool_maxsize=40,
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
        except:
            pass
        
        return "User"
    
    def login(self):
        """Login and extract all tokens"""
        if not self.user_id:
            return False
        
        try:
            print(f"[INFO] Loading UID: {self.user_id}")
            
            response = self.session.get(
                'https://www.facebook.com/',
                timeout=30,
                allow_redirects=True
            )
            
            if response.status_code != 200:
                return False
            
            html = response.text
            
            if 'login' in response.url.lower() or 'checkpoint' in response.url.lower():
                print(f"[ERROR] Cookie expired!")
                return False
            
            self.user_name = self.extract_user_name(html)
            
            # Extract all required tokens
            dtsg_match = re.search(r'"DTSGInitialData"[^}]*"token":"([^"]+)"', html)
            if dtsg_match:
                self.fb_dtsg = dtsg_match.group(1)
            
            if not self.fb_dtsg:
                dtsg_match = re.search(r'"dtsg"\s*:\s*\{\s*"token"\s*:\s*"([^"]+)"', html)
                if dtsg_match:
                    self.fb_dtsg = dtsg_match.group(1)
            
            lsd_match = re.search(r'"LSD"[^}]*"token":"([^"]+)"', html)
            if lsd_match:
                self.lsd = lsd_match.group(1)
            
            rev_match = re.search(r'"__rev":(\d+)', html)
            if rev_match:
                self.revision = rev_match.group(1)
            
            hsi_match = re.search(r'"hsi":"([^"]+)"', html)
            if hsi_match:
                self.hsi = hsi_match.group(1)
            
            spin_r_match = re.search(r'"__spin_r":(\d+)', html)
            if spin_r_match:
                self.spin_r = spin_r_match.group(1)
            
            spin_b_match = re.search(r'"__spin_b":"([^"]+)"', html)
            if spin_b_match:
                self.spin_b = spin_b_match.group(1)
            
            spin_t_match = re.search(r'"__spin_t":(\d+)', html)
            if spin_t_match:
                self.spin_t = spin_t_match.group(1)
            
            if self.user_id:
                self.jazoest = '2' + str(sum(ord(c) for c in self.user_id))
            
            if self.fb_dtsg:
                print(f"[SUCCESS] Logged in as: {self.user_name} (UID: {self.user_id})")
                return True
            
            return False
            
        except Exception as e:
            print(f"[ERROR] Login failed: {str(e)}")
            return False
    
    def resolve_post_id(self, post_url_or_id):
        """
        Resolve pfbid or URL to actual numeric post ID
        This is the KEY to making it work!
        """
        try:
            original = str(post_url_or_id).strip()
            
            # If already numeric format, return it
            if original.replace('_', '').isdigit() and len(original) > 15:
                return original
            
            # Build full URL
            if not original.startswith('http'):
                if original.startswith('pfbid'):
                    # Try different URL formats for pfbid
                    urls_to_try = [
                        f'https://www.facebook.com/permalink.php?story_fbid={original}',
                        f'https://m.facebook.com/story.php?story_fbid={original}',
                    ]
                else:
                    urls_to_try = [f'https://www.facebook.com/{original}']
            else:
                urls_to_try = [original]
            
            # Try each URL
            for url in urls_to_try:
                try:
                    print(f"[INFO] Resolving post ID from: {url[:60]}...")
                    
                    response = self.session.get(url, timeout=20, allow_redirects=True)
                    
                    if response.status_code != 200:
                        continue
                    
                    html = response.text
                    
                    # CRITICAL: Extract the actual numeric post ID
                    # This is what Facebook uses internally!
                    patterns = [
                        r'"post_id":"(\d{15,})"',
                        r'"feedback_id":"(\d{15,})"',
                        r'"feedbackID":"(\d{15,})"',
                        r'"legacy_story_hideable_id":"(\d{15,})"',
                        r'"top_level_post_id":"(\d{15,})"',
                        r'story_fbid=(\d{15,})',
                        r'"target_id":(\d{15,})',
                    ]
                    
                    for pattern in patterns:
                        matches = re.findall(pattern, html)
                        if matches:
                            post_id = max(matches, key=len)
                            print(f"[SUCCESS] Resolved to numeric ID: {post_id}")
                            return post_id
                    
                except Exception as e:
                    print(f"[DEBUG] Try failed: {str(e)[:50]}")
                    continue
            
            print(f"[WARNING] Could not resolve to numeric ID, using original")
            return original
            
        except Exception as e:
            print(f"[ERROR] resolve_post_id: {str(e)}")
            return post_url_or_id
    
    def react_method_1(self, feedback_id, reaction_id):
        """Method 1: Using GraphQL API (newest)"""
        try:
            doc_ids = [
                '7565960703454863',
                '8047049165356556',
                '6360991980619959',
            ]
            
            for doc_id in doc_ids:
                variables = {
                    "input": {
                        "feedback_id": feedback_id,
                        "feedback_reaction_id": reaction_id,
                        "feedback_source": "OBJECT",
                        "is_tracking_encrypted": False,
                        "actor_id": self.user_id,
                        "client_mutation_id": str(random.randint(1, 9999))
                    },
                    "useDefaultActor": False
                }
                
                payload = {
                    'fb_dtsg': self.fb_dtsg,
                    'jazoest': self.jazoest,
                    'variables': json.dumps(variables),
                    'doc_id': doc_id,
                    '__user': self.user_id,
                    '__a': '1',
                    '__req': hex(random.randint(1, 50))[2:],
                    '__rev': self.revision or '1000000',
                }
                
                if self.lsd:
                    payload['lsd'] = self.lsd
                
                response = self.session.post(
                    'https://www.facebook.com/api/graphql/',
                    data=payload,
                    timeout=30,
                    headers={
                        'content-type': 'application/x-www-form-urlencoded',
                        'x-fb-friendly-name': 'CometUFIFeedbackReactMutation'
                    }
                )
                
                if response.status_code == 200:
                    text = response.text.replace('for(;;);', '')
                    
                    try:
                        result = json.loads(text)
                        if 'errors' not in result and 'data' in result:
                            return True
                    except:
                        pass
        except:
            pass
        
        return False
    
    def react_method_2(self, feedback_id, reaction_id):
        """Method 2: Using UFI (Unified Feedback Interface) - older but stable"""
        try:
            payload = {
                'fb_dtsg': self.fb_dtsg,
                'jazoest': self.jazoest,
                'feedback_id': feedback_id,
                'reaction_type': reaction_id,
                '__user': self.user_id,
                '__a': '1',
                '__req': hex(random.randint(1, 50))[2:],
            }
            
            if self.lsd:
                payload['lsd'] = self.lsd
            
            response = self.session.post(
                'https://www.facebook.com/ufi/reaction/profile/browser/',
                data=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return True
        except:
            pass
        
        return False
    
    def react_method_3(self, feedback_id, reaction_id):
        """Method 3: Using AJAX endpoint - most compatible"""
        try:
            payload = {
                'fb_dtsg': self.fb_dtsg,
                'jazoest': self.jazoest,
                'ft_ent_identifier': feedback_id,
                'reaction_type': reaction_id,
                '__user': self.user_id,
                '__a': '1',
                '__req': hex(random.randint(1, 50))[2:],
            }
            
            if self.lsd:
                payload['lsd'] = self.lsd
            
            response = self.session.post(
                'https://www.facebook.com/ajax/ufi/modify.php',
                data=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                text = response.text
                if 'error' not in text.lower() or 'success' in text.lower():
                    return True
        except:
            pass
        
        return False
    
    def react_to_post(self, post_id, reaction_type='LIKE'):
        """React to post using multiple methods"""
        
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
        
        # CRITICAL: Resolve to numeric ID first
        feedback_id = self.resolve_post_id(post_id)
        
        print(f"[INFO] Attempting reaction with feedback_id: {feedback_id}")
        
        # Try all methods
        methods = [
            ("GraphQL API", self.react_method_1),
            ("UFI Endpoint", self.react_method_2),
            ("AJAX Endpoint", self.react_method_3),
        ]
        
        for method_name, method in methods:
            try:
                print(f"[INFO] Trying {method_name}...")
                if method(feedback_id, reaction_id):
                    print(f"[SUCCESS] Reacted using {method_name}!")
                    return True, f"✓ {reaction_type}"
                time.sleep(0.5)
            except Exception as e:
                print(f"[DEBUG] {method_name} failed: {str(e)[:40]}")
                continue
        
        return False, "❌ All methods failed"

def worker(cookie, post_id, reaction_type, thread_id):
    """Worker function"""
    try:
        fb = FBAutoReact(cookie)
        
        if not fb.user_id:
            return thread_id, False, f"[{thread_id}] ❌ Invalid cookie", "INVALID_COOKIE", None, None
        
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
║  FB Auto React v5.0 - Multi-Method Approach          ║
║  ✓ 3 Different reaction methods                      ║
║  ✓ Automatic pfbid resolution to numeric ID          ║
║  ✓ Works with both old and new post formats          ║
╚═══════════════════════════════════════════════════════╝
    """)

def extract_post_id(url_or_id):
    """Quick extract - will be resolved later"""
    url_or_id = url_or_id.strip()
    
    # Return as-is, will resolve in react_to_post
    if url_or_id.startswith('pfbid') or url_or_id.startswith('http'):
        return url_or_id
    
    # Try to extract from URL if provided
    try:
        if 'facebook.com' in url_or_id:
            parsed = urlparse(url_or_id)
            params = parse_qs(parsed.query)
            
            if 'story_fbid' in params:
                return params['story_fbid'][0]
            
            if '/posts/' in url_or_id:
                match = re.search(r'/posts/([^/?&]+)', url_or_id)
                if match:
                    return match.group(1)
            
            match = re.search(r'pfbid[\w\-]+', url_or_id)
            if match:
                return match.group(0)
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
        print("\n❌ No cookies!")
        return
    
    print(f"\n✓ Total: {len(cookies)} cookie(s)")
    
    # Test first cookie
    print("\n[*] Testing first cookie...")
    print("="*70)
    test_fb = FBAutoReact(cookies[0])
    if test_fb.initialized:
        print(f"✅ Cookie working!")
    else:
        print(f"❌ Cookie failed!")
        return
    print("="*70)
    
    print("\n[*] Enter post URL or ID:")
    print("   Any format: pfbid, numeric ID, or full URL")
    
    post_input = input("\n[?] Post: ").strip()
    
    if not post_input:
        print("\n❌ Post required!")
        return
    
    post_id = extract_post_id(post_input)
    
    print("\n[*] Reaction:")
    print("1.👍 LIKE  2.❤️ LOVE  3.🤗 CARE  4.😂 HAHA")
    print("5.😮 WOW   6.😢 SAD   7.😡 ANGRY")
    
    choice = input("\n[?] Choose (1-7): ").strip() or '1'
    reactions = {
        '1': 'LIKE', '2': 'LOVE', '3': 'CARE',
        '4': 'HAHA', '5': 'WOW', '6': 'SAD', '7': 'ANGRY'
    }
    reaction = reactions.get(choice, 'LIKE')
    
    threads = input("[?] Threads (1-10): ").strip() or '3'
    try:
        threads = min(max(int(threads), 1), 10)
    except:
        threads = 3
    
    print("\n" + "="*70)
    print(f"Starting - {reaction} reaction on {len(cookies)} account(s)")
    print("="*70 + "\n")
    
    success_count = 0
    failed_count = 0
    
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [
            executor.submit(worker, cookie, post_id, reaction, i)
            for i, cookie in enumerate(cookies, 1)
        ]
        
        for future in as_completed(futures):
            tid, ok, msg, err_type, uid, name = future.result()
            print(msg)
            
            if ok:
                success_count += 1
            else:
                failed_count += 1
            
            time.sleep(0.1)
    
    elapsed = time.time() - start_time
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"✓ Success: {success_count}")
    print(f"✗ Failed: {failed_count}")
    print(f"Rate: {(success_count/len(cookies)*100):.1f}%")
    print(f"Time: {elapsed:.2f}s")
    print("="*70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Stopped")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
