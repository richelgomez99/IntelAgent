"""
Fivetran Connector for USPTO Patents
Fetches patent data from Google Patents API and loads into BigQuery
Ported from AWS IntelAgent Lambda function
"""
from fivetran_connector_sdk import Connector, Operations, Logging
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Iterator
import logging
import time

# Set up logging
logger = logging.getLogger(__name__)

def schema(configuration: Dict[str, Any]) -> list:
    """
    Define BigQuery table schema for patents
    Matches AWS IntelAgent patent data structure
    """
    return [
        {
            "table": "patents",
            "primary_key": ["patent_number"],
            "columns": {
                "patent_number": "STRING",
                "title": "STRING",
                "abstract": "STRING",
                "company": "STRING",
                "grant_date": "STRING",
                "filing_date": "STRING",
                "inventors": "JSON",  # Array of inventor names
                "cpc_classifications": "JSON",  # Patent classification codes
                "patent_url": "STRING",
                "source": "STRING",  # 'Google Patents' or 'Mock Data'
                "scraped_at": "UTC_DATETIME"
            }
        }
    ]

def update(configuration: Dict[str, Any], state: Dict[str, Any]) -> Iterator[Operations]:
    """
    Fetch patent data from Google Patents API
    Uses same fetch logic as AWS IntelAgent's patent_monitor Lambda
    
    Configuration parameters:
    - companies: Comma-separated list of company names (default: Anthropic,OpenAI,Google)
    """
    # Get configuration - convert comma-separated string to list
    companies_str = configuration.get("companies", "Anthropic,OpenAI,Google")
    companies = [c.strip() for c in companies_str.split(",")]
    
    logger.info(f"Fetching patents for companies: {companies}")
    
    for company in companies:
        try:
            # Try real Google Patents API first (same as AWS Lambda)
            result = fetch_patents_google(company, max_results=20)
            
            if result['success'] and result['patents']:
                patents = result['patents']
                source = 'Google Patents'
                logger.info(f"Found {len(patents)} patents for {company} from Google Patents")
            else:
                # Fallback to mock data (same as AWS Lambda)
                patents = get_mock_patents(company)
                source = 'Mock Data'
                logger.info(f"Using {len(patents)} mock patents for {company}")
            
            # Yield each patent as an UPSERT operation
            for patent in patents:
                # Transform data to match schema
                record = {
                    "patent_number": patent.get("patent_number", ""),
                    "title": patent.get("title", ""),
                    "abstract": patent.get("abstract", "")[:1000],  # Truncate if too long
                    "company": company,
                    "grant_date": patent.get("grant_date", ""),
                    "filing_date": patent.get("filing_date", ""),
                    "inventors": patent.get("inventors", []),
                    "cpc_classifications": patent.get("cpc_classifications", []),
                    "patent_url": patent.get("url", ""),
                    "source": source,
                    "scraped_at": datetime.utcnow().isoformat()
                }
                
                yield Operations.UPSERT("patents", record)
            
            # Rate limiting between companies
            time.sleep(2)
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching patents for {company}: {e}")
            # Continue with next company instead of failing completely
            continue
        except Exception as e:
            logger.error(f"Unexpected error for {company}: {e}")
            continue
    
    logger.info("Patent sync completed")


def fetch_patents_google(company_name: str, max_results: int = 20) -> Dict[str, Any]:
    """
    Fetch real patents from Google Patents XHR API
    Ported directly from AWS IntelAgent patent_monitor Lambda
    
    Args:
        company_name: Company name to search for
        max_results: Maximum number of patents to return
        
    Returns:
        Dictionary with patent data
    """
    # Google Patents XHR endpoint
    url = f"https://patents.google.com/xhr/query?url=q%3D{company_name}%26assignee%3D{company_name}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', {})
            total = results.get('total_num_results', 0)
            
            patents = []
            clusters = results.get('cluster', [])
            
            for cluster in clusters[:max_results]:
                for result in cluster.get('result', []):
                    patent_data = result.get('patent', {})
                    
                    patent = {
                        'patent_number': result.get('id', '').replace('patent/', '').replace('/en', ''),
                        'title': patent_data.get('title', '').strip(),
                        'abstract': patent_data.get('snippet', '').strip()[:300],
                        'url': f"https://patents.google.com/{result.get('id', '')}" if result.get('id') else None,
                        'source': 'Google Patents',
                        'inventors': [],  # Google Patents API doesn't provide this in initial results
                        'cpc_classifications': [],
                        'grant_date': '',
                        'filing_date': ''
                    }
                    
                    if patent['title']:
                        patents.append(patent)
            
            return {
                'success': True,
                'total_count': total,
                'patents': patents[:max_results]
            }
        else:
            return {'success': False, 'error': f'HTTP {response.status_code}', 'patents': []}
            
    except Exception as e:
        return {'success': False, 'error': str(e), 'patents': []}


def get_mock_patents(company_name: str) -> list:
    """
    Return mock patent data (same as AWS Lambda fallback)
    Used when Google Patents API is unavailable
    
    Args:
        company_name: Company name
        
    Returns:
        List of patent dictionaries
    """
    mock_patents = {
        'anthropic': [
            {
                'patent_number': 'US11234567',
                'title': 'Methods and Systems for Constitutional AI Training',
                'abstract': 'Systems and methods for training AI models using constitutional approaches to ensure safety and alignment...',
                'grant_date': '2024-03-15',
                'filing_date': '2023-09-15',
                'inventors': ['Dario Amodei', 'Chris Olah', 'Sam McCandlish'],
                'cpc_classifications': ['G06N3/08', 'G06F17/16'],
                'url': 'https://patents.google.com/patent/US11234567'
            },
            {
                'patent_number': 'US11345678',
                'title': 'Contextual Embedding Techniques for Large Language Models',
                'abstract': 'Novel approaches to context window expansion and efficient attention mechanisms for large language models...',
                'grant_date': '2024-06-20',
                'filing_date': '2023-12-20',
                'inventors': ['Tom Brown', 'Jared Kaplan', 'Amanda Askell'],
                'cpc_classifications': ['G06N3/04', 'G06F40/30'],
                'url': 'https://patents.google.com/patent/US11345678'
            },
            {
                'patent_number': 'US11456789',
                'title': 'Safety Mechanisms for AI-Assisted Code Generation',
                'abstract': 'Systems for detecting and preventing unsafe code patterns in AI-generated programming outputs...',
                'grant_date': '2024-09-10',
                'filing_date': '2024-03-10',
                'inventors': ['Catherine Olsson', 'Jackson Kernion'],
                'cpc_classifications': ['G06F8/30', 'G06N20/00'],
                'url': 'https://patents.google.com/patent/US11456789'
            }
        ],
        'openai': [
            {
                'patent_number': 'US11567890',
                'title': 'Reinforcement Learning from Human Feedback Systems',
                'abstract': 'Methods for training language models using human preference feedback to improve alignment and safety...',
                'grant_date': '2024-02-28',
                'filing_date': '2023-08-28',
                'inventors': ['John Schulman', 'Filip Wolski', 'Paul Christiano'],
                'cpc_classifications': ['G06N3/08', 'G06N20/10'],
                'url': 'https://patents.google.com/patent/US11567890'
            },
            {
                'patent_number': 'US11678901',
                'title': 'Multimodal AI Architecture for Vision and Language',
                'abstract': 'Integrated systems for processing and generating content across visual and linguistic modalities...',
                'grant_date': '2024-05-15',
                'filing_date': '2023-11-15',
                'inventors': ['Alec Radford', 'Ilya Sutskever', 'Greg Brockman'],
                'cpc_classifications': ['G06N3/04', 'G06V10/82'],
                'url': 'https://patents.google.com/patent/US11678901'
            },
            {
                'patent_number': 'US11789012',
                'title': 'Token-Efficient Prompt Engineering Methods',
                'abstract': 'Techniques for optimizing prompt construction to maximize model performance with minimal token usage...',
                'grant_date': '2024-08-22',
                'filing_date': '2024-02-22',
                'inventors': ['Wojciech Zaremba', 'Jan Leike'],
                'cpc_classifications': ['G06F40/20', 'G06N3/045'],
                'url': 'https://patents.google.com/patent/US11789012'
            }
        ],
        'google': [
            {
                'patent_number': 'US11890123',
                'title': 'Transformer Architecture Optimization for Large Scale Models',
                'abstract': 'Methods for efficiently scaling transformer models to trillions of parameters...',
                'grant_date': '2024-04-10',
                'filing_date': '2023-10-10',
                'inventors': ['Jeff Dean', 'Demis Hassabis', 'Sundar Pichai'],
                'cpc_classifications': ['G06N3/04', 'G06N3/08'],
                'url': 'https://patents.google.com/patent/US11890123'
            }
        ]
    }
    
    company_lower = company_name.lower()
    
    # Return mock data for known companies
    if company_lower in mock_patents:
        return mock_patents[company_lower]
    
    # Return empty list for unknown companies
    return []


# Create connector instance
connector = Connector(update=update, schema=schema)

if __name__ == "__main__":
    # For local testing
    connector.debug()
