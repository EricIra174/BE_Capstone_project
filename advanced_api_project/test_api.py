#!/usr/bin/env python3
"""
Simple test script to verify the API functionality.
This script tests the basic CRUD operations and demonstrates
how the generic views work.
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def test_list_books():
    """Test the book list endpoint"""
    print("Testing Book List Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/books/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Found {len(data.get('results', data))} books")
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_book_detail():
    """Test the book detail endpoint"""
    print("\nTesting Book Detail Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/books/1/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Retrieved book: {data.get('title', 'Unknown')}")
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_create_book_unauthorized():
    """Test that creating a book without authentication fails"""
    print("\nTesting Book Creation (Unauthorized)...")
    try:
        book_data = {
            "title": "Unauthorized Book",
            "publication_year": 2024,
            "author": 1
        }
        response = requests.post(
            f"{BASE_URL}/books/create/",
            json=book_data,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 401:
            print("✅ Success! Authentication required as expected")
            print(f"Response: {response.text}")
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_author_list():
    """Test the author list endpoint"""
    print("\nTesting Author List Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/authors/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Found {len(data.get('results', data))} authors")
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_author_books():
    """Test the author books endpoint"""
    print("\nTesting Author Books Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/authors/1/books/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Retrieved books for author")
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_search_functionality():
    """Test the search functionality"""
    print("\nTesting Search Functionality...")
    try:
        response = requests.get(f"{BASE_URL}/books/?search=Test")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Search completed")
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_filtering():
    """Test the filtering functionality"""
    print("\nTesting Filtering Functionality...")
    try:
        response = requests.get(f"{BASE_URL}/books/?publication_year=2023")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Filtering completed")
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Run all tests"""
    print("🚀 Starting API Tests...")
    print("=" * 50)
    
    # Test basic functionality
    test_list_books()
    test_book_detail()
    test_author_list()
    test_author_books()
    
    # Test search and filtering
    test_search_functionality()
    test_filtering()
    
    # Test permissions
    test_create_book_unauthorized()
    
    print("\n" + "=" * 50)
    print("🎉 API Testing Complete!")
    print("\nNote: Some endpoints require authentication.")
    print("To test authenticated endpoints, you'll need to:")
    print("1. Log in through the admin interface")
    print("2. Use session cookies or implement proper authentication")

if __name__ == "__main__":
    main()
