#!/usr/bin/env python3
"""
Script to get and display top followers using GitHub API
Updates the README.md with follower information
"""

import os
import sys
import requests
import json

def get_followers(username, token):
    """Get followers from GitHub API"""
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    followers = []
    page = 1
    per_page = 10  # Get top 10 followers
    
    while len(followers) < per_page:
        url = f'https://api.github.com/users/{username}/followers?page={page}&per_page={per_page}'
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"Error fetching followers: {response.status_code}")
            return []
        
        page_followers = response.json()
        if not page_followers:
            break
            
        followers.extend(page_followers)
        page += 1
    
    return followers[:per_page]

def format_followers_html(followers):
    """Format followers as HTML table"""
    if not followers:
        return "<p>No followers data available</p>"
    
    html = '<table>\n'
    
    # Process followers in rows of 7
    for i in range(0, len(followers), 7):
        html += '  <tr>\n'
        row_followers = followers[i:i+7]
        
        for follower in row_followers:
            username = follower['login']
            avatar_url = follower['avatar_url']
            profile_url = follower['html_url']
            
            html += '    <td align="center">\n'
            html += f'      <a href="{profile_url}">\n'
            html += f'        <img src="{avatar_url}" width="100px;" alt="{username}"/>\n'
            html += f'      </a>\n'
            html += f'      <br />\n'
            html += f'      <a href="{profile_url}">{username}</a>\n'
            html += '    </td>\n'
        
        html += '  </tr>\n'
    
    html += '</table>'
    return html

def main():
    """Main function to get top followers"""
    if len(sys.argv) < 3:
        print("Usage: python getTopFollowers.py <username> <token> [readme_file]")
        sys.exit(1)
    
    username = sys.argv[1]
    token = sys.argv[2]
    readme_file = sys.argv[3] if len(sys.argv) > 3 else "README.md"
    
    # Get followers
    followers = get_followers(username, token)
    
    # Format as HTML
    followers_html = format_followers_html(followers)
    
    # Create the section content
    followers_section = f"""
<!--START_SECTION:top-followers-->
{followers_html}
<!--END_SECTION:top-followers-->
"""
    
    # Update README.md
    readme_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), readme_file)
    
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace the followers section
        import re
        pattern = r'<!--START_SECTION:top-followers-->.*?<!--END_SECTION:top-followers-->'
        content = re.sub(pattern, followers_section.strip(), content, flags=re.DOTALL)
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Updated {readme_file} with {len(followers)} followers")
    else:
        print(f"{readme_file} not found")

if __name__ == "__main__":
    main()
