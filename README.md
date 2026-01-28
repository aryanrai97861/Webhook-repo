# GitHub Webhook Receiver

A Flask application that receives GitHub webhook events (Push, Pull Request, Merge), stores them in MongoDB, and displays them in a real-time dashboard.

Based on the reference structure from [techstax-dev/tsk-public-assignment-webhook-repo](https://github.com/techstax-dev/tsk-public-assignment-webhook-repo).

## Features

- 🔔 Receives GitHub webhook events in real-time
- 📊 Stores events in MongoDB with structured schema
- 🖥️ Clean, minimal dark-themed dashboard
- ⚡ Auto-refreshes every 15 seconds
- 🎨 Color-coded event types (Push, PR, Merge)

## Project Structure

```
webhook-repo/
├── app/
│   ├── __init__.py         # Application factory
│   ├── extensions.py       # MongoDB extension
│   └── webhook/
│       ├── __init__.py     # Webhook blueprint
│       └── routes.py       # Webhook endpoints
├── templates/
│   └── index.html          # Dashboard UI
├── static/
│   └── styles.css          # Styling
├── run.py                  # Entry point
├── requirements.txt
└── .env                    # Environment variables
```

## Setup

1. **Create a new virtual environment**

```bash
pip install virtualenv
virtualenv venv
```

2. **Activate the virtual env**

```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Install requirements**

```bash
pip install -r requirements.txt
```

4. **Configure MongoDB Atlas**

Create a `.env` file with your MongoDB connection:
```
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/github_events
DATABASE_NAME=github_events
COLLECTION_NAME=events
```

5. **Run the Flask application**

```bash
python run.py
```

6. **Endpoints**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Dashboard UI |
| `/webhook` | POST | GitHub webhook receiver |
| `/webhook/receiver` | POST | Alternative webhook endpoint |
| `/api/events` | GET | Fetch stored events (JSON) |

## MongoDB Schema

```json
{
  "request_id": "uuid",
  "author": "string",
  "action": "PUSH | PULL_REQUEST | MERGE",
  "from_branch": "string",
  "to_branch": "string",
  "timestamp": "datetime"
}
```

## Event Formats

| Event | Format |
|-------|--------|
| **PUSH** | `"{author}" pushed to "{branch}" on {timestamp}` |
| **PULL_REQUEST** | `"{author}" submitted a pull request from "{from}" to "{to}" on {timestamp}` |
| **MERGE** | `"{author}" merged branch "{from}" to "{to}" on {timestamp}` |

## Setting Up GitHub Webhook

1. Go to your `action-repo` on GitHub
2. Settings → Webhooks → Add webhook
3. Payload URL: `https://your-ngrok-url/webhook`
4. Content type: `application/json`
5. Select events: Pushes, Pull requests

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: MongoDB Atlas
- **Frontend**: Vanilla HTML/CSS/JavaScript
