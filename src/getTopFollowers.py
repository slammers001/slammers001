#!/usr/bin/env python3
"""
Script to get and display top followers using GitHub GraphQL API
Updates the README.md with follower information
"""

import os
import sys
import requests
import json

def get_followers(username, token):
    """Get followers from GitHub GraphQL API sorted by most recent first"""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # GraphQL query to get followers with their creation dates
    query = """
    query($username: String!, $first: Int!) {
      user(login: $username) {
        followers(first: $first) {
          nodes {
            login
            avatarUrl
            url
            htmlUrl: url
            createdAt
          }
        }
      }
    }
    """
    
    variables = {
        'username': username,
        'first': 10  # Get top 10 followers
    }
    
    response = requests.post(
        'https://api.github.com/graphql',
        headers=headers,
        json={'query': query, 'variables': variables}
    )
    
    if response.status_code != 200:
        print(f"Error fetching followers: {response.status_code}")
        print(f"Response: {response.text}")
        return []
    
    data = response.json()
    
    if 'errors' in data:
        print(f"GraphQL errors: {data['errors']}")
        return []
    
    followers = data.get('data', {}).get('user', {}).get('followers', {}).get('nodes', [])
    
    # Sort by createdAt in descending order (most recent first)
    followers.sort(key=lambda x: x.get('createdAt', ''), reverse=True)
    
    # Convert GraphQL response to match expected format
    formatted_followers = []
    for follower in followers:
        formatted_followers.append({
            'login': follower['login'],
            'avatar_url': follower['avatarUrl'],
            'html_url': follower['htmlUrl']
        })
    
    return formatted_followers

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
