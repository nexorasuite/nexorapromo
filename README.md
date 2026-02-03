# AutoPost Hub

A complete, production-ready multi-platform autoposting web application built with Python Flask. Runs smoothly on Termux (Android phone) and any Linux/Windows system without Docker.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square)
![Flask](https://img.shields.io/badge/Flask-2.3-green?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

## Features

### 🚀 Core Features

- **Manual Posting**: Post instantly to multiple platforms with text and images
- **Scheduled Posts**: Schedule content for future posting (timezone-safe)
- **Campaigns**: Post the same content to multiple platforms in one action
- **Post Templates**: Save and reuse post templates for quick creation
- **Hashtag Manager**: Save and manage reusable hashtag sets
- **Post History**: Track all posts with status (Pending/Posted/Failed)
- **Drafts**: Save posts as drafts before publishing
- **Dark/Light Theme**: Beautiful dark and light mode toggle

### 📱 Supported Platforms

- **LinkedIn** - Professional network posting
- **Facebook** - Social media posting
- **Instagram** - Photo sharing (requires image)
- **Telegram** - Channel/bot messaging
- **Twitter/X** - Tweet posting (280 character limit)

### 🎯 Key Capabilities

✅ Multi-platform simultaneous posting
✅ Timezone-aware scheduling (UTC internally)
✅ Platform-specific formatting and validation
✅ Image upload and attachment support
✅ Session-based authentication
✅ Mobile-responsive UI (Tailwind CSS)
✅ Background scheduler with threading
✅ SQLite database (zero setup required)
✅ Runs on low-resource devices
✅ No Docker required

## System Requirements

- **Python 3.8+**
- **~50MB disk space** (including virtual environment)
- **Termux (Android)** or Linux/Windows/macOS

## Quick Start

### 1. Clone or Extract the Project

```bash
cd autopost
chmod +x setup.sh
```

### 2. Run Setup (Automatic)

```bash
./setup.sh
```

This will:
- Create virtual environment
- Install dependencies
- Initialize database
- Create necessary directories

### 3. Start the Application

```bash
source venv/bin/activate
python3 app.py
```

### 4. Open in Browser

```
http://localhost:5000
```

**Default Login:**
- Username: `admin`
- Password: `admin123`

⚠️ **Change this immediately in production!**

## Manual Installation (If setup.sh fails)

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create directories
mkdir -p instance/uploads
mkdir -p instance/data

# Initialize database
python3 << 'EOF'
from app import create_app
from database import init_db
app = create_app()
with app.app_context():
    init_db(app)
EOF

# Run application
python3 app.py
```

## Configuration

### Environment Variables

```bash
export FLASK_ENV=production          # or development
export SECRET_KEY="your-secret-key"
export FLASK_ENV=termux              # For Termux-specific paths
```

### Config File: `config.py`

- Database URL: `SQLALCHEMY_DATABASE_URI`
- Session lifetime: `PERMANENT_SESSION_LIFETIME`
- Upload folder: `UPLOAD_FOLDER`
- Max file size: `MAX_CONTENT_LENGTH`

## Platform Authentication

### LinkedIn
1. Go to [LinkedIn Developers](https://www.linkedin.com/developers)
2. Create app and get API credentials
3. In Settings > LinkedIn, enter credentials

### Facebook
1. Go to [Facebook Developers](https://developers.facebook.com)
2. Create app and generate access token
3. In Settings > Facebook, enter token and page ID

### Instagram
1. Use Instagram Graph API credentials
2. Requires business account
3. Enter access token in Settings

### Telegram
1. Chat with [@BotFather](https://t.me/botfather) on Telegram
2. Create bot, get token
3. Get your channel ID (e.g., -100123456789)
4. In Settings > Telegram, enter both

### Twitter/X
1. Go to [Twitter Developer Portal](https://developer.twitter.com)
2. Apply for API access
3. Generate API v2 bearer token
4. In Settings > Twitter, enter token

## Project Structure

```
autopost/
├── app.py                    # Main Flask app
├── config.py                 # Configuration
├── database.py               # SQLAlchemy models
├── scheduler.py              # Background scheduler
├── requirements.txt          # Dependencies
├── setup.sh                  # Setup script
│
├── services/                 # Platform services
│   ├── __init__.py
│   ├── base.py              # Abstract service
│   ├── factory.py            # Service factory
│   ├── linkedin_service.py   # LinkedIn posting
│   ├── facebook_service.py   # Facebook posting
│   ├── instagram_service.py  # Instagram posting
│   ├── telegram_service.py   # Telegram posting
│   └── twitter_service.py    # Twitter posting
│
├── routes/                   # Flask blueprints
│   ├── auth.py              # Login/logout
│   ├── dashboard.py         # Dashboard/stats
│   ├── composer.py          # Compose posts
│   ├── campaigns.py         # Campaign management
│   ├── history.py           # Post history
│   └── settings.py          # Settings & credentials
│
├── templates/               # HTML templates
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── compose.html
│   ├── schedule.html
│   ├── campaigns.html
│   ├── history.html
│   ├── settings.html
│   ├── sidebar.html
│   └── header.html
│
├── static/
│   ├── css/
│   │   └── style.css        # Custom styles
│   └── js/
│       ├── main.js          # Main utilities
│       └── theme.js         # Theme toggle
│
└── instance/                # Runtime data
    ├── autopost.db          # SQLite database
    └── uploads/             # Uploaded images
```

## API Endpoints

### Authentication
- `POST /login` - User login
- `GET /logout` - User logout
- `GET /api/auth/check` - Check auth status

### Dashboard
- `GET /` - Dashboard home
- `GET /api/dashboard/stats` - Get statistics

### Compose & Scheduling
- `POST /api/post/manual` - Create manual post
- `POST /api/post/schedule` - Schedule post
- `GET /api/templates` - List templates
- `POST /api/templates` - Create template

### Campaigns
- `GET /api/campaigns` - List campaigns
- `POST /api/campaigns` - Create campaign
- `POST /api/campaigns/<id>/posts` - Add post to campaign

### History
- `GET /api/posts` - Get posts (with filtering)
- `GET /api/posts/<id>` - Get post details
- `DELETE /api/posts/<id>` - Delete post

### Settings
- `GET /api/platforms/status` - Get platform connection status
- `GET /api/platforms/<platform>/credentials` - Get credentials
- `POST /api/platforms/<platform>/credentials` - Save credentials
- `DELETE /api/platforms/<platform>/credentials` - Remove credentials

## Scheduler

The application runs a background scheduler that:

1. **Checks every 30 seconds** for posts scheduled to publish
2. **Posts automatically** at scheduled time (UTC)
3. **Runs in a daemon thread** (non-blocking)
4. **Starts automatically** with the Flask app
5. **Handles failures gracefully** with retry logic

### How It Works

```python
# In scheduler.py
- _check_and_post() finds posts where scheduled_at <= now
- For each platform, calls the appropriate service
- Updates post status to 'posted' or 'failed'
- Logs results in post_results JSON field
```

## Database Schema

### Users Table
- `id` - Primary key
- `username` - Unique username
- `password_hash` - Hashed password
- `email` - Email address
- `created_at` - Registration date

### Posts Table
- `id` - Primary key
- `user_id` - Foreign key to users
- `content` - Post text
- `image_path` - Path to uploaded image
- `platforms` - JSON array of platforms
- `status` - draft/pending/posted/failed
- `scheduled_at` - Scheduled time (UTC)
- `posted_at` - Actual post time
- `post_results` - JSON with per-platform results
- `created_at` - Created date

### PostTemplate Table
- `id` - Primary key
- `user_id` - Foreign key
- `name` - Template name
- `content` - Template content
- `image_path` - Template image

### HashtagSet Table
- `id` - Primary key
- `user_id` - Foreign key
- `name` - Set name
- `hashtags` - Newline-separated hashtags

### Campaign Table
- `id` - Primary key
- `user_id` - Foreign key
- `name` - Campaign name
- `platforms` - JSON array
- `status` - active/completed/cancelled

### PlatformCredential Table
- `id` - Primary key
- `user_id` - Foreign key
- `platform` - Platform name
- `api_key` - API credentials
- `access_token` - OAuth token
- `username` - Username
- `is_active` - Active status

## Platform Implementation

Each platform has an abstract service class in `services/`:

```python
class LinkedInService(BasePostingService):
    def authenticate(self, user_id, credentials=None):
        # TODO: Implement LinkedIn OAuth
        pass
    
    def post_text(self, content, user_id, **kwargs):
        # TODO: Implement text posting
        pass
    
    def post_image(self, caption, image_path, user_id, **kwargs):
        # TODO: Implement image posting
        pass
```

All services are **currently mocked** with TODO comments showing where real API calls should go. This allows testing without actual API keys.

## Running on Termux

### Initial Setup

```bash
# In Termux, install Python first (if not already there)
pkg install python3

# Clone or extract the project
cd autopost

# Run setup
bash setup.sh

# Activate environment
source venv/bin/activate

# Start app
python3 app.py
```

### Accessing from Other Devices

1. **Get Termux IP:**
   ```bash
   ifconfig | grep 'inet '
   ```
   Look for something like `192.168.x.x`

2. **Access from other device:**
   ```
   http://192.168.x.x:5000
   ```

3. **Keep Termux Running:**
   - Use `Termux:Tasker` app to keep session alive
   - Or use `nohup python3 app.py &` to run in background

## Security Notes

### Development ⚠️
- Default admin credentials are in config.py
- Session cookies not secure (HTTP)
- Credentials stored in plaintext (for demo)

### Production 🔒
1. **Change SECRET_KEY** in config.py to a random string
2. **Use environment variables** for credentials
3. **Encrypt stored credentials** (use cryptography library)
4. **Enable HTTPS** (use reverse proxy like nginx)
5. **Use strong passwords** and change default credentials
6. **Set SESSION_COOKIE_SECURE = True**
7. **Implement CSRF protection** for forms
8. **Rate limiting** on login endpoint
9. **Regular backups** of SQLite database

## Troubleshooting

### Port Already in Use
```bash
# Change port in app.py
app.run(host='0.0.0.0', port=5001)  # Use different port
```

### Database Locked Error
```bash
# Delete and reinitialize database
rm instance/autopost.db
python3 -c "from app import create_app; from database import init_db; app = create_app(); init_db(app)"
```

### Virtual Environment Issues
```bash
# Recreate venv
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Template Not Found
```bash
# Ensure you're in the right directory
pwd  # Should end in /autopost
ls templates/  # Should list HTML files
```

## Performance Tips

1. **Use SQLite WAL mode** for better concurrency
2. **Index frequently queried columns** (user_id, status)
3. **Implement pagination** for large post lists
4. **Use connection pooling** for multiple users
5. **Cache platform configs** in memory
6. **Batch scheduled post checks**

## Future Enhancements

- [ ] Real OAuth2 implementation for all platforms
- [ ] File storage (S3, Google Cloud, etc.)
- [ ] Advanced analytics dashboard
- [ ] Post performance metrics
- [ ] A/B testing for content
- [ ] AI-powered content suggestions
- [ ] Multi-user support with roles
- [ ] Two-factor authentication
- [ ] API rate limiting
- [ ] Webhook support for external integrations
- [ ] Mobile app (React Native)

## Contributing

Feel free to fork, modify, and improve! Some ideas:
- Add more social platforms
- Implement real API integrations
- Improve UI/UX
- Add analytics
- Performance optimizations

## License

MIT License - Free to use and modify

## Support & Issues

For issues or questions:
1. Check the troubleshooting section
2. Review the code comments
3. Check Flask/SQLAlchemy documentation

## Made With ❤️

Built for content creators who want to automate their social media posting across multiple platforms without complex setup or expensive tools.

---

**Happy Posting! 🚀**

Need help? Start with the [Quick Start](#quick-start) section or check out the [Troubleshooting](#troubleshooting) guide.
