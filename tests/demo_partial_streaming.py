"""
Demo script to show partial summary streaming in action
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.streaming_json_parser import StreamingJSONParser


def demo_partial_streaming():
    """Demonstrate partial summary streaming"""
    response = '''{
        "summary": "The top 5 best-selling products by quantity sold are Kingston Fury Beast 16GB DDR4 (85 units), Corsair Vengeance LPX 32GB (72 units), Intel Core i5-13600K (68 units), NVIDIA GeForce RTX 4070 (45 units), and AMD Ryzen 7 7800X3D (42 units), generating a combined revenue of $45,230.",
        "components": [
            {
                "type": "metric",
                "config": {
                    "label": "Total Revenue",
                    "value": "$45,230"
                }
            }
        ]
    }'''
    
    parser = StreamingJSONParser()
    
    print("=" * 80)
    print("PARTIAL SUMMARY STREAMING DEMO")
    print("=" * 80)
    print("\nWatch as the summary streams in real-time!\n")
    print("-" * 80)
    
    last_partial = ""
    summary_complete = False
    
    for i, char in enumerate(response):
        results = parser.feed(char)
        
        for result in results:
            if result["type"] == "summary_partial":
                # Show progressive update
                partial_text = result["content"]
                if partial_text != last_partial:
                    # Clear previous line and show new partial text
                    print(f"\r💡 {partial_text}▌", end="", flush=True)
                    last_partial = partial_text
                    time.sleep(0.05)  # Simulate streaming delay
                
            elif result["type"] == "summary":
                # Show complete summary
                print(f"\r💡 {result['content']}")
                print("\n" + "=" * 80)
                print("✅ SUMMARY COMPLETE!")
                print("=" * 80)
                summary_complete = True
                break
        
        if summary_complete:
            break
        
        # Simulate network delay
        if i % 5 == 0:
            time.sleep(0.02)
    
    print("\n✨ Demo complete! This is how users will see the summary appear in real-time.\n")


if __name__ == "__main__":
    demo_partial_streaming()
