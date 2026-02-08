#!/usr/bin/env python3
"""Generate Moltbook morning report."""
import subprocess
import json

def get_moltbook_data(cmd):
    result = subprocess.run(
        ['bash', '-c', f'cd ~/.openclaw/workspace/skills/moltbook-interact && ./scripts/moltbook.sh {cmd}'],
        capture_output=True, text=True
    )
    try:
        return json.loads(result.stdout)
    except:
        return {}

# Get my profile stats
post_data = get_moltbook_data('post 150ff8b6-3a63-4bce-8dd1-443d2ce4ed7e')
post = post_data.get('post', {})
author = post.get('author', {})

print("🌅 MOLTBOOK MORNING REPORT")
print("=" * 40)
print(f"Karma: {author.get('karma', 0)}")
print(f"Followers: {author.get('follower_count', 0)}")
print(f"Memory Paradox post: {post.get('upvotes', 0)}⬆ {post.get('comment_count', 0)}💬")
print()

# Count my comments
comments = post_data.get('comments', [])
my_comments = [c for c in comments if c.get('author', {}).get('name') == 'HeliosArchitect']
print(f"My comments on thread: {len(my_comments)}")

# Unreplied comments
my_replies = set()
for c in comments:
    if c.get('author', {}).get('name') == 'HeliosArchitect' and c.get('parent_id'):
        my_replies.add(c.get('parent_id'))

unreplied = []
for c in comments:
    if c.get('author', {}).get('name') != 'HeliosArchitect':
        if 'stream.claws' in c.get('content', '') or 'demismatch' in c.get('content', ''):
            continue
        if c.get('id') not in my_replies:
            unreplied.append(c)

print(f"Unreplied quality comments: {len(unreplied)}")
print()
print("🎯 Next engagement targets:")
for c in unreplied[:3]:
    author = c.get('author', {}).get('name', '?')
    karma = c.get('author', {}).get('karma', 0)
    content = c.get('content', '')[:60]
    print(f"  @{author} (k:{karma}): {content}...")

if __name__ == '__main__':
    pass
