# Korea Industrial Accident Calculator API (한국 산재 전문 계산기 API)

A high-performance, zero-cost API for calculating South Korean Industrial Accident (Worker's Compensation) benefits.

## Features
- **Average Wage Calculation**: Precise calculation including bonuses and annual leave pay.
- **Temporary Disability Benefit**: 70% of average wage with automatic max/min caps.
- **Disability Benefit**: Grade-based (1-14) lump sum and pension estimation.
- **Survivor & Funeral Benefit**: Legal pension and funeral expense calculation.
- **Automated Data Updates**: 2026 standards automatically updated via GitHub Actions.

## Tech Stack
- **Backend**: FastAPI (Python)
- **Deployment**: Vercel (Serverless)
- **Automation**: GitHub Actions + BeautifulSoup
- **Aesthetics**: Glassmorphism UI for Documentation

## Quick Start (Local)
1. Install dependencies: `pip install -r requirements.txt`
2. Run server: `uvicorn main:app --reload`
3. Visit: `http://localhost:8000`

## Deployment
Deploys automatically to Vercel. For RapidAPI integration, point your dashboard to the Vercel URL.

---
*Created by [chenghun1234-dotcom](https://github.com/chenghun1234-dotcom)*
