# Fivetran USPTO Patents Connector

Custom Fivetran connector that syncs patent data from Google Patents API into BigQuery.

## Features

- Fetches patents for multiple companies (Anthropic, OpenAI, Google)
- Uses Google Patents XHR API for real-time data
- Falls back to mock data if API unavailable
- Automatic schema mapping to BigQuery
- UPSERT operations for deduplication

## Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Run connector in debug mode
python connector.py
```

## Deploy to Fivetran

```bash
# Package connector
zip -r connector.zip connector.py configuration.json secrets.json state.json requirements.txt

# Upload to Fivetran dashboard:
# 1. Go to https://fivetran.com/dashboard
# 2. Click "Add Connector" → "Custom Connector"
# 3. Upload connector.zip
# 4. Configure destination: BigQuery
# 5. Set dataset name: "patent_intelligence"
# 6. Run initial sync
```

## Configuration

Edit `configuration.json` to monitor different companies:

```json
{
  "companies": ["Anthropic", "OpenAI", "Google", "Microsoft"]
}
```

## Schema

The connector creates a `patents` table in BigQuery with:
- `patent_number` (STRING, PRIMARY KEY)
- `title` (STRING)
- `abstract` (STRING)
- `company` (STRING)
- `grant_date` (STRING)
- `filing_date` (STRING)
- `inventors` (JSON array)
- `cpc_classifications` (JSON array)
- `patent_url` (STRING)
- `source` (STRING)
- `scraped_at` (UTC_DATETIME)

## Data Sources

1. **Primary**: Google Patents XHR API
2. **Fallback**: Mock patent data (for testing/demo)

## Ported From

This connector is ported from the AWS IntelAgent patent_monitor Lambda function,
maintaining the same data fetching logic and structure.
