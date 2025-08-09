#!/usr/bin/env python3
"""
Test script to verify streaming functionality works correctly.
"""

import sys
import os
import requests
import time

# Add the src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_streaming_api():
    """Test the streaming API endpoint."""
    url = "http://localhost:5000/api/chat"
    
    # Test data
    test_data = {
        "message": "What is the current market trend?",
        "stream": True
    }
    
    print("Testing streaming API...")
    print(f"URL: {url}")
    print(f"Data: {test_data}")
    print("-" * 50)
    
    try:
        response = requests.post(url, json=test_data, stream=True)
        
        if response.status_code == 200:
            print("✅ Streaming response received:")
            print("Assistant: ", end='', flush=True)
            
            for chunk in response.iter_content(chunk_size=1, decode_unicode=True):
                if chunk:
                    if chunk.startswith('data: '):
                        content = chunk[6:]  # Remove 'data: ' prefix
                        if content.strip():
                            print(content, end='', flush=True)
                            time.sleep(0.01)  # Small delay to simulate real streaming
            
            print("\n" + "=" * 50)
            print("✅ Streaming test completed successfully!")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to backend server.")
        print("Make sure the backend server is running on http://localhost:5000")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_non_streaming_api():
    """Test the non-streaming API endpoint."""
    url = "http://localhost:5000/api/chat"
    
    # Test data
    test_data = {
        "message": "What is AAPL stock price?",
        "stream": False
    }
    
    print("\nTesting non-streaming API...")
    print(f"URL: {url}")
    print(f"Data: {test_data}")
    print("-" * 50)
    
    try:
        response = requests.post(url, json=test_data)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Non-streaming response received:")
            print(f"Assistant: {data.get('response', 'No response')}")
            print(f"Timestamp: {data.get('timestamp', 'No timestamp')}")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to backend server.")
        print("Make sure the backend server is running on http://localhost:5000")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    print("🚀 Testing Stock Investment Assistant Streaming API")
    print("=" * 60)
    
    # Test both streaming and non-streaming
    test_streaming_api()
    test_non_streaming_api()
    
    print("\n🎉 All tests completed!")
