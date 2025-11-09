#!/usr/bin/env python3
"""
Facebook Auto React Tool for Termux
Supports multiple accounts with threading and GraphQL API
"""

import requests
import json
import threading
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

class FBAutoReact:
    def __init__(self, cookie):
        self.cookie = cookie
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Linux; Android 11; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.104 Mobile Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': cookie,
            'x-fb-friendly-name': 'FeedbackReactMutation',
            'x-fb-lsd': self.extract_token('LSD'),
        })
        self.user_id = self.extract_user_id()
        self.fb_dtsg = self.get_fb_dtsg()
        self.jazoest = self.extract_token('jazoest')
        
    def extract_user_id(self):
        """Extract user ID from cookie"""
        try:
            if 'c_user=' in self.cookie:
                return self.cookie.split('c_user=')[1].split(';')[0]
        except:
            pass
        return None
    
    def extract_token(self, token_name):
        """Extract tokens from Facebook"""
        try:
            if token_name == 'LSD':
                r = self.session.get('https://m.facebook.com/')
                if 'LSD' in r.text:
                    return r.text.split('LSD",[],{"token":"')[1].split('"')[0]
            elif token_name == 'jazoest':
                # Generate jazoest from user_id
                return '2' + str(sum(ord(c) for c in self.user_id))
        except:
            pass
        return None
    
    def get_fb_dtsg(self):
        """Get fb_dtsg token"""
        try:
            r = self.session.get('https://m.facebook.com/')
            if 'DTSGInitialData' in r.text:
                dtsg = r.text.split('DTSGInitialData",[],{"token":"')[1].split('"')[0]
                return dtsg
        except:
            pass
        return None
    
    def react_to_post(self, post_id, reaction_type='LIKE'):
        """
        React to a Facebook post using GraphQL API
        reaction_type: LIKE, LOVE, HAHA, WOW, SAD, ANGRY, CARE
        """
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
        
        # GraphQL mutation payload
        data = {
            'fb_dtsg': self.fb_dtsg,
            'jazoest': self.jazoest,
            'fb_api_req_friendly_name': 'FeedbackReactMutation',
            'variables': json.dumps({
                'input': {
                    'attribution_id_v2': f'FeedbackReactMutation,{post_id}',
                    'feedback_id': post_id,
                    'feedback_reaction_id': reaction_id,
                    'feedback_source': 'OBJECT',
                    'is_tracking_encrypted': False,
                    'tracking': [],
                    'session_id': str(int(time.time())),
                    'actor_id': self.user_id,
                    'client_mutation_id': str(int(time.time() * 1000))
                }
            }),
            'doc_id': '5359434074136134'
        }
        
        try:
            response = self.session.post(
                'https://www.facebook.com/api/graphql/',
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'errors' not in result:
                    return True, f"✓ Reacted with {reaction_type}"
                else:
                    return False, f"✗ Error: {result.get('errors', 'Unknown error')}"
            else:
                return False, f"✗ HTTP {response.status_code}"
                
        except Exception as e:
            return False, f"✗ Exception: {str(e)}"

def load_cookies(cookie_file='cookies.txt'):
    """Load cookies from file"""
    cookies = []
    try:
        with open(cookie_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    cookies.append(line)
    except FileNotFoundError:
        print(f"[!] Cookie file '{cookie_file}' not found!")
        return []
    return cookies

def worker(cookie, post_id, reaction_type, thread_id):
    """Worker function for threading"""
    try:
        fb = FBAutoReact(cookie)
        if not fb.user_id:
            return thread_id, False, "Invalid cookie"
        
        success, message = fb.react_to_post(post_id, reaction_type)
        status = f"[Thread-{thread_id}] [{fb.user_id}] {message}"
        return thread_id, success, status
    except Exception as e:
        return thread_id, False, f"[Thread-{thread_id}] Error: {str(e)}"

def banner():
    """Display banner"""
    print("""
╔═══════════════════════════════════════╗
║   FB Auto React Tool - Termux        ║
║   Multi-Account with Threading       ║
║   GraphQL API Support                ║
╚═══════════════════════════════════════╝
""")

def main():
    banner()
    
    # Input
    cookie_file = input("[?] Cookie file path (default: cookies.txt): ").strip() or 'cookies.txt'
    cookies = load_cookies(cookie_file)
    
    if not cookies:
        print("[!] No cookies loaded. Exiting...")
        return
    
    print(f"[+] Loaded {len(cookies)} cookie(s)")
    
    post_id = input("[?] Enter Post ID or Post URL: ").strip()
    
    # Extract post ID from URL if needed
    if 'facebook.com' in post_id:
        try:
            if '/posts/' in post_id:
                post_id = post_id.split('/posts/')[1].split('/')[0].split('?')[0]
            elif 'story_fbid=' in post_id:
                post_id = post_id.split('story_fbid=')[1].split('&')[0]
        except:
            print("[!] Could not extract post ID from URL")
            return
    
    print(f"[+] Target Post ID: {post_id}")
    
    # Reaction type selection
    print("\n[*] Reaction Types:")
    print("1. LIKE ❤️")
    print("2. LOVE 😍")
    print("3. CARE 🤗")
    print("4. HAHA 😂")
    print("5. WOW 😮")
    print("6. SAD 😢")
    print("7. ANGRY 😡")
    
    choice = input("\n[?] Select reaction (1-7, default: 1): ").strip() or '1'
    reactions = {
        '1': 'LIKE', '2': 'LOVE', '3': 'CARE', 
        '4': 'HAHA', '5': 'WOW', '6': 'SAD', '7': 'ANGRY'
    }
    reaction_type = reactions.get(choice, 'LIKE')
    
    max_threads = input("[?] Max threads (default: 5): ").strip() or '5'
    max_threads = int(max_threads)
    
    print(f"\n[+] Starting auto-react with {max_threads} threads...")
    print(f"[+] Reaction Type: {reaction_type}")
    print(f"[+] Target: {post_id}")
    print("-" * 50)
    
    # Threading execution
    success_count = 0
    failed_count = 0
    
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = {
            executor.submit(worker, cookie, post_id, reaction_type, i): i 
            for i, cookie in enumerate(cookies, 1)
        }
        
        for future in as_completed(futures):
            thread_id, success, status = future.result()
            print(status)
            
            if success:
                success_count += 1
            else:
                failed_count += 1
            
            time.sleep(0.5)  # Rate limiting
    
    print("-" * 50)
    print(f"\n[+] Completed!")
    print(f"[+] Success: {success_count}")
    print(f"[+] Failed: {failed_count}")
    print(f"[+] Total: {len(cookies)}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user")
    except Exception as e:
        print(f"[!] Error: {str(e)}")
