# AD Wayfinder

An interactive Active Directory topology visualizer — think of it as a network
map for your AD.  Browse OUs and groups, drill into memberships, see full user
profiles, and get automatic alerts for stale-but-enabled accounts.

---

## Features

| Feature | Description |
|---|---|
| **Interactive topology graph** | Zoomable, pannable graph of your domain.  Click an OU to expand/collapse its children. |
| **Drill-down detail panel** | Click any node (domain, OU, group, or user) to see its full details in the side panel. |
| **User profiles** | Display name, email, phone, department, title, last login, group memberships, etc. |
| **Stale account alerts** | Any enabled account that hasn't logged in for ≥ 6 months (configurable) is flagged. |
| **Alerts view** | Filterable table of all flagged accounts — filter by OU, type (never logged in vs. old login), and sort by any column. |
| **Global search** | Search users, groups, and OUs by name, username, or email with instant results. |
| **Demo mode** | Ships with a realistic sample AD (Acme Corporation) so you can explore without a live DC. |

---

## Quick Start (Demo Mode)

**Prerequisites:** Python 3.10+, Node 18+

```bash
# 1. Backend
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # USE_MOCK_DATA=true by default
python app.py

# 2. Frontend (new terminal)
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

---

## Connecting to a Real Active Directory

1. Copy `backend/.env.example` → `backend/.env`
2. Fill in your DC details:

```env
USE_MOCK_DATA=false
AD_HOST=your-dc.corp.example.com
AD_PORT=389          # or 636 for LDAPS
AD_USER=CORP\svc_adwayfinder
AD_PASSWORD=SuperSecretPassword
AD_BASE_DN=DC=corp,DC=example,DC=com
AD_USE_SSL=false     # set true if using port 636
AD_USE_TLS=false     # set true to STARTTLS on port 389
STALE_ACCOUNT_DAYS=180
```

3. The service account needs **read-only** access to AD (standard Domain Users is usually sufficient for the attributes queried).

---

## Docker Compose

```bash
# Demo mode
docker compose up --build

# Live AD — create a .env file first, then:
docker compose --env-file .env up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

---

## Alert Logic

An account is flagged **stale** when **all** of the following are true:

1. `userAccountControl` does **not** have the `ACCOUNTDISABLE` bit set (account is enabled)
2. `lastLogonTimestamp` is either missing/zero **or** more than `STALE_ACCOUNT_DAYS` days ago

The threshold defaults to **180 days (6 months)** and can be changed via the
`STALE_ACCOUNT_DAYS` environment variable.

---

## Project Structure

```
AD-wayfinder/
├── backend/
│   ├── app.py           Flask API (routes)
│   ├── ad_client.py     Live LDAP client (ldap3)
│   ├── mock_data.py     Demo data + MockADClient
│   ├── config.py        Environment variable loading
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx               Root component + state
│   │   ├── api/adApi.js          Fetch wrappers
│   │   └── components/
│   │       ├── Header.jsx        Nav bar + global search
│   │       ├── TopologyMap.jsx   React Flow graph
│   │       ├── DetailPanel.jsx   Side panel (OU/group/user details)
│   │       ├── AlertsPanel.jsx   Stale accounts table
│   │       └── nodes/            Custom React Flow node components
│   └── package.json
└── docker-compose.yml
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, React Flow (graph), Tailwind CSS, Lucide icons |
| Backend | Python 3, Flask, ldap3, python-dotenv |
| Graph layout | dagre (hierarchical auto-layout) |
| Container | Docker + nginx (frontend), gunicorn (backend) |
