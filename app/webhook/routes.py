from flask import request, jsonify
from datetime import datetime
import uuid
from app.webhook import webhook_bp
from app.extensions import mongo


def format_timestamp(dt):
    """Format datetime to readable string: 1st April 2021 - 9:30 PM UTC"""
    day = dt.day
    suffix = 'th' if 11 <= day <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
    return dt.strftime(f'{day}{suffix} %B %Y - %I:%M %p UTC')


def parse_github_timestamp(timestamp_str):
    """Parse GitHub timestamp to datetime object"""
    if timestamp_str:
        try:
            return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except:
            pass
    return datetime.utcnow()


@webhook_bp.route('/webhook', methods=['POST'])
@webhook_bp.route('/webhook/receiver', methods=['POST'])
def webhook_receiver():
    """
    Handle incoming GitHub webhook events
    Endpoint: POST /webhook or POST /webhook/receiver
    """
    if mongo.collection is None:
        return jsonify({'error': 'Database not connected'}), 500
    
    # Get the event type from GitHub headers
    event_type = request.headers.get('X-GitHub-Event', 'unknown')
    payload = request.json
    
    if not payload:
        return jsonify({'error': 'No payload received'}), 400
    
    event_data = None
    
    if event_type == 'push':
        # Handle PUSH event
        event_data = {
            'request_id': str(uuid.uuid4()),
            'author': payload.get('pusher', {}).get('name', 'Unknown'),
            'action': 'PUSH',
            'from_branch': '',
            'to_branch': payload.get('ref', '').replace('refs/heads/', ''),
            'timestamp': parse_github_timestamp(
                payload.get('head_commit', {}).get('timestamp')
            )
        }
    
    elif event_type == 'pull_request':
        pr = payload.get('pull_request', {})
        action = payload.get('action', '')
        
        # Check if this is a MERGE event (PR closed and merged)
        if action == 'closed' and pr.get('merged', False):
            event_data = {
                'request_id': str(uuid.uuid4()),
                'author': pr.get('merged_by', {}).get('login', 
                          pr.get('user', {}).get('login', 'Unknown')),
                'action': 'MERGE',
                'from_branch': pr.get('head', {}).get('ref', ''),
                'to_branch': pr.get('base', {}).get('ref', ''),
                'timestamp': parse_github_timestamp(pr.get('merged_at'))
            }
        elif action in ['opened', 'reopened', 'synchronize']:
            # Handle PULL_REQUEST event
            event_data = {
                'request_id': str(uuid.uuid4()),
                'author': pr.get('user', {}).get('login', 'Unknown'),
                'action': 'PULL_REQUEST',
                'from_branch': pr.get('head', {}).get('ref', ''),
                'to_branch': pr.get('base', {}).get('ref', ''),
                'timestamp': parse_github_timestamp(pr.get('created_at'))
            }
    
    if event_data:
        # Store in MongoDB
        mongo.collection.insert_one(event_data)
        print(f"📥 Stored {event_data['action']} event from {event_data['author']}")
        return jsonify({'status': 'success', 'event': event_data['action']}), 200
    
    return jsonify({'status': 'ignored', 'event_type': event_type}), 200


@webhook_bp.route('/api/events', methods=['GET'])
def get_events():
    """API endpoint for the UI to fetch events"""
    if mongo.collection is None:
        return jsonify({'error': 'Database not connected'}), 500
    
    # Fetch latest 50 events, sorted by timestamp descending
    events = list(mongo.collection.find({}, {'_id': 0}).sort('timestamp', -1).limit(50))
    
    # Format events for the UI
    formatted_events = []
    for event in events:
        timestamp = event.get('timestamp')
        if isinstance(timestamp, datetime):
            formatted_time = format_timestamp(timestamp)
        else:
            formatted_time = str(timestamp)
        
        formatted_event = {
            'request_id': event.get('request_id'),
            'author': event.get('author'),
            'action': event.get('action'),
            'from_branch': event.get('from_branch'),
            'to_branch': event.get('to_branch'),
            'timestamp': formatted_time,
            'raw_timestamp': timestamp.isoformat() if isinstance(timestamp, datetime) else str(timestamp)
        }
        formatted_events.append(formatted_event)
    
    return jsonify({'events': formatted_events}), 200
