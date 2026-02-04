import json
import threading
import os
from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

POSTS_DIR = "posts"
IMAGE_DIR = "images"
SUITE_FILE = os.path.join(POSTS_DIR, "visa_posts.json")
INVESTMENTS_FILE = os.path.join(POSTS_DIR, "tour_posts.json")
INSTA_FILE = os.path.join(POSTS_DIR, "insta_posts.json")

# Global variables for thread control
insta_running = False
suite_running = False
investments_running = False
insta_thread = None
suite_thread = None
investments_thread = None

def load_posts(filepath):
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except:
        return []

def save_posts(filepath, posts):
    with open(filepath, 'w') as f:
        json.dump(posts, f, indent=2)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/posts/<category>')
def get_posts(category):
    if category == 'suite':
        posts = load_posts(SUITE_FILE)
    elif category == 'investments':
        posts = load_posts(INVESTMENTS_FILE)
    elif category == 'insta':
        posts = load_posts(INSTA_FILE)
    else:
        posts = []

    return jsonify(posts)

@app.route('/api/posts/<category>', methods=['POST'])
def add_post(category):
    if category == 'suite':
        filepath = SUITE_FILE
    elif category == 'investments':
        filepath = INVESTMENTS_FILE
    elif category == 'insta':
        filepath = INSTA_FILE
    else:
        return jsonify({'error': 'Invalid category'}), 400

    data = request.get_json()
    message = data.get('message', '')
    image_filename = data.get('image_filename', '')
    delay = data.get('delay', '10')

    if not message:
        return jsonify({'error': 'Message is required'}), 400

    posts = load_posts(filepath)
    new_post = {
        'message': message,
        'image_filename': image_filename,
        'delay': delay
    }
    posts.append(new_post)
    save_posts(filepath, posts)

    return jsonify({'success': True, 'post': new_post})

@app.route('/api/posts/<category>/<int:index>', methods=['PUT'])
def update_post(category, index):
    if category == 'suite':
        filepath = SUITE_FILE
    elif category == 'investments':
        filepath = INVESTMENTS_FILE
    elif category == 'insta':
        filepath = INSTA_FILE
    else:
        return jsonify({'error': 'Invalid category'}), 400

    posts = load_posts(filepath)
    if 0 <= index < len(posts):
        data = request.get_json()
        posts[index]['message'] = data.get('message', posts[index]['message'])
        posts[index]['image_filename'] = data.get('image_filename', posts[index]['image_filename'])
        posts[index]['delay'] = data.get('delay', posts[index]['delay'])
        save_posts(filepath, posts)
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Post not found'}), 404

@app.route('/api/posts/<category>/<int:index>', methods=['DELETE'])
def delete_post(category, index):
    if category == 'suite':
        filepath = SUITE_FILE
    elif category == 'investments':
        filepath = INVESTMENTS_FILE
    elif category == 'insta':
        filepath = INSTA_FILE
    else:
        return jsonify({'error': 'Invalid category'}), 400

    posts = load_posts(filepath)
    if 0 <= index < len(posts):
        deleted_post = posts.pop(index)
        save_posts(filepath, posts)
        return jsonify({'success': True, 'deleted': deleted_post})
    else:
        return jsonify({'error': 'Post not found'}), 404

@app.route('/api/control/<action>/<category>', methods=['POST'])
def control_posting(action, category):
    global insta_running, suite_running, investments_running
    global insta_thread, suite_thread, investments_thread

    if category == 'insta':
        if action == 'start' and not insta_running:
            import insta
            insta_thread = threading.Thread(target=insta.run_insta_sync, daemon=True)
            insta_thread.start()
            insta_running = True
            return jsonify({'status': 'started', 'category': 'insta'})
        elif action == 'stop' and insta_running:
            import insta
            insta.stop_insta_sync()
            insta_running = False
            return jsonify({'status': 'stopped', 'category': 'insta'})

    elif category == 'suite':
        if action == 'start' and not suite_running:
            import nexora_suite
            suite_thread = threading.Thread(target=nexora_suite.run_nz, daemon=True)
            suite_thread.start()
            suite_running = True
            return jsonify({'status': 'started', 'category': 'suite'})
        elif action == 'stop' and suite_running:
            import nexora_suite
            nexora_suite.stop_nz()
            suite_running = False
            return jsonify({'status': 'stopped', 'category': 'suite'})

    elif category == 'investments':
        if action == 'start' and not investments_running:
            import nexora_investments
            investments_thread = threading.Thread(target=nexora_investments.run_tour, daemon=True)
            investments_thread.start()
            investments_running = True
            return jsonify({'status': 'started', 'category': 'investments'})
        elif action == 'stop' and investments_running:
            import nexora_investments
            nexora_investments.stop_tour()
            investments_running = False
            return jsonify({'status': 'stopped', 'category': 'investments'})

    return jsonify({'error': 'Invalid action or category'}), 400

@app.route('/api/control/<action>/all', methods=['POST'])
def control_all(action):
    results = []
    for category in ['insta', 'visa', 'tour']:
        try:
            result = control_posting(action, category)
            results.append(result.get_json())
        except:
            results.append({'error': f'Failed to {action} {category}'})
    return jsonify(results)

@app.route('/api/status')
def get_status():
    return jsonify({
        'insta_running': insta_running,
        'suite_running': suite_running,
        'investments_running': investments_running
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
