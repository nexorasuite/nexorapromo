# nz_thread.py
import requests, time, random, os, json
from threading import Event

stop_event = Event()
LOOP = True  # Set to False to stop after one cycle
ACCESS_TOKEN = "EAAT3Q4oZCLo0BQjTSQXZB7w2FDaIjWkHWhYeW1GI5YoDYYWilYiP6FhZC8RUz2UQaZCfNp5lSpIIfgZB3ThWuLIdine7qZB1QhYHaZCDsl5w0FZA6dZCYNZC3tGyHZCsH6xYRxupxIGx5Pq66YBFkx0h5umTHJuGLgrGHyCCq83YlSvc6jPgExp2ZBEDazStFoRtBAZDZD"
PAGE_ID = "967550829768297"
IMAGE_FOLDER = "images"
POST_INTERVAL = 30 * 60
FB_API_URL = f"https://graph.facebook.com/v19.0/{PAGE_ID}/photos"
POSTS_FILE = "posts/visa_posts.json"

def load_posts():
    with open(POSTS_FILE, 'r') as f:
        return json.load(f)

def post_on_facebook(message, image_filename):
    path = os.path.join(IMAGE_FOLDER, image_filename)
    if not os.path.exists(path):
        print(f"Image not found: {path}")
        return

    with open(path, 'rb') as img:
        files = {'source': (image_filename, img, 'image/jpeg')}
        data = {"message": message, "access_token": ACCESS_TOKEN}
        res = requests.post(FB_API_URL, files=files, data=data).json()
        print("✅ Posted" if "id" in res else "❌ Failed:", res)

def run_nz():
    posts = load_posts()
    random.shuffle(posts)
    while not stop_event.is_set():
        for post in posts:
            if stop_event.is_set():
                break
            post_on_facebook(post["message"], post["image_filename"])
            delay_seconds = int(post.get("delay", "10")) * 60
            time.sleep(delay_seconds)
        if not LOOP:
            break

def stop_nz():
    stop_event.set()
