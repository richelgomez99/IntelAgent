# Patent Tracker - AI Competitive Intelligence

🔍 AI-powered competitive intelligence using Fivetran + Google Cloud + Gemini

**Hackathon Project**: Google Cloud Hackathon 2025

## Overview

Patent Tracker is an AI agent that analyzes competitive intelligence by aggregating data from multiple sources:
- USPTO Patents (via Fivetran → BigQuery)
- Job Postings (Cloud Functions → Firestore)
- News Coverage (Cloud Functions → Firestore)
- GitHub Activity (Cloud Functions → Firestore)

The system uses **Gemini 2.5 Pro** to orchestrate analysis across these data sources and provide strategic insights.

## Architecture

```
Fivetran → BigQuery (patents)
           ↓
Cloud Functions → Firestore (jobs, news, github)
           ↓
Streamlit + Gemini 2.5 Pro (AI agent)
```

## Tech Stack

- **Fivetran**: Custom connector for USPTO patent data
- **Google Cloud BigQuery**: Patent data warehouse
- **Cloud Functions**: Serverless data collectors
- **Firestore**: Multi-source data store
- **Cloud Run**: Streamlit app hosting
- **Vertex AI (Gemini 2.5 Pro)**: AI agent orchestration

## Features

- 🤖 AI agent with function calling
- 📊 Multi-source data aggregation
- 🔍 Strategic analysis and predictions
- 📈 Competitive intelligence reports
- 🎯 30/60/90 day forecasting

## Deployment

### Fivetran Connector
```bash
cd fivetran-connector
# Deploy to Fivetran
```

### Cloud Functions
```bash
cd cloud-functions/job-scraper
gcloud functions deploy job-scraper --gen2 --runtime=python311
# Repeat for news-search and github-activity
```

### Streamlit App
```bash
cd streamlit-app
gcloud builds submit --tag gcr.io/PROJECT_ID/patent-tracker-app
gcloud run deploy patent-tracker --image gcr.io/PROJECT_ID/patent-tracker-app
```

## Data Sources

1. **Patents**: Google Patents Public Data (via Fivetran)
2. **Jobs**: Greenhouse job boards (web scraping)
3. **News**: Google News RSS feeds
4. **GitHub**: GitHub public repository API

## Demo

Live app: [URL_HERE]

## Development Notes

This project was built for the Google Cloud Hackathon 2025, ported from a previous AWS implementation (IntelAgent).

## License

MIT
