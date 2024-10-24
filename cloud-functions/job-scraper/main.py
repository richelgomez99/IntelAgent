"""
Cloud Function: Job Scraper
Scrapes job postings from Greenhouse career pages
Ported from AWS IntelAgent job_scraper Lambda
"""
from google.cloud import firestore
import requests
from datetime import datetime, timedelta
import logging
import json
from typing import Dict, List, Any

# Initialize Firestore
db = firestore.Client()

# Company Greenhouse board names
COMPANY_GREENHOUSE_IDS = {
    "anthropic": "anthropic",
    "openai": "openai",
    "google": "google"
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_greenhouse_jobs(company_name: str) -> List[Dict[str, Any]]:
    """
    Fetch jobs from Greenhouse API with retry logic
    Ported from AWS Lambda
    
    Args:
        company_name: Company identifier for Greenhouse
        
    Returns:
        List of job dictionaries, or None if company has no public board
    """
    # Normalize company name
    company_key = company_name.lower().replace(" ", "")
    greenhouse_id = COMPANY_GREENHOUSE_IDS.get(company_key, company_name.lower())
    
    url = f"https://boards-api.greenhouse.io/v1/boards/{greenhouse_id}/jobs"
    
    headers = {
        'User-Agent': 'GCP-CompetitiveIntel-Agent/1.0 (Hackathon Project)'
    }
    
    try:
        response = requests.get(
            url,
            params={'content': 'true'},
            headers=headers,
            timeout=20
        )
        
        # Return None for 404 (no public board) instead of raising error
        if response.status_code == 404:
            return None
        
        response.raise_for_status()
        
        data = response.json()
        return data.get('jobs', [])
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching jobs for {company_name}: {e}")
        raise


def filter_recent_jobs(jobs: List[Dict[str, Any]], days: int = 30) -> List[Dict[str, Any]]:
    """
    Filter jobs to only include those posted/updated in the last N days
    Same logic as AWS Lambda
    
    Args:
        jobs: List of job dictionaries
        days: Number of days to look back
        
    Returns:
        Filtered list of recent jobs
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    recent_jobs = []
    
    for job in jobs:
        updated_at = job.get('updated_at', '')
        if not updated_at:
            continue
            
        try:
            job_date = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            if job_date.replace(tzinfo=None) > cutoff_date:
                # Extract department name
                departments = job.get('departments', [])
                department = departments[0].get('name', 'N/A') if departments else 'N/A'
                
                # Extract location
                location = job.get('location', {})
                location_name = location.get('name', 'N/A')
                
                # Extract job description/content (Greenhouse provides this with content=true)
                job_content = job.get('content', '')
                description = ''
                if job_content:
                    description = job_content.strip()[:2000]  # Keep first 2000 chars for analysis
                
                recent_jobs.append({
                    'job_id': str(job.get('id', '')),
                    'title': job.get('title', 'N/A'),
                    'department': department,
                    'location': location_name,
                    'posted_date': updated_at,
                    'url': job.get('absolute_url', ''),
                    'description': description  # Full job description for AI analysis
                })
        except (ValueError, TypeError):
            # Skip jobs with invalid dates
            continue
    
    return recent_jobs


def calculate_competitive_score(jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate 0-100 competitive threat score based on hiring signals
    Ported from AWS Lambda
    
    Args:
        jobs: List of job dictionaries
        
    Returns:
        Dictionary with score and breakdown
    """
    if not jobs or len(jobs) == 0:
        return {
            'overall_score': 0,
            'threat_level': 'None',
            'velocity_score': 0,
            'diversity_score': 0,
            'strategic_score': 0,
            'reasoning': 'No hiring activity detected'
        }
    
    # Velocity score (0-40 points): Based on absolute job count
    velocity_score = min(40, (len(jobs) / 5))  # 1 point per 5 jobs, max 40
    
    # Diversity score (0-30 points): Department and location diversity
    departments = set(job.get('department', 'N/A') for job in jobs)
    locations = set(job.get('location', 'N/A') for job in jobs)
    diversity_score = min(30, (len(departments) * 3) + (len(locations) * 2))
    
    # Strategic score (0-30 points): High-value department hiring
    strategic_keywords = ['Research', 'AI', 'ML', 'Engineering', 'Product', 'Sales', 'Enterprise']
    strategic_count = sum(
        1 for job in jobs 
        if any(keyword.lower() in job.get('department', '').lower() for keyword in strategic_keywords)
    )
    strategic_score = min(30, strategic_count * 2)
    
    overall_score = velocity_score + diversity_score + strategic_score
    
    # Determine threat level
    if overall_score >= 75:
        threat_level = 'HIGH'
    elif overall_score >= 50:
        threat_level = 'MEDIUM'
    elif overall_score >= 25:
        threat_level = 'LOW'
    else:
        threat_level = 'MINIMAL'
    
    return {
        'overall_score': round(overall_score, 1),
        'threat_level': threat_level,
        'velocity_score': round(velocity_score, 1),
        'diversity_score': round(diversity_score, 1),
        'strategic_score': round(strategic_score, 1),
        'reasoning': f'{len(jobs)} open positions across {len(departments)} departments signals {threat_level.lower()} competitive activity'
    }


def extract_job_insights(jobs: List[Dict[str, Any]], company_name: str) -> Dict[str, Any]:
    """
    Extract high-level insights from job data
    Same logic as AWS Lambda
    
    Args:
        jobs: List of job dictionaries
        company_name: Company name
        
    Returns:
        Dictionary of insights
    """
    if not jobs:
        return {
            'summary': f'No recent job postings found for {company_name}',
            'hiring_velocity': 'None',
            'top_departments': [],
            'top_locations': [],
            'competitive_score': calculate_competitive_score([])
        }
    
    dept_counts = {}
    location_counts = {}
    
    for job in jobs:
        dept = job.get('department', 'N/A')
        loc = job.get('location', 'N/A')
        
        dept_counts[dept] = dept_counts.get(dept, 0) + 1
        location_counts[loc] = location_counts.get(loc, 0) + 1
    
    # Sort departments by count
    top_departments = sorted(dept_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    top_locations = sorted(location_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Determine hiring velocity
    velocity = 'Low'
    if len(jobs) > 20:
        velocity = 'High'
    elif len(jobs) > 10:
        velocity = 'Moderate'
    
    return {
        'summary': f'{company_name} has {len(jobs)} active job postings in the last 30 days',
        'hiring_velocity': velocity,
        'top_departments': [{'name': dept, 'count': count} for dept, count in top_departments],
        'top_locations': [{'name': loc, 'count': count} for loc, count in top_locations],
        'competitive_score': calculate_competitive_score(jobs)
    }


def job_scraper(request):
    """
    Cloud Function entry point
    HTTP-triggered function for scraping job data
    
    Args:
        request: Flask request object
        
    Returns:
        JSON response with job data
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
    company = request_json.get("company", "all") if request_json else "all"
    
    all_jobs = []
    results_by_company = {}
    
    try:
        # Scrape companies
        companies = [company] if company != "all" else COMPANY_GREENHOUSE_IDS.keys()
        
        for comp in companies:
            logger.info(f"Scraping jobs for {comp}")
            
            try:
                jobs_raw = fetch_greenhouse_jobs(comp)
                
                # Handle case where company has no Greenhouse board
                if jobs_raw is None:
                    logger.info(f"{comp} does not have a public Greenhouse job board")
                    results_by_company[comp] = {
                        'job_count': 0,
                        'message': f'{comp} does not have a public Greenhouse job board',
                        'recent_jobs': []
                    }
                    continue
                
                # Filter for recent jobs
                recent_jobs = filter_recent_jobs(jobs_raw, days=30)
                
                # Extract insights
                insights = extract_job_insights(recent_jobs, comp)
                
                # Store in Firestore
                for job in recent_jobs:
                    doc_id = f"{comp}_{job['job_id']}"
                    job['company'] = comp
                    job['scraped_at'] = datetime.utcnow().isoformat()
                    db.collection("jobs").document(doc_id).set(job)
                
                all_jobs.extend(recent_jobs)
                results_by_company[comp] = {
                    'company': comp,
                    'job_count': len(recent_jobs),
                    'recent_jobs': recent_jobs,  # Return ALL jobs for comprehensive analysis
                    'insights': insights
                }
                
            except Exception as e:
                logger.error(f"Error processing {comp}: {e}")
                results_by_company[comp] = {
                    'error': str(e),
                    'job_count': 0
                }
        
        return (json.dumps({
            'success': True,
            'total_jobs': len(all_jobs),
            'companies': results_by_company,
            'timestamp': datetime.utcnow().isoformat()
        }), 200, headers)
        
    except Exception as e:
        logger.error(f"Job scraper error: {e}")
        return (json.dumps({
            'success': False,
            'error': str(e)
        }), 500, headers)


# For local testing
if __name__ == "__main__":
    class MockRequest:
        def __init__(self):
            self.method = 'POST'
            
        def get_json(self, silent=False):
            return {"company": "Anthropic"}
    
    result = job_scraper(MockRequest())
    print(result[0])
