# Acme Logistics — Inbound Carrier Sales Agent
*Built on HappyRobot*

---

## What it does

Alex is an AI voice agent that picks up inbound calls from freight carriers looking to book loads. It handles the entire conversation without human involvement — verifying the carrier, finding a matching load, negotiating the rate, collecting contact details, and confirming the booking.

---

## Call Flow

1. **Greet & identify** — asks for the carrier's MC number
2. **FMCSA check** — verifies operating authority in real time; ends the call immediately if the carrier is not authorized
3. **Load search** — asks for origin, destination, and equipment type; searches available loads
4. **Pitch** — presents up to 3 matching loads with pickup date, weight, commodity, and rate
5. **Negotiate** — counters carrier offers over up to 3 rounds; never goes below 90% of the listed rate
6. **Contact collection** — collects name, phone, and email before confirming
7. **Book & log** — confirms the load, saves the full call record

---

## Tools

The agent uses three tools during the call to interact with external systems:

- **verify_carrier** — live FMCSA DOT lookup for carrier operating authority
- **search_loads** — finds available loads by lane and equipment type
- **save_call** — records the full outcome, rates, and contact details to the database

---

## Dashboard

A custom-built analytics dashboard tracks every call in real time:

- Booking rate, average agreed rate, and negotiation rounds
- Outcome breakdown (booked / declined / no deal / invalid carrier)
- Carrier sentiment per call
- Full call log with load details, commodity, dimensions, and rates

---

## Technical setup

- **Agent:** HappyRobot platform (V3 engine)
- **Backend:** Python / FastAPI, deployed on Railway with HTTPS and API key authentication
- **Dashboard:** GitHub Pages
- **Containerization:** Docker + docker-compose included for local deployment

---

## Links

- Agent: https://platform.happyrobot.ai/fdeingohartmann/workflows/vxwad2ig5ico/editor/tu7gqzc4d4rg
- Dashboard: https://ihartmann-commits.github.io/happyrobot-carrier-sales/
- Repository: https://github.com/ihartmann-commits/happyrobot-carrier-sales
