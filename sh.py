#!/usr/bin/env python3
"""
Advanced API Endpoint Tester with aiohttp
Compatible with Termux

Install requirements:
    pkg install python
    pip install aiohttp
"""

import aiohttp
import asyncio
import json
import sys
from typing import Dict, Any, List
from datetime import datetime

class APITester:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.results = []
        
    async def test_endpoint(self, session: aiohttp.ClientSession, path: str, method: str = 'GET') -> Dict[str, Any]:
        """Test a single API endpoint"""
        url = f"{self.base_url}{path}"
        
        try:
            async with session.request(method, url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                content_type = response.headers.get('Content-Type', '')
                
                # Try to get response body
                try:
                    if 'application/json' in content_type:
                        data = await response.json()
                        data_type = 'json'
                    else:
                        text = await response.text()
                        data = text[:1000]  # First 1000 chars
                        data_type = 'text'
                except:
                    data = None
                    data_type = 'error'
                
                result = {
                    'method': method,
                    'path': path,
                    'url': url,
                    'status': response.status,
                    'status_text': response.reason,
                    'success': response.ok,
                    'content_type': content_type,
                    'headers': dict(response.headers),
                    'data_type': data_type,
                    'data': data,
                    'timestamp': datetime.now().isoformat()
                }
                
                return result
                
        except asyncio.TimeoutError:
            return {
                'method': method,
                'path': path,
                'url': url,
                'status': 0,
                'success': False,
                'error': 'Timeout',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'method': method,
                'path': path,
                'url': url,
                'status': 0,
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def test_all_endpoints(self, paths: List[str]):
        """Test all endpoints concurrently"""
        async with aiohttp.ClientSession() as session:
            tasks = [self.test_endpoint(session, path) for path in paths]
            self.results = await asyncio.gather(*tasks)
        return self.results
    
    async def custom_request(self, path: str, method: str = 'GET', headers: Dict = None, data: Any = None):
        """Make a custom request to the API"""
        url = f"{self.base_url}{path}"
        
        async with aiohttp.ClientSession() as session:
            try:
                kwargs = {'timeout': aiohttp.ClientTimeout(total=10)}
                if headers:
                    kwargs['headers'] = headers
                if data:
                    if isinstance(data, dict):
                        kwargs['json'] = data
                    else:
                        kwargs['data'] = data
                
                async with session.request(method, url, **kwargs) as response:
                    content_type = response.headers.get('Content-Type', '')
                    
                    if 'application/json' in content_type:
                        response_data = await response.json()
                    else:
                        response_data = await response.text()
                    
                    return {
                        'url': url,
                        'method': method,
                        'status': response.status,
                        'headers': dict(response.headers),
                        'data': response_data
                    }
            except Exception as e:
                return {'error': str(e), 'url': url}
    
    def print_result(self, result: Dict[str, Any]):
        """Pretty print a single result"""
        print(f"\n{'='*70}")
        print(f"🔗 {result['method']} {result['url']}")
        print(f"{'='*70}")
        
        if result.get('error'):
            print(f"❌ Error: {result['error']}")
        else:
            status_symbol = "✅" if result['success'] else "❌"
            print(f"{status_symbol} Status: {result['status']} {result.get('status_text', '')}")
            print(f"📦 Content-Type: {result.get('content_type', 'N/A')}")
            
            if result.get('data_type') == 'json' and result.get('data'):
                print(f"\n📄 JSON Response:")
                print(json.dumps(result['data'], indent=2, ensure_ascii=False))
            elif result.get('data_type') == 'text' and result.get('data'):
                print(f"\n📝 Text Response (first 1000 chars):")
                print(result['data'])
    
    def print_summary(self):
        """Print summary of all tests"""
        print(f"\n{'='*70}")
        print("📊 SUMMARY")
        print(f"{'='*70}")
        
        total = len(self.results)
        successful = sum(1 for r in self.results if r.get('success'))
        
        print(f"Total endpoints tested: {total}")
        print(f"Successful (2xx): {successful}")
        print(f"Failed: {total - successful}")
        
        # Group by status code
        status_codes = {}
        for r in self.results:
            status = r.get('status', 0)
            status_codes[status] = status_codes.get(status, 0) + 1
        
        print(f"\n📈 Status Code Distribution:")
        for status, count in sorted(status_codes.items()):
            print(f"  {status}: {count}")
        
        # Show successful endpoints
        successful_endpoints = [r for r in self.results if r.get('success')]
        if successful_endpoints:
            print(f"\n✅ Working Endpoints ({len(successful_endpoints)}):")
            for r in successful_endpoints:
                print(f"  [{r['status']}] {r['method']} {r['path']}")
    
    def save_results(self, filename: str = 'api_test_results.json'):
        """Save results to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Results saved to: {filename}")

async def main():
    """Main function"""
    print("="*70)
    print("🚀 ADVANCED API ENDPOINT TESTER (aiohttp)")
    print("="*70)
    
    base_url = "https://pyprivate.pshteam.dev"
    print(f"Base URL: {base_url}\n")
    
    # Extensive list of common API paths
    paths = [
        # Root and common paths
        '/',
        '/api',
        '/api/v1',
        '/api/v2',
        '/v1',
        '/v2',
        
        # Documentation
        '/docs',
        '/documentation',
        '/swagger',
        '/swagger.json',
        '/openapi.json',
        '/redoc',
        '/api-docs',
        
        # Health and status
        '/health',
        '/healthz',
        '/status',
        '/ping',
        '/alive',
        '/ready',
        
        # PyPI related (since it's pyprivate)
        '/simple',
        '/simple/',
        '/packages',
        '/packages/',
        '/pypi',
        '/pypi/',
        '/package',
        '/package/',
        
        # Authentication
        '/auth',
        '/login',
        '/token',
        '/api/token',
        
        # User/Admin
        '/user',
        '/users',
        '/admin',
        '/api/users',
        
        # Info/Meta
        '/info',
        '/meta',
        '/version',
        '/api/info',
        
        # Search
        '/search',
        '/api/search',
        
        # Upload
        '/upload',
        '/api/upload',
        
        # Common endpoints
        '/index',
        '/home',
        '/stats',
        '/metrics',
    ]
    
    tester = APITester(base_url)
    
    print(f"Testing {len(paths)} endpoints concurrently...\n")
    print("⏳ Please wait...\n")
    
    # Test all endpoints
    await tester.test_all_endpoints(paths)
    
    # Print results
    for result in tester.results:
        tester.print_result(result)
    
    # Print summary
    tester.print_summary()
    
    # Save results
    tester.save_results()
    
    # Interactive mode
    print(f"\n{'='*70}")
    print("🔧 CUSTOM REQUEST MODE")
    print(f"{'='*70}")
    print("You can now make custom requests to the API")
    print("Commands:")
    print("  - Enter path (e.g., /api/v1/packages)")
    print("  - 'quit' or 'exit' to exit")
    print("  - 'list' to see successful endpoints")
    print()
    
    while True:
        try:
            user_input = input("Enter path or command: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            elif user_input.lower() == 'list':
                successful = [r for r in tester.results if r.get('success')]
                if successful:
                    print("\n✅ Successful endpoints:")
                    for r in successful:
                        print(f"  [{r['status']}] {r['path']}")
                else:
                    print("\n❌ No successful endpoints found")
                print()
                continue
            elif not user_input:
                continue
            
            # Ensure path starts with /
            if not user_input.startswith('/'):
                user_input = '/' + user_input
            
            # Ask for method
            method = input("HTTP Method (GET/POST/PUT/DELETE) [GET]: ").strip().upper() or 'GET'
            
            # Ask for headers
            print("Headers (JSON format, or press Enter to skip):")
            headers_input = input().strip()
            headers = None
            if headers_input:
                try:
                    headers = json.loads(headers_input)
                except:
                    print("⚠️  Invalid JSON, using no headers")
            
            # Ask for data
            data = None
            if method in ['POST', 'PUT', 'PATCH']:
                print("Request body (JSON format, or press Enter to skip):")
                data_input = input().strip()
                if data_input:
                    try:
                        data = json.loads(data_input)
                    except:
                        print("⚠️  Invalid JSON, sending as text")
                        data = data_input
            
            print("\n⏳ Sending request...")
            result = await tester.custom_request(user_input, method, headers, data)
            
            print(f"\n{'='*70}")
            print(f"📬 Response from {method} {user_input}")
            print(f"{'='*70}")
            if result.get('error'):
                print(f"❌ Error: {result['error']}")
            else:
                print(f"✅ Status: {result['status']}")
                print(f"\n📄 Response:")
                if isinstance(result['data'], dict) or isinstance(result['data'], list):
                    print(json.dumps(result['data'], indent=2, ensure_ascii=False))
                else:
                    print(result['data'])
            print()
            
        except (KeyboardInterrupt, EOFError):
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"❌ Error: {e}\n")
    
    print("\n✅ Done!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)
