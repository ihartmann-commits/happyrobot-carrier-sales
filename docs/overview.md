# Acme Logistics — Inbound Carrier Sales Agent
*Technical Overview*

---

## What was built

An AI-powered inbound voice agent that handles calls from freight carriers looking to book loads. The agent runs on the HappyRobot platform and manages the full conversation autonomously — from carrier verification to load booking.

---

## Conversation Flow

1. Greet the carrier and collect their MC number
2. Verify operating authority via FMCSA
3. Ask for origin, destination, and equipment type
4. Search available loads and pitch up to 3 options
5. Negotiate the rate (max 3 rounds, floor at 90% of listed rate)
6. Collect contact details (name, phone, email)
7. Confirm booking and save the call record

---

## Tools

Tools are functions the AI agent calls during a conversation to interact with external systems instead of just generating text. Three tools were built:

| Tool | What it does |
|------|-------------|
| `verify_carrier` | Checks FMCSA DOT database for active operating authority |
| `search_loads` | Returns matching loads by origin, destination, and equipment type |
| `save_call` | Persists full call outcome to the database |

---

## Architecture

```
HappyRobot (Voice + Agent)
        ↓
FastAPI (Railway) — HTTPS + API Key Auth
        ↓
SQLite Database
```

- **Backend:** Python / FastAPI, deployed on Railway with automatic GitHub deploys
- **FMCSA:** Live DOT QC API with mock carrier fallback for demos
- **Load matching:** Fuzzy state-name matching (e.g. "Florida" → "FL")
- **Security:** HTTPS via Let's Encrypt, API key authentication on all endpoints
- **Containerization:** Dockerfile + docker-compose included for local deployment

---

## Dashboard

A custom analytics dashboard deployed on GitHub Pages showing:

- Total calls, booking rate, avg agreed rate, avg negotiation rounds
- Call outcome breakdown (booked / declined / no deal / invalid carrier)
- Carrier sentiment distribution
- Full call log with load details, rates, commodity type, and dimensions

---

## Current Metrics (live data)

| Metric | Value |
|--------|-------|
| Total Calls | 21 |
| Booking Rate | 52.4% |
| Avg Agreed Rate | $1,938 |
| Avg Negotiation Rounds | 0.9 |
| FMCSA Verified Rate | 81% |

---

## Links

- Agent Workflow: https://platform.happyrobot.ai/fdeingohartmann/workflows/vxwad2ig5ico/editor/tu7gqzc4d4rg
- Dashboard: https://ihartmann-commits.github.io/happyrobot-carrier-sales/
- API Docs: https://happyrobot-carrier-sales-production-a675.up.railway.app/docs
- Repository: https://github.com/ihartmann-commits/happyrobot-carrier-sales
