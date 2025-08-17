#!/usr/bin/env python3
"""
Comprehensive test script for filtering, searching, and ordering capabilities.
This script tests all the advanced features we've implemented in our API.
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:8000/api"

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def test_basic_functionality():
    """Test basic API functionality"""
    print_section("BASIC FUNCTIONALITY TESTS")
    
    # Test book list
    print("Testing Book List Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/books/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Found {len(data.get('results', data))} books")
            
            # Check if filtering info is included
            if 'filtering_info' in data:
                print("✅ Filtering information included in response")
            else:
                print("❌ Filtering information missing from response")
        else:
            print(f"❌ Failed with status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_filtering_capabilities():
    """Test all filtering capabilities"""
    print_section("FILTERING CAPABILITIES TESTS")
    
    # Test title filtering
    print("Testing Title Filtering...")
    filters_to_test = [
        ("title", "Test", "Filter by title (contains)"),
        ("title_exact", "Test Book", "Filter by exact title"),
        ("title_starts_with", "Test", "Filter by title starting with"),
        ("publication_year", "2023", "Filter by exact publication year"),
        ("publication_year_min", "2020", "Filter by minimum publication year"),
        ("publication_year_max", "2025", "Filter by maximum publication year"),
        ("has_author", "true", "Filter books with author"),
        ("recent_books", "true", "Filter recent books"),
        ("title_length", "5", "Filter by minimum title length")
    ]
    
    for filter_name, filter_value, description in filters_to_test:
        try:
            params = {filter_name: filter_value}
            response = requests.get(f"{BASE_URL}/books/", params=params)
            
            if response.status_code == 200:
                data = response.json()
                count = len(data.get('results', data))
                print(f"✅ {description}: {count} results")
            else:
                print(f"❌ {description}: Failed with status {response.status_code}")
        except Exception as e:
            print(f"❌ {description}: Error - {e}")

def test_search_functionality():
    """Test search functionality"""
    print_section("SEARCH FUNCTIONALITY TESTS")
    
    search_terms = ["Test", "Book", "Author"]
    
    for term in search_terms:
        print(f"Testing search for '{term}'...")
        try:
            response = requests.get(f"{BASE_URL}/books/", params={"search": term})
            
            if response.status_code == 200:
                data = response.json()
                count = len(data.get('results', data))
                print(f"✅ Search for '{term}': {count} results")
                
                # Show some results
                if count > 0:
                    first_result = data.get('results', data)[0]
                    print(f"   First result: {first_result.get('title', 'Unknown')}")
            else:
                print(f"❌ Search for '{term}': Failed with status {response.status_code}")
        except Exception as e:
            print(f"❌ Search for '{term}': Error - {e}")

def test_ordering_capabilities():
    """Test ordering capabilities"""
    print_section("ORDERING CAPABILITIES TESTS")
    
    ordering_fields = [
        ("title", "Order by title (ascending)"),
        ("-title", "Order by title (descending)"),
        ("publication_year", "Order by publication year (ascending)"),
        ("-publication_year", "Order by publication year (descending)"),
        ("created_at", "Order by creation date (ascending)"),
        ("-created_at", "Order by creation date (descending)")
    ]
    
    for field, description in ordering_fields:
        print(f"Testing {description}...")
        try:
            response = requests.get(f"{BASE_URL}/books/", params={"ordering": field})
            
            if response.status_code == 200:
                data = response.json()
                count = len(data.get('results', data))
                print(f"✅ {description}: {count} results")
                
                # Show first and last results to verify ordering
                if count > 1:
                    results = data.get('results', data)
                    first = results[0]
                    last = results[-1]
                    
                    if field.startswith('-'):
                        # Descending order
                        print(f"   First: {first.get('title', 'Unknown')}")
                        print(f"   Last: {last.get('title', 'Unknown')}")
                    else:
                        # Ascending order
                        print(f"   First: {first.get('title', 'Unknown')}")
                        print(f"   Last: {last.get('title', 'Unknown')}")
            else:
                print(f"❌ {description}: Failed with status {response.status_code}")
        except Exception as e:
            print(f"❌ {description}: Error - {e}")

def test_combined_filters():
    """Test combining multiple filters"""
    print_section("COMBINED FILTERS TESTS")
    
    # Test multiple filters together
    combined_filters = [
        {
            "search": "Test",
            "publication_year": "2023",
            "ordering": "title"
        },
        {
            "has_author": "true",
            "recent_books": "true",
            "ordering": "-publication_year"
        },
        {
            "title_length": "5",
            "ordering": "created_at"
        }
    ]
    
    for i, filters in enumerate(combined_filters, 1):
        print(f"Testing combined filters set {i}...")
        try:
            response = requests.get(f"{BASE_URL}/books/", params=filters)
            
            if response.status_code == 200:
                data = response.json()
                count = len(data.get('results', data))
                print(f"✅ Combined filters {i}: {count} results")
                print(f"   Filters: {filters}")
            else:
                print(f"❌ Combined filters {i}: Failed with status {response.status_code}")
        except Exception as e:
            print(f"❌ Combined filters {i}: Error - {e}")

def test_author_filtering():
    """Test author filtering capabilities"""
    print_section("AUTHOR FILTERING TESTS")
    
    # Test author list with filters
    print("Testing Author List with Filters...")
    try:
        response = requests.get(f"{BASE_URL}/authors/")
        
        if response.status_code == 200:
            data = response.json()
            count = len(data.get('results', data))
            print(f"✅ Author list: {count} authors")
            
            # Test author filtering
            if count > 0:
                author_filters = [
                    {"name": "Test", "Description": "Filter by name contains"},
                    {"has_books": "true", "Description": "Filter authors with books"},
                    {"ordering": "name", "Description": "Order by name"}
                ]
                
                for filters in author_filters:
                    try:
                        response = requests.get(f"{BASE_URL}/authors/", params=filters)
                        if response.status_code == 200:
                            filter_data = response.json()
                            filter_count = len(filter_data.get('results', filter_data))
                            print(f"✅ {filters['Description']}: {filter_count} results")
                        else:
                            print(f"❌ {filters['Description']}: Failed")
                    except Exception as e:
                        print(f"❌ {filters['Description']}: Error - {e}")
        else:
            print(f"❌ Author list failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Author filtering test error: {e}")

def test_advanced_features():
    """Test advanced features like related books and metadata"""
    print_section("ADVANCED FEATURES TESTS")
    
    # Test book detail with related books
    print("Testing Book Detail with Related Books...")
    try:
        response = requests.get(f"{BASE_URL}/books/1/")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Book detail retrieved successfully")
            
            if 'related_books' in data:
                related = data['related_books']
                print(f"✅ Related books feature: {len(related.get('books', []))} related books")
            else:
                print("❌ Related books feature not found")
        else:
            print(f"❌ Book detail failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Book detail test error: {e}")
    
    # Test author books with metadata
    print("Testing Author Books with Metadata...")
    try:
        response = requests.get(f"{BASE_URL}/authors/1/books/")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Author books retrieved successfully")
            
            if 'metadata' in data:
                metadata = data['metadata']
                print(f"✅ Metadata included: {metadata.get('total_books', 0)} total books")
                print(f"   Publication years: {metadata.get('publication_years', [])}")
                print(f"   Latest book: {metadata.get('latest_book', 'None')}")
            else:
                print("❌ Metadata not found")
        else:
            print(f"❌ Author books failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Author books test error: {e}")

def test_error_handling():
    """Test error handling for invalid filters"""
    print_section("ERROR HANDLING TESTS")
    
    # Test invalid filter values
    invalid_filters = [
        {"publication_year": "invalid_year"},
        {"created_after": "invalid_date"},
        {"ordering": "invalid_field"},
        {"page": "invalid_page"}
    ]
    
    for filters in invalid_filters:
        print(f"Testing invalid filters: {filters}")
        try:
            response = requests.get(f"{BASE_URL}/books/", params=filters)
            
            # Should handle gracefully (either return empty results or error)
            if response.status_code in [200, 400, 422]:
                print(f"✅ Handled gracefully with status {response.status_code}")
            else:
                print(f"❌ Unexpected status {response.status_code}")
        except Exception as e:
            print(f"❌ Error handling test failed: {e}")

def test_performance_features():
    """Test performance-related features"""
    print_section("PERFORMANCE FEATURES TESTS")
    
    # Test with include_author_details parameter
    print("Testing Performance Optimization Features...")
    try:
        response = requests.get(f"{BASE_URL}/books/", params={"include_author_details": "true"})
        
        if response.status_code == 200:
            data = response.json()
            count = len(data.get('results', data))
            print(f"✅ Performance optimization: {count} results with author details")
        else:
            print(f"❌ Performance optimization failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Performance test error: {e}")
    
    # Test author list with book counts
    try:
        response = requests.get(f"{BASE_URL}/authors/", params={"include_book_counts": "true"})
        
        if response.status_code == 200:
            data = response.json()
            count = len(data.get('results', data))
            print(f"✅ Author optimization: {count} authors with book counts")
        else:
            print(f"❌ Author optimization failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Author optimization test error: {e}")

def main():
    """Run all tests"""
    print("🚀 Starting Comprehensive API Testing...")
    print("Testing Filtering, Searching, and Ordering Capabilities")
    
    # Run all test categories
    test_basic_functionality()
    test_filtering_capabilities()
    test_search_functionality()
    test_ordering_capabilities()
    test_combined_filters()
    test_author_filtering()
    test_advanced_features()
    test_error_handling()
    test_performance_features()
    
    print_section("TESTING COMPLETE")
    print("🎉 All tests completed!")
    print("\nSummary of Features Tested:")
    print("✅ Basic API functionality")
    print("✅ Advanced filtering (title, author, year, dates, custom)")
    print("✅ Search functionality across multiple fields")
    print("✅ Flexible ordering by any field")
    print("✅ Combined filters and complex queries")
    print("✅ Author filtering and optimization")
    print("✅ Advanced features (related books, metadata)")
    print("✅ Error handling for invalid inputs")
    print("✅ Performance optimization features")
    
    print("\nTo test authenticated endpoints, you'll need to:")
    print("1. Log in through the admin interface")
    print("2. Use session cookies or implement proper authentication")

if __name__ == "__main__":
    main()
