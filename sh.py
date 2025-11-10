#!/usr/bin/env python3
"""
Facebook Auto React Tool v5.1 - Enhanced DTSG Getter
- Enhanced fb_dtsg extraction from Node.js method
- No threading - sequential processing
- Better error handling
- Fixed scraping detection
"""

import requests
import json
import re
import time
from urllib.parse import urlparse, parse_qs, unquote
import random

class FBAutoReact:
    def __init__(self, cookie):
        self.cookie = cookie.strip()
        self.session = requests.Session()
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
            
        except:
            pass
        
        return "Unknown User"
    
    def get_fb_dtsg_enhanced(self):
        """Enhanced fb_dtsg getter using Node.js method"""
        try:
            print(f"[*] Getting fb_dtsg using enhanced method...")
            
            # Method from Node.js code
            response = self.session.get(
                'https://www.facebook.com/ajax/dtsg/?__a=1',
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"[!] HTTP {response.status_code}")
                return None
            
            text = response.text
            
            # Remove for(;;); prefix if exists
            text = re.sub(r'^\s*for\s*\(\s*;;\s*\)\s*;?', '', text)
            
            try:
                data = json.loads(text)
                
                # Extract token from payload
                if 'payload' in data and 'token' in data['payload']:
                    token = data['payload']['token']
                    print(f"[✓] Got fb_dtsg: {token[:20]}...")
                    return token
                
                # Try alternative paths
                if 'data' in data:
                    if isinstance(data['data'], dict) and 'token' in data['data']:
                        token = data['data']['token']
                        print(f"[✓] Got fb_dtsg (alt path): {token[:20]}...")
                        return token
                
            except json.JSONDecodeError as e:
                print(f"[!] JSON decode error: {str(e)}")
                
                # Try regex extraction as fallback
                token_match = re.search(r'"token"\s*:\s*"([^"]+)"', text)
                if token_match:
                    token = token_match.group(1)
                    print(f"[✓] Got fb_dtsg (regex): {token[:20]}...")
                    return token
            
            print(f"[!] Could not extract token from response")
            return None
            
        except Exception as e:
            print(f"[!] Enhanced dtsg error: {str(e)}")
            return None
    
    def fix_scraping_detection(self, html):
        """Fix scraping detection if detected"""
        try:
            if 'FBScrapingWarningCometApp.entrypoint' in html or '"entrypoint":"FBScrapingWarningCometApp' in html:
                print(f"[⚠] Scraping detection found, attempting fix...")
                
                time.sleep(2)
                response = self.session.get('https://www.facebook.com/', timeout=30)
                
                if response.status_code == 200:
                    new_html = response.text
                    if 'FBScrapingWarningCometApp' not in new_html:
                        print(f"[✓] Scraping detection fixed!")
                        return True, new_html
                
                print(f"[!] Could not fix scraping detection")
                return False, html
            
            return True, html
            
        except Exception as e:
            print(f"[!] Fix scraping error: {str(e)}")
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
        """Enhanced login with better fb_dtsg extraction"""
        if not self.user_id:
            print("[!] No c_user in cookie")
            return False
        
        try:
            print(f"[*] Loading cookie for UID: {self.user_id}...")
            
            # Get fb_dtsg using enhanced method first
            self.fb_dtsg = self.get_fb_dtsg_enhanced()
            
            if not self.fb_dtsg:
                print("[!] Enhanced method failed, trying standard method...")
                
                response = self.session.get(
                    'https://www.facebook.com/',
                    timeout=30,
                    allow_redirects=True
                )
                
                if response.status_code != 200:
                    print(f"[!] HTTP {response.status_code}")
                    return False
                
                html = response.text
                
                # Check scraping detection
                scraping_ok, html = self.fix_scraping_detection(html)
                
                # Check if logged in
                if 'login' in response.url.lower() or 'checkpoint' in response.url.lower():
                    print(f"[!] Cookie expired or checkpoint")
                    return False
                
                # Extract user name
                self.user_name = self.extract_user_name(html)
                print(f"[✓] Found user: {self.user_name}")
                
                # Extract fb_dtsg from HTML
                dtsg_patterns = [
                    r'"DTSGInitialData"[^}]*"token":"([^"]+)"',
                    r'"dtsg"\s*:\s*\{\s*"token"\s*:\s*"([^"]+)"',
                    r'\["DTSGInitialData",[^,]*,\{"token":"([^"]+)"',
                    r'name="fb_dtsg"\s+value="([^"]+)"',
                ]
                
                for pattern in dtsg_patterns:
                    match = re.search(pattern, html)
                    if match:
                        self.fb_dtsg = match.group(1)
                        print(f"[✓] Got fb_dtsg: {self.fb_dtsg[:20]}...")
                        break
                
                if not self.fb_dtsg:
                    print("[!] Failed to extract fb_dtsg")
                    return False
            else:
                # Get user info from main page
                response = self.session.get('https://www.facebook.com/', timeout=30)
                if response.status_code == 200:
                    self.user_name = self.extract_user_name(response.text)
                    print(f"[✓] Found user: {self.user_name}")
            
            # Get additional tokens
            response = self.session.get('https://www.facebook.com/', timeout=30)
            if response.status_code == 200:
                html = response.text
                
                # Extract LSD
                lsd_patterns = [
                    r'"LSD"[^}]*"token":"([^"]+)"',
                    r'"lsd":"([^"]+)"',
                ]
                
                for pattern in lsd_patterns:
                    match = re.search(pattern, html)
                    if match:
                        self.lsd = match.group(1)
                        self.session.headers['x-fb-lsd'] = self.lsd
                        print(f"[✓] Got LSD token")
                        break
                
                # Extract revision
                rev_match = re.search(r'"__rev":(\d+)', html)
                if rev_match:
                    self.revision = rev_match.group(1)
                    print(f"[✓] Got revision: {self.revision}")
            
            # Generate jazoest
            if self.user_id:
                self.jazoest = '2' + str(sum(ord(c) for c in self.user_id))
                print(f"[✓] Generated jazoest")
            
            success = bool(self.fb_dtsg and self.user_id)
            
            if success:
                print(f"[✓] Login successful!")
                print(f"    UID: {self.user_id}")
                print(f"    Name: {self.user_name}")
            
            return success
            
        except requests.exceptions.Timeout:
            print("[!] Timeout during login")
            return False
        except Exception as e:
            print(f"[!] Login error: {str(e)}")
            return False
    
    def handle_error_1357004(self):
        """Handle error 1357004 - renew_values"""
        try:
            print(f"[*] Handling error 1357004 (renew_values)...")
            self.errors = 0
            
            # Get fresh fb_dtsg
            self.fb_dtsg = self.get_fb_dtsg_enhanced()
            
            if self.fb_dtsg:
                # Get fresh revision
                response = self.session.get('https://www.facebook.com/', timeout=30)
                
                if response.status_code == 200:
                    html = response.text
                    
                    rev_match = re.search(r'"__rev":(\d+)', html)
                    if rev_match:
                        self.revision = rev_match.group(1)
                        print(f"[✓] Got new revision")
                    
                    lsd_match = re.search(r'"LSD"[^}]*"token":"([^"]+)"', html)
                    if lsd_match:
                        self.lsd = lsd_match.group(1)
                        self.session.headers['x-fb-lsd'] = self.lsd
                        print(f"[✓] Got new LSD")
                    
                    print("[✓] Tokens renewed successfully")
                    return True
            
            return False
            
        except Exception as e:
            print(f"[!] handle_error_1357004 error: {str(e)}")
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
            
            print(f"[*] Fetching post to extract feedback_id...")
            
            # Fetch page
            response = self.session.get(post_link, timeout=30, allow_redirects=True)
            
            if response.status_code != 200:
                print(f"[!] HTTP {response.status_code} when fetching post")
                return post_link
            
            html = response.text
            
            # Enhanced patterns for feedback_id
            patterns = [
                r'"feedback_id":"(\d+)"',
                r'"feedbackID":"(\d+)"',
                r'"legacy_story_hideable_id":"(\d+)"',
                r'"post_id":"(\d+)"',
                r'"top_level_post_id":"(\d+)"',
                r'story_fbid=(\d+)[^0-9]+id=(\d+)',
                r'"id":"(\d+)"[^}]{0,200}"__typename":"Post"',
                r'"feedback"\s*:\s*\{\s*"id"\s*:\s*"(\d+)"',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, html)
                if matches:
                    if isinstance(matches[0], tuple):
                        feedback_id = f"{matches[0][1]}_{matches[0][0]}"
                        print(f"[✓] Extracted feedback_id: {feedback_id}")
                        return feedback_id
                    longest = max(matches, key=lambda x: len(str(x)))
                    if len(str(longest)) >= 15:
                        print(f"[✓] Extracted feedback_id: {longest}")
                        return str(longest)
            
            print(f"[!] Could not extract feedback_id from post")
            
        except Exception as e:
            print(f"[!] get_feedback_id error: {str(e)}")
        
        return post_link
    
    def react_to_post(self, post_link, reaction_type='LIKE'):
        """React with GraphQL only payload"""
        
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
                print(f"[*] Attempting reaction with doc_id: {doc_id}...")
                
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
                
                # Payload matching the image format
                payload_data = {
                    'user_id': self.user_id,
                    'revision': self.revision if self.revision else '1000000',
                    'fb_dtsg': self.fb_dtsg,
                    'jazoest': self.jazoest
                }
                
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
                            
                            print(f"[!] API Error: {error_msg} (code: {error_code})")
                            
                            # Handle error 1357004 - renew_values
                            if error_code == 1357004:
                                if self.errors < self.max_errors:
                                    self.errors += 1
                                    print(f"[*] Error 1357004 detected, renewing tokens...")
                                    
                                    if self.handle_error_1357004():
                                        time.sleep(1)
                                        return self.react_to_post(post_link, reaction_type)
                                
                                return False, "Tokens expired (1357004)"
                            
                            # Handle renew_values / new_packs
                            if 'renew_values' in error_msg.lower() or 'new_packs' in error_msg.lower():
                                if self.errors < self.max_errors:
                                    self.errors += 1
                                    
                                    if self.handle_error_1357004():
                                        time.sleep(1)
                                        return self.react_to_post(post_link, reaction_type)
                                
                                return False, "Session expired"
                            
                            if 'scraping' in error_msg.lower():
                                return False, "Scraping detected"
                            
                            if 'not found' in error_msg.lower():
                                if attempt < len(doc_ids) - 1:
                                    print(f"[*] Post not found with this doc_id, trying next...")
                                    continue
                                return False, "Post not found"
                            
                            if attempt == len(doc_ids) - 1:
                                return False, f"{error_msg[:40]}"
                            continue
                        
                        # Success
                        if 'data' in result:
                            self.errors = 0
                            print(f"[✓] Reaction successful: {reaction_type}")
                            return True, f"{reaction_type}"
                        
                        self.errors = 0
                        print(f"[✓] Reaction successful: {reaction_type}")
                        return True, f"{reaction_type}"
                        
                    except json.JSONDecodeError:
                        if len(text) > 50:
                            print(f"[✓] Reaction successful: {reaction_type}")
                            return True, f"{reaction_type}"
                        if attempt < len(doc_ids) - 1:
                            continue
                        return False, "Invalid response"
                
                elif response.status_code == 401:
                    return False, "Unauthorized"
                else:
                    print(f"[!] HTTP {response.status_code}")
                    if attempt < len(doc_ids) - 1:
                        continue
                    return False, f"HTTP {response.status_code}"
                    
            except requests.exceptions.Timeout:
                if attempt < len(doc_ids) - 1:
                    print(f"[!] Timeout, trying next doc_id...")
                    time.sleep(2)
                    continue
                return False, "Timeout"
            except Exception as e:
                print(f"[!] Error: {str(e)}")
                if attempt < len(doc_ids) - 1:
                    continue
                return False, f"{str(e)[:30]}"
        
        return False, "All attempts failed"

def banner():
    print("""
╔═══════════════════════════════════════════════════════╗
║  FB Auto React v5.1 - Enhanced DTSG Getter            ║
║  ✓ Enhanced fb_dtsg extraction                        ║
║  ✓ No threading - sequential processing               ║
║  ✓ Better error messages                              ║
║  ✓ Fixed scraping detection                           ║
╚═══════════════════════════════════════════════════════╝
    """)

def main():
    banner()
    
    print("\n[*] Enter your Facebook cookie:")
    print("    Format: datr=xxx;sb=xxx;c_user=xxx;xs=xxx;fr=xxx")
    print()
    
    cookie = input("Cookie: ").strip()
    
    if not cookie:
        print("\n[!] Cookie required!")
        return
    
    if 'c_user=' not in cookie:
        print("\n[!] Invalid cookie - must contain c_user")
        return
    
    print("\n" + "="*70)
    
    fb = FBAutoReact(cookie)
    
    if not fb.initialized:
        print("\n[!] Failed to initialize. Please check your cookie!")
        return
    
    print("="*70)
    
    print("\n[*] Enter post link:")
    print("    Examples:")
    print("    - https://www.facebook.com/PAGE/posts/123456789")
    print("    - https://www.facebook.com/story.php?story_fbid=XXX&id=YYY")
    
    post_link = input("\n[?] Post link: ").strip()
    
    if not post_link:
        print("\n[!] Post link required!")
        return
    
    print("\n[*] Select Reaction:")
    print("    1. LIKE    2. LOVE    3. CARE    4. HAHA")
    print("    5. WOW     6. SAD     7. ANGRY")
    
    choice = input("\n[?] Choose (1-7, default=1): ").strip() or '1'
    reactions = {
        '1': 'LIKE', '2': 'LOVE', '3': 'CARE',
        '4': 'HAHA', '5': 'WOW', '6': 'SAD', '7': 'ANGRY'
    }
    reaction = reactions.get(choice, 'LIKE')
    
    print("\n" + "="*70)
    print(f"[*] Reacting to post...")
    print(f"    Post: {post_link[:60]}...")
    print(f"    Reaction: {reaction}")
    print("="*70 + "\n")
    
    start_time = time.time()
    
    success, message = fb.react_to_post(post_link, reaction)
    
    elapsed_time = time.time() - start_time
    
    print("\n" + "="*70)
    print("RESULT")
    print("="*70)
    
    if success:
        print(f"[✓] SUCCESS: {message}")
    else:
        print(f"[✗] FAILED: {message}")
    
    print(f"[⏱] Time: {elapsed_time:.2f}s")
    print("="*70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!] Interrupted by user")
    except Exception as e:
        print(f"\n[!] Critical Error: {str(e)}")
        import traceback
        traceback.print_exc()
