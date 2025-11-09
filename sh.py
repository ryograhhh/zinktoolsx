import requests
import json
import sys
from typing import Dict, Any

def test_endpoint(base_url: str, path: str) -> Dict[str, Any]:
    """Test a single API endpoint and return results"""
    url = f"{base_url}{path}"
    
    print(f"\n{'='*60}")
    print(f"Testing: {url}")
    print(f"{'='*60}")
    
    try:
        response = requests.get(url, timeout=10)
        
        result = {
            'url': url,
            'status_code': response.status_code,
            'status_text': response.reason,
            'success': response.ok,
            'headers': dict(response.headers)
        }
        
        # Try to parse as JSON
        content_type = response.headers.get('Content-Type', '')
        
        if 'application/json' in content_type:
            try:
                result['data'] = response.json()
                result['type'] = 'json'
            except:
                result['data'] = response.text[:500]
                result['type'] = 'text'
        else:
            result['data'] = response.text[:500]
            result['type'] = 'text'
        
        # Print results
        print(f"✓ Status: {result['status_code']} {result['status_text']}")
        print(f"✓ Content-Type: {content_type}")
        
        if result['type'] == 'json':
            print(f"\n📦 JSON Response:")
            print(json.dumps(result['data'], indent=2, ensure_ascii=False))
        else:
            print(f"\n📄 Text Response (first 500 chars):")
            print(result['data'])
        
        return result
        
    except requests.exceptions.Timeout:
        print(f"✗ Timeout - Server took too long to respond")
        return {'url': url, 'error': 'Timeout', 'success': False}
        
    except requests.exceptions.ConnectionError as e:
        print(f"✗ Connection Error: {str(e)[:200]}")
        return {'url': url, 'error': f'Connection Error: {str(e)}', 'success': False}
        
    except Exception as e:
        print(f"✗ Error: {str(e)[:200]}")
        return {'url': url, 'error': str(e), 'success': False}

def main():
    """Main function to test API endpoints"""
    
    base_url = "https://pyprivate.pshteam.dev"
    
    print("=" * 60)
    print("🔍 API ENDPOINT TESTER")
    print("=" * 60)
    print(f"Base URL: {base_url}")
    print(f"Testing common API paths...\n")
    
    # Common API paths to test
    paths = [
        '/',
        '/api',
        '/api/v1',
        '/v1',
        '/docs',
        '/swagger',
        '/openapi.json',
        '/health',
        '/status',
        '/packages',
        '/simple',
        '/pypi',
        '/simple/',
        '/packages/',
    ]
    
    successful_endpoints = []
    
    for path in paths:
        result = test_endpoint(base_url, path)
        if result.get('success'):
            successful_endpoints.append(path)
        print()  # Empty line between tests
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"Total endpoints tested: {len(paths)}")
    print(f"Successful responses: {len(successful_endpoints)}")
    
    if successful_endpoints:
        print("\n✓ Working endpoints:")
        for endpoint in successful_endpoints:
            print(f"  - {base_url}{endpoint}")
    else:
        print("\n✗ No working endpoints found")
        print("\nPossible reasons:")
        print("  1. The API requires authentication (API key, token)")
        print("  2. The API is down or not accessible")
        print("  3. CORS restrictions prevent access")
        print("  4. Different endpoint structure is used")
    
    # Option to test custom path
    print("\n" + "=" * 60)
    try:
        custom = input("\nEnter custom path to test (or press Enter to exit): ").strip()
        if custom:
            if not custom.startswith('/'):
                custom = '/' + custom
            test_endpoint(base_url, custom)
    except (KeyboardInterrupt, EOFError):
        print("\n\nExiting...")
    
    print("\n✅ Done!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)
