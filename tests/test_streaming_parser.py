"""
Test script for StreamingJSONParser

Run this to verify the parser works correctly before testing with real API.
"""

import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.streaming_json_parser import StreamingJSONParser


def simulate_gpt_stream():
    """Simulate character-by-character GPT streaming"""
    response = '''{
        "summary": "The top 5 products are X, Y, Z, A, and B with total sales of $10,000.",
        "components": [
            {
                "type": "metric",
                "config": {
                    "label": "Total Revenue",
                    "value": "$10,000"
                }
            },
            {
                "type": "bar_chart",
                "config": {
                    "title": "Top Products",
                    "data": [
                        {"product": "Product X", "sales": 100},
                        {"product": "Product Y", "sales": 90}
                    ],
                    "x": "product",
                    "y": "sales"
                }
            }
        ]
    }'''
    
    parser = StreamingJSONParser()
    
    print("=" * 80)
    print("STREAMING JSON PARSER TEST")
    print("=" * 80)
    print("\nStarting stream simulation...\n")
    
    for i, char in enumerate(response):
        results = parser.feed(char)
        
        for result in results:
            if result["type"] == "summary":
                print(f"\n{'='*60}")
                print("✅ SUMMARY COMPLETE")
                print(f"{'='*60}")
                print(f"Content: {result['content']}")
                print(f"{'='*60}\n")
                
            elif result["type"] == "component":
                print(f"\n{'='*60}")
                print(f"✅ COMPONENT {result['index']} COMPLETE")
                print(f"{'='*60}")
                print(f"Type: {result['data']['type']}")
                print(f"Config keys: {list(result['data']['config'].keys())}")
                print(f"{'='*60}\n")
                
            elif result["type"] == "error":
                print(f"\n{'='*60}")
                print("❌ ERROR")
                print(f"{'='*60}")
                print(f"Message: {result['message']}")
                print(f"Recoverable: {result.get('recoverable', False)}")
                print(f"{'='*60}\n")
        
        # Simulate network delay (every 10 characters)
        if i % 10 == 0:
            time.sleep(0.01)
    
    print(f"\n{'='*80}")
    print("FINAL STATISTICS")
    print(f"{'='*80}")
    print(f"Summary extracted: {parser.summary_extracted}")
    print(f"Components yielded: {parser.components_yielded}")
    print(f"Parsing complete: {parser.is_complete()}")
    print(f"Total characters processed: {parser.position}")
    print(f"Error count: {parser.error_count}")
    print(f"{'='*80}\n")
    
    return parser.error_count == 0 and parser.is_complete()


def test_escaped_quotes():
    """Test handling of escaped quotes"""
    parser = StreamingJSONParser()
    json_str = '{"summary": "The \\"best\\" product", "components": []}'
    
    print("=" * 80)
    print("TEST: Escaped Quotes")
    print("=" * 80)
    print(f"Input: {json_str}\n")
    
    results = []
    for char in json_str:
        results.extend(parser.feed(char))
    
    summary = next((r for r in results if r["type"] == "summary"), None)
    
    if summary and 'best' in summary["content"]:
        print("✅ PASS: Escaped quotes handled correctly")
        print(f"Summary: {summary['content']}\n")
        return True
    else:
        print("❌ FAIL: Escaped quotes not handled correctly\n")
        return False


def test_nested_objects():
    """Test handling of deeply nested objects"""
    parser = StreamingJSONParser()
    json_str = '''{
        "summary": "Test",
        "components": [{
            "type": "chart",
            "config": {
                "data": {
                    "nested": {
                        "deep": true
                    }
                }
            }
        }]
    }'''
    
    print("=" * 80)
    print("TEST: Nested Objects")
    print("=" * 80)
    
    results = []
    for char in json_str:
        results.extend(parser.feed(char))
    
    components = [r for r in results if r["type"] == "component"]
    
    if len(components) == 1:
        print("✅ PASS: Nested objects handled correctly")
        print(f"Component extracted: {components[0]['data']['type']}\n")
        return True
    else:
        print("❌ FAIL: Nested objects not handled correctly\n")
        return False


def test_partial_stream():
    """Test recovery from incomplete stream"""
    parser = StreamingJSONParser()
    json_str = '{"summary": "Test", "components": [{"type": "metric", "conf'
    
    print("=" * 80)
    print("TEST: Partial Stream Recovery")
    print("=" * 80)
    print(f"Input (incomplete): {json_str}\n")
    
    results = []
    for char in json_str:
        results.extend(parser.feed(char))
    
    partial = parser.get_partial_result()
    
    if partial["summary_extracted"] and partial["components_count"] == 0:
        print("✅ PASS: Partial stream handled correctly")
        print(f"Summary extracted: {partial['summary_extracted']}")
        print(f"Components count: {partial['components_count']}\n")
        return True
    else:
        print("❌ FAIL: Partial stream not handled correctly\n")
        return False


if __name__ == "__main__":
    print("\n" + "🧪 " * 40 + "\n")
    print("STREAMING JSON PARSER - COMPREHENSIVE TEST SUITE")
    print("\n" + "🧪 " * 40 + "\n")
    
    tests = [
        ("Main Streaming Test", simulate_gpt_stream),
        ("Escaped Quotes Test", test_escaped_quotes),
        ("Nested Objects Test", test_nested_objects),
        ("Partial Stream Test", test_partial_stream)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} EXCEPTION: {str(e)}\n")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print("=" * 80)
    print(f"TOTAL: {passed}/{total} tests passed")
    print("=" * 80 + "\n")
    
    sys.exit(0 if passed == total else 1)
