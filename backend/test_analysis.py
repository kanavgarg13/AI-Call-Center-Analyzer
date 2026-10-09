
from analysis import analyze_transcript

sample_transcript = """
Agent: Hello, how can I help you?
Customer: My internet has not been working since yesterday.
Agent: I am sorry for the inconvenience. I will check your connection.
Customer: I have already restarted the router twice.
Agent: I can see an outage in your area. Our technical team is working on it.
Customer: Okay, but I need the internet for work.
"""

result = analyze_transcript(sample_transcript)

print("\nCall Analysis:")
for key, value in result.items():
    print(f"{key}: {value}")
