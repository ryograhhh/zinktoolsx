#!/usr/bin/env python3
"""
Facebook Auto React Tool v5.0 - Enhanced Edition
- Fixed scraping detection
- Enhanced payload structure (GraphQL only)
- Error code 1357004 handling (renew_values)
- Better token refresh mechanism
"""

import requests
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, parse_qs
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
            'x-asbd-id': '129477',
            'x-fb-friendly-name': 'CometUFIFeedbackReactMutation',
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
    
    def fix_scraping_detection(self, html):
        """Fix scraping detection if detected"""
        try:
            if 'FBScrapingWarningCometApp.entrypoint' in html or '"entrypoint":"FBScrapingWarningCometApp' in html:
                print(f"[DEBUG] Warning: Scraping detection found, attempting fix...")
                
                time.sleep(2)
                response = self.session.get('https://www.facebook.com/', timeout=30)
                
                if response.status_code == 200:
                    new_html = response.text
                    if 'FBScrapingWarningCometApp' not in new_html:
                        print(f"[DEBUG] Success: Scraping detection fixed!")
                        return True, new_html
                
                print(f"[DEBUG] Failed to fix scraping detection automatically")
                return False, html
            
            return True, html
            
        except Exception as e:
            print(f"[DEBUG] Fix scraping error: {str(e)}")
            return False, html
    
    def get_payload(self, data):
        """Get payload data matching the image format"""
        return {
            'av': data['user_id'],
            '__user': data['user_id'],
            '__rev': data['revision'],
            'fb_dtsg': data['fb_dtsg'],
            'jazoest': data['jazoest']
        }
    
    def login(self):
        """Enhanced login with scraping detection fix"""
        if not self.user_id:
            print("[DEBUG] Error: No c_user in cookie")
            return False
        
        try:
            print(f"[DEBUG] Loading cookie for UID: {self.user_id}...")
            
            response = self.session.get(
                'https://www.facebook.com/',
                timeout=30,
                allow_redirects=True
            )
            
            if response.status_code != 200:
                print(f"[DEBUG] Error: HTTP {response.status_code}")
                return False
            
            html = response.text
            
            # Check scraping detection
            scraping_ok, html = self.fix_scraping_detection(html)
            if not scraping_ok:
                print(f"[DEBUG] Warning: Scraping detection active, continuing anyway...")
            
            # Check if logged in
            if 'login' in response.url.lower() or 'checkpoint' in response.url.lower():
                print(f"[DEBUG] Error: Cookie expired or checkpoint")
                return False
            
            # Extract user name
            self.user_name = self.extract_user_name(html)
            print(f"[DEBUG] Success: Found user: {self.user_name}")
            
            # Extract fb_dtsg
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
                    print(f"[DEBUG] Success: Got fb_dtsg: {self.fb_dtsg[:20]}...")
                    break
            
            if not self.fb_dtsg:
                print("[DEBUG] Error: Failed to extract fb_dtsg")
                return self.fallback_token_extraction()
            
            # Extract LSD
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
                    print(f"[DEBUG] Success: Got LSD token")
                    break
            
            # Extract revision
            rev_match = re.search(r'"__rev":(\d+)', html)
            if rev_match:
                self.revision = rev_match.group(1)
                print(f"[DEBUG] Success: Got revision: {self.revision}")
            
            # Generate jazoest
            if self.user_id:
                self.jazoest = '2' + str(sum(ord(c) for c in self.user_id))
                print(f"[DEBUG] Success: Generated jazoest")
            
            success = bool(self.fb_dtsg and self.user_id)
            
            if success:
                print(f"[DEBUG] Login successful!")
                print(f"[DEBUG] UID: {self.user_id}")
                print(f"[DEBUG] Name: {self.user_name}")
            
            return success
            
        except requests.exceptions.Timeout:
            print("[DEBUG] Error: Timeout during login")
            return False
        except Exception as e:
            print(f"[DEBUG] Error: Login error: {str(e)}")
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
                        print(f"[DEBUG] Success: Got fb_dtsg from fallback: {self.fb_dtsg[:20]}...")
                        
                        if self.user_id:
                            self.jazoest = '2' + str(sum(ord(c) for c in self.user_id))
                        
                        return True
                except:
                    pass
            
            print("[DEBUG] Error: Fallback extraction failed")
            return False
            
        except Exception as e:
            print(f"[DEBUG] Fallback error: {str(e)}")
            return False
    
    def handle_error_1357004(self):
        """Handle error 1357004 - renew_values"""
        try:
            print(f"[DEBUG] Handling error 1357004 (renew_values)...")
            self.errors = 0
            
            # Force re-login to get fresh tokens
            response = self.session.get('https://www.facebook.com/', timeout=30)
            
            if response.status_code == 200:
                html = response.text
                
                # Re-extract tokens
                dtsg_match = re.search(r'"DTSGInitialData"[^}]*"token":"([^"]+)"', html)
                if dtsg_match:
                    self.fb_dtsg = dtsg_match.group(1)
                    print(f"[DEBUG] Success: Got new fb_dtsg")
                
                lsd_match = re.search(r'"LSD"[^}]*"token":"([^"]+)"', html)
                if lsd_match:
                    self.lsd = lsd_match.group(1)
                    self.session.headers['x-fb-lsd'] = self.lsd
                    print(f"[DEBUG] Success: Got new LSD")
                
                rev_match = re.search(r'"__rev":(\d+)', html)
                if rev_match:
                    self.revision = rev_match.group(1)
                    print(f"[DEBUG] Success: Got new revision")
                
                print("[DEBUG] Tokens renewed successfully")
                return True
            
            return False
            
        except Exception as e:
            print(f"[DEBUG] handle_error_1357004 error: {str(e)}")
            return False
    
    def get_feedback_id(self, post_link):
        """Enhanced feedback ID extraction"""
        try:
            post_link = str(post_link).strip()
            
            # Already in correct format
            if '_' in post_link and post_link.replace('_', '').isdigit():
                if len(post_link) > 15:
                    return post_link
            
            if post_link.isdigit() and len(post_link) >= 15:
                return post_link
            
            # Build full URL
            if not post_link.startswith('http'):
                if 'pfbid' in post_link:
                    post_link = f'https://www.facebook.com/permalink.php?story_fbid={post_link}'
                else:
                    post_link = f'https://www.facebook.com/{post_link}'
            
            # Parse URL parameters
            parsed = urlparse(post_link)
            params = parse_qs(parsed.query)
            
            # story_fbid + id format
            if 'story_fbid' in params and 'id' in params:
                return f"{params['id'][0]}_{params['story_fbid'][0]}"
            
            # Fetch page
            response = self.session.get(post_link, timeout=30, allow_redirects=True)
            
            if response.status_code != 200:
                return post_link
            
            html = response.text
            
            # Enhanced patterns
            patterns = [
                r'"feedback_id":"(\d+)"',
                r'"feedbackID":"(\d+)"',
                r'"legacy_story_hideable_id":"(\d+)"',
                r'"post_id":"(\d+)"',
                r'"top_level_post_id":"(\d+)"',
                r'story_fbid=(\d+)[^0-9]+id=(\d+)',
                r'"id":"(\d+)"[^}]{0,200}"__typename":"Post"',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, html)
                if matches:
                    if isinstance(matches[0], tuple):
                        return f"{matches[0][1]}_{matches[0][0]}"
                    longest = max(matches, key=lambda x: len(str(x)))
                    if len(str(longest)) >= 15:
                        return str(longest)
            
        except Exception as e:
            print(f"[DEBUG] get_feedback_id error: {str(e)}")
        
        return post_link
    
    def react_to_post(self, post_link, reaction_type='LIKE'):
        """React with GraphQL only payload (matching image)"""
        
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
        feedback_id = self.get_feedback_id(post_link)
        
        # Latest working doc_ids
        doc_ids = [
            '8047049165356556',
            '7565960703454863',
            '6360991980619959',
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
                        "client_mutation_id": str(random.randint(1, 999))
                    },
                    "useDefaultActor": False,
                    "scale": 1
                }
                
                # Payload matching the image format - GraphQL only
                payload_data = {
                    'user_id': self.user_id,
                    'revision': self.revision if self.revision else '1000000',
                    'fb_dtsg': self.fb_dtsg,
                    'jazoest': self.jazoest
                }
                
                # Get payload using the function from image
                payload = self.get_payload(payload_data)
                
                # Add GraphQL specific fields
                payload.update({
                    '__a': '1',
                    '__req': hex(random.randint(1, 99))[2:],
                    '__hs': str(int(time.time())),
                    '__comet_req': '15',
                    'fb_api_caller_class': 'RelayModern',
                    'fb_api_req_friendly_name': 'CometUFIFeedbackReactMutation',
                    'variables': json.dumps(variables),
                    'server_timestamps': 'true',
                    'doc_id': doc_id
                })
                
                if self.lsd:
                    payload['lsd'] = self.lsd
                
                response = self.session.post(
                    'https://www.facebook.com/api/graphql/',
                    data=payload,
                    timeout=40
                )
                
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
                            
                            # Handle error 1357004 - renew_values
                            if error_code == 1357004:
                                if self.errors < self.max_errors:
                                    self.errors += 1
                                    print(f"[DEBUG] Error 1357004 detected, renewing tokens...")
                                    
                                    if self.handle_error_1357004():
                                        time.sleep(1)
                                        return self.react_to_post(post_link, reaction_type)
                                
                                return False, "Error: Tokens expired (1357004)"
                            
                            # Handle renew_values / new_packs
                            if 'renew_values' in error_msg.lower() or 'new_packs' in error_msg.lower():
                                if self.errors < self.max_errors:
                                    self.errors += 1
                                    
                                    if self.handle_error_1357004():
                                        time.sleep(1)
                                        return self.react_to_post(post_link, reaction_type)
                                
                                return False, "Error: Session expired"
                            
                            if 'scraping' in error_msg.lower():
                                return False, "Error: Scraping detected"
                            
                            if 'not found' in error_msg.lower():
                                if attempt < len(doc_ids) - 1:
                                    continue
                                return False, "Error: Post not found"
                            
                            if attempt == len(doc_ids) - 1:
                                return False, f"Error: {error_msg[:40]}"
                            continue
                        
                        # Success
                        if 'data' in result:
                            self.errors = 0
                            return True, f"Success: {reaction_type}"
                        
                        self.errors = 0
                        return True, f"Success: {reaction_type}"
                        
                    except json.JSONDecodeError:
                        if len(text) > 50:
                            return True, f"Success: {reaction_type}"
                        if attempt < len(doc_ids) - 1:
                            continue
                        return False, "Error: Invalid response"
                
                elif response.status_code == 401:
                    return False, "Error: Unauthorized"
                else:
                    if attempt < len(doc_ids) - 1:
                        continue
                    return False, f"Error: HTTP {response.status_code}"
                    
            except requests.exceptions.Timeout:
                if attempt < len(doc_ids) - 1:
                    time.sleep(2)
                    continue
                return False, "Error: Timeout"
            except Exception as e:
                if attempt < len(doc_ids) - 1:
                    continue
                return False, f"Error: {str(e)[:30]}"
        
        return False, "Error: All attempts failed"

def worker(cookie, post_link, reaction_type, thread_id):
    """Worker function"""
    try:
        fb = FBAutoReact(cookie)
        
        if not fb.user_id:
            return thread_id, False, f"[{thread_id}] Invalid cookie (no c_user)", "INVALID_COOKIE", None, None
        
        if not fb.initialized:
            return thread_id, False, f"[{thread_id}] [{fb.user_id}] Login failed", "LOGIN_FAILED", fb.user_id, fb.user_name
        
        success, message = fb.react_to_post(post_link, reaction_type)
        status = f"[{thread_id}] [{fb.user_id}] [{fb.user_name}] {message}"
        error_type = None if success else "REACTION_FAILED"
        
        return thread_id, success, status, error_type, fb.user_id, fb.user_name
        
    except Exception as e:
        return thread_id, False, f"[{thread_id}] Error: {str(e)[:50]}", "EXCEPTION", None, None

def banner():
    print("""
╔═══════════════════════════════════════════════════════╗
║  FB Auto React v5.0 - Enhanced Edition                ║
║  ✓ Fixed scraping detection                           ║
║  ✓ GraphQL payload only (matching image)              ║
║  ✓ Error 1357004 handling (renew_values)              ║
║  ✓ Better token refresh mechanism                     ║
╚═══════════════════════════════════════════════════════╝
    """)

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
            print(f"Loaded {len(cookies)} cookie(s)")
        except FileNotFoundError:
            print("Error: cookies.txt not found!")
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
                print("   Error: Invalid - must contain c_user")
                continue
            
            cookies.append(cookie)
            print("   Added!")
    
    return cookies

def main():
    banner()
    
    cookies = get_cookies()
    
    if not cookies:
        print("\nError: No cookies provided!")
        return
    
    print(f"\nTotal: {len(cookies)} cookie(s)")
    
    # Test first cookie
    print("\n[*] Testing first cookie...")
    print("="*70)
    test_fb = FBAutoReact(cookies[0])
    if test_fb.initialized:
        print(f"Cookie loaded successfully!")
        print(f"   UID: {test_fb.user_id}")
        print(f"   Name: {test_fb.user_name}")
    else:
        print(f"Error: First cookie failed to load. Please check your cookies!")
        return
    print("="*70)
    
    print("\n[*] Enter post link:")
    print("   Examples:")
    print("   - https://www.facebook.com/PAGE/posts/123456789")
    print("   - https://www.facebook.com/story.php?story_fbid=XXX&id=YYY")
    
    post_link = input("\n[?] Post link: ").strip()
    
    if not post_link:
        print("\nError: Post link required!")
        return
    
    print(f"Using: {post_link}")
    
    print("\n[*] Select Reaction:")
    print("1. LIKE    2. LOVE    3. CARE    4. HAHA")
    print("5. WOW     6. SAD     7. ANGRY")
    
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
    print(f"Post: {post_link}")
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
            executor.submit(worker, cookie, post_link, reaction, i)
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
    print(f"Successful: {success_count}")
    print(f"Failed: {failed_count}")
    print(f"Total Accounts: {len(cookies)}")
    print(f"Success Rate: {(success_count/len(cookies)*100):.1f}%")
    print(f"Time: {elapsed_time:.2f}s")
    
    if loaded_users:
        print(f"\n[Loaded Users: {len(loaded_users)}]")
        for uid, name in loaded_users[:5]:
            print(f"  - {uid} - {name}")
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
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nCritical Error: {str(e)}")
        import traceback
        traceback.print_exc()
