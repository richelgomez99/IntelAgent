"""
Cloud Function: GitHub Activity
Monitors GitHub organization activity
Ported from AWS IntelAgent github_activity Lambda
"""
from google.cloud import firestore
import requests
from datetime import datetime, timedelta
import logging
import os
import json
from typing import Dict, List, Any, Optional

db = firestore.Client()

# GitHub API token (set as environment variable)
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

# Known company to GitHub org mappings
COMPANY_ORG_MAPPINGS = {
    "anthropic": "anthropics",
    "openai": "openai",
    "google": "google",
    "deepmind": "google-deepmind",
    "google deepmind": "google-deepmind",
    "databricks": "databricks",
    "cohere": "cohere-ai",
    "hugging face": "huggingface",
    "huggingface": "huggingface",
    "meta": "meta-llama",
    "stability": "Stability-AI",
    "stability ai": "Stability-AI",
    "microsoft": "microsoft",
    "amazon": "amzn"
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def resolve_github_org(company_name: str, token: Optional[str]) -> Optional[str]:
    """
    Intelligently resolve company name to GitHub organization
    Ported from AWS Lambda
    
    Args:
        company_name: Company name from query
        token: GitHub token (optional)
        
    Returns:
        Resolved GitHub organization name or None
    """
    # Normalize company name
    normalized = company_name.lower().strip()
    
    # Check exact mapping
    if normalized in COMPANY_ORG_MAPPINGS:
        return COMPANY_ORG_MAPPINGS[normalized]
    
    # Try variations
    variations = [
        company_name,  # Original
        company_name.lower(),  # Lowercase
        company_name.lower() + 's',  # Add 's'
        company_name.lower().rstrip('s'),  # Remove 's'
        company_name.lower().replace(' ', '-'),  # Replace spaces with hyphens
        company_name.lower().replace(' ', ''),  # Remove spaces
    ]
    
    headers = {
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
        'User-Agent': 'GCP-CompetitiveIntel-Agent/1.0'
    }
    
    if token:
        headers['Authorization'] = f'token {token}'
    
    # Try each variation
    for variant in variations:
        try:
            url = f"https://api.github.com/orgs/{variant}"
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                return variant
        except:
            continue
    
    return None


def list_organization_repos(organization: str, token: Optional[str]) -> List[Dict[str, Any]]:
    """
    List all repositories for an organization (with pagination)
    Ported from AWS Lambda
    
    Args:
        organization: GitHub organization name
        token: GitHub API token (optional)
        
    Returns:
        List of repository dictionaries
    """
    headers = {
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
        'User-Agent': 'GCP-CompetitiveIntel-Agent/1.0'
    }
    
    if token:
        headers['Authorization'] = f'token {token}'
    
    repos = []
    page = 1
    max_pages = 3  # Limit to 300 repos to avoid timeouts
    
    while page <= max_pages:
        url = f"https://api.github.com/orgs/{organization}/repos"
        params = {
            'per_page': 100,
            'sort': 'updated',
            'direction': 'desc',
            'page': page
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=20)
            
            if response.status_code != 200:
                break
            
            data = response.json()
            
            if not data:
                break
        except Exception as e:
            logger.error(f"Error fetching repos for {organization}: {e}")
            break
        
        for repo in data:
            # Fetch README for high-value repos (stars > 100) to conserve API calls
            readme_content = ''
            if repo.get('stargazers_count', 0) > 100:
                try:
                    readme_url = f"https://api.github.com/repos/{repo.get('full_name')}/readme"
                    readme_response = requests.get(readme_url, headers=headers, timeout=5)
                    if readme_response.status_code == 200:
                        readme_data = readme_response.json()
                        # README content is base64 encoded
                        import base64
                        readme_content = base64.b64decode(readme_data.get('content', '')).decode('utf-8')[:3000]  # First 3000 chars
                except Exception as e:
                    logger.debug(f"Could not fetch README for {repo.get('name')}: {e}")
            
            repos.append({
                'name': repo.get('name', 'Unknown'),
                'full_name': repo.get('full_name', ''),
                'description': (repo.get('description') or '')[:500],  # Longer description
                'readme': readme_content,  # README content for strategic repos
                'stars': repo.get('stargazers_count', 0),
                'forks': repo.get('forks_count', 0),
                'watchers': repo.get('watchers_count', 0),
                'language': repo.get('language') or 'Unknown',
                'topics': repo.get('topics', []),  # GitHub topics/tags
                'created_at': repo.get('created_at', ''),
                'updated_at': repo.get('updated_at', ''),
                'url': repo.get('html_url', '')
            })
        
        page += 1
    
    return repos


def github_activity(request):
    """
    Cloud Function entry point
    HTTP-triggered function for GitHub activity monitoring
    
    Args:
        request: Flask request object
        
    Returns:
        JSON response with GitHub data
    """
    # Set CORS headers for the preflight request
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
        }
        return ('', 204, headers)

    # Set CORS headers for the main request
    headers = {
        'Access-Control-Allow-Origin': '*'
    }
    
    # Parse request
    request_json = request.get_json(silent=True)
    company = request_json.get("company", "Anthropic") if request_json else "Anthropic"
    
    try:
        logger.info(f"Fetching GitHub data for: {company}")
        
        # Resolve company name to GitHub org
        organization = resolve_github_org(company, GITHUB_TOKEN)
        
        if not organization:
            logger.warning(f"Could not resolve GitHub org for {company}")
            return (json.dumps({
                'success': False,
                'company': company,
                'message': f'Could not find GitHub organization for "{company}"',
                'total_repos': 0,
                'total_stars': 0
            }), 200, headers)
        
        # Fetch repos
        repos = list_organization_repos(organization, GITHUB_TOKEN)
        
        # Handle None or empty list
        if repos is None or not repos:
            return (json.dumps({
                'success': True,
                'company': company,
                'organization': organization if organization else 'Unknown',
                'total_repos': 0,
                'total_stars': 0,
                'message': f'No repositories found for {company}'
            }), 200, headers)
        
        # Filter recently active repos (updated in last 30 days)
        cutoff = datetime.utcnow() - timedelta(days=30)
        recently_active = []
        
        for repo in repos:
            updated = repo.get('updated_at', '')
            if updated:
                try:
                    update_date = datetime.fromisoformat(updated.replace('Z', '+00:00'))
                    if update_date.replace(tzinfo=None) > cutoff:
                        recently_active.append({
                            'name': repo.get('name', 'Unknown'),
                            'stars': repo.get('stars', 0),
                            'updated': updated.split('T')[0] if 'T' in updated else updated[:10]
                        })
                except Exception as e:
                    logger.warning(f"Error parsing repo date: {e}")
                    pass
        
        # Sort by stars (most popular first) - use .get() for safety
        repos.sort(key=lambda x: x.get('stars', 0), reverse=True)
        recently_active.sort(key=lambda x: x.get('updated', ''), reverse=True)
        
        # Calculate totals
        total_stars = sum(r.get('stars', 0) for r in repos)
        total_forks = sum(r.get('forks', 0) for r in repos)
        
        # Build summary
        recent_summary = ', '.join([f"{r.get('name', 'Unknown')} ({r.get('stars', 0)}★)" for r in recently_active[:3]]) if recently_active else 'None'
        
        # Store in Firestore
        for repo in repos[:50]:  # Store top 50 repos
            try:
                doc_id = f"{company}_{repo.get('name', 'unknown')}"
                repo['company'] = company
                repo['scraped_at'] = datetime.utcnow().isoformat()
                db.collection("github").document(doc_id).set(repo)
            except Exception as e:
                logger.warning(f"Error storing repo in Firestore: {e}")
        
        result = {
            'success': True,
            'company': company,
            'organization': organization,
            'total_repos': len(repos),
            'total_stars': total_stars,
            'total_forks': total_forks,
            'active_last_30d': len(recently_active),
            'recent_activity': recent_summary,
            'activity_level': 'High' if len(recently_active) > 10 else ('Moderate' if len(recently_active) > 3 else 'Low'),
            'top_repos': repos[:5],  # Top 5 by stars
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return (json.dumps(result), 200, headers)
        
    except requests.exceptions.RequestException as e:
        logger.error(f"GitHub API error for {company}: {e}", exc_info=True)
        return (json.dumps({
            'success': False,
            'error': f'GitHub API request failed: {str(e)}'
        }), 502, headers)
    except Exception as e:
        logger.error(f"Error fetching GitHub data for {company}: {e}", exc_info=True)
        return (json.dumps({
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        }), 500, headers)


# For local testing
if __name__ == "__main__":
    class MockRequest:
        def __init__(self):
            self.method = 'POST'
            
        def get_json(self, silent=False):
            return {"company": "Anthropic"}
    
    result = github_activity(MockRequest())
    print(result[0])
