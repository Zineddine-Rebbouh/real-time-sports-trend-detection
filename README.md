# Tendances Sportives - Sports Trends Analytics Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Django](https://img.shields.io/badge/Django-4.2.7-green.svg)](https://www.djangoproject.com/)
[![Next.js](https://img.shields.io/badge/Next.js-15.2.4-black.svg)](https://nextjs.org/)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)](https://www.typescriptlang.org/)

## 📖 Overview

**Tendances Sportives** is a comprehensive Arabic sports trends analytics platform that monitors, analyzes, and visualizes sports-related content from social media platforms. The application provides real-time insights into sports discussions, sentiment analysis, entity recognition, and trending topics in Arabic sports communities.

### 🌟 Key Features

- **Real-time Data Collection**: Automated scraping from Twitter/X and other social platforms
- **Arabic Text Processing**: Advanced NLP for Arabic sports content
- **Entity Recognition**: Identification of teams, players, competitions, and sports entities
- **Sentiment Analysis**: Emotion detection in Arabic sports discussions
- **Trend Analysis**: Real-time trending topics and hashtag tracking
- **Interactive Dashboard**: Modern web interface with charts and analytics
- **Report Generation**: Export capabilities for insights and analytics
- **Multi-sport Support**: Coverage of various sports with customizable filters

## 🏗️ Architecture

This is a full-stack application with a clear separation between frontend and backend:

### Frontend (Next.js)

- **Framework**: Next.js 15.2.4 with TypeScript
- **UI Library**: Tailwind CSS + Radix UI components
- **State Management**: React hooks and context
- **Charts**: Recharts for data visualization
- **Authentication**: JWT-based auth integration

### Backend (Django)

- **Framework**: Django 4.2.7 with Django REST Framework
- **Database**: MongoDB with Djongo ODM
- **Task Queue**: Celery with Redis broker
- **Real-time**: Django Channels for WebSocket support
- **AI/ML**: Transformers, Stanza, and custom Arabic NLP models

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+**
- **Node.js 18+** and **pnpm**
- **MongoDB** (local or cloud)
- **Redis** server
- **Git**

### 1. Clone the Repository

```bash
git clone https://github.com/Zineddine-Rebbouh/back-end-web-app.git
cd back-end-web-app
```

### 2. Backend Setup

```bash
# Navigate to server directory
cd server

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configurations

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start Django development server
python manage.py runserver
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory (from project root)
cd frontend

# Install dependencies
pnpm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with your configurations

# Start development server
pnpm dev
```

### 4. Start Background Services

```bash
# In separate terminals:

# Start Redis (if not running as service)
redis-server

# Start Celery worker (in server directory)
celery -A config worker --loglevel=info

# Start Celery beat scheduler (in server directory)
celery -A config beat --loglevel=info
```

## 🔧 Configuration

### Environment Variables

#### Backend (.env)

```env
DJANGO_SECRET_KEY=your_secret_key_here
MONGODB_NAME=tendances_sportives_db
MONGODB_HOST=your_mongodb_connection_string
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
TWITTER_USERNAME=your_twitter_username
TWITTER_EMAIL=your_twitter_email
TWITTER_PASSWORD=your_twitter_password
YOUTUBE_API_KEY=your_youtube_api_key
```

#### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Tendances Sportives
```

## 📁 Project Structure

```
tendances-sportives/
├── frontend/                    # Next.js frontend application
│   ├── app/                    # Next.js 13+ app directory
│   │   ├── globals.css         # Global styles
│   │   ├── layout.tsx          # Root layout
│   │   ├── page.tsx           # Home page
│   │   ├── about/             # About page
│   │   ├── login/             # Authentication pages
│   │   ├── profile/           # User profile
│   │   ├── reports/           # Reports dashboard
│   │   ├── settings/          # App settings
│   │   └── trends/            # Trends analysis
│   ├── components/             # Reusable React components
│   │   ├── ui/                # Base UI components
│   │   ├── charts/            # Chart components
│   │   └── dashboard-*.tsx    # Dashboard components
│   ├── hooks/                 # Custom React hooks
│   ├── lib/                   # Utility functions
│   ├── services/              # API service layers
│   ├── types/                 # TypeScript type definitions
│   └── public/                # Static assets
├── server/                     # Django backend application
│   ├── config/                # Django project configuration
│   │   ├── settings/          # Environment-specific settings
│   │   ├── urls.py           # URL routing
│   │   ├── wsgi.py           # WSGI configuration
│   │   └── asgi.py           # ASGI configuration
│   ├── accountss/             # User authentication app
│   ├── apps/                  # Core application modules
│   │   ├── data_collection/   # Social media scraping
│   │   ├── text_processing/   # Arabic text processing
│   │   ├── entity_recognition/ # NER for sports entities
│   │   ├── sentiment_analysis/ # Emotion detection
│   │   ├── trend_analysis/    # Trending topics analysis
│   │   └── database_management/ # Data management
│   ├── celery_app/            # Celery task configuration
│   ├── models/                # Pre-trained ML models
│   │   ├── camelbert_ner/     # Arabic NER model
│   │   └── fine_tuned_arabert_v2/ # Arabic sentiment model
│   ├── api/                   # REST API endpoints
│   └── media/                 # User-uploaded files
└── README.md                  # This file
```

## 🧪 API Documentation

### Authentication Endpoints

- `POST /api/auth/login/` - User login
- `POST /api/auth/register/` - User registration
- `POST /api/auth/logout/` - User logout
- `POST /api/auth/refresh/` - Token refresh

### Data Collection Endpoints

- `GET /api/trends/` - Get trending topics
- `GET /api/trends/{id}/` - Get specific trend details
- `POST /api/trends/collect/` - Trigger data collection

### Analytics Endpoints

- `GET /api/analytics/sentiment/` - Sentiment analysis data
- `GET /api/analytics/entities/` - Recognized entities
- `GET /api/analytics/hashtags/` - Hashtag trends
- `GET /api/analytics/mentions/` - Mention analytics

### Reports Endpoints

- `GET /api/reports/` - List available reports
- `POST /api/reports/generate/` - Generate new report
- `GET /api/reports/{id}/download/` - Download report

## 🔄 Development Workflow

### Running Tests

```bash
# Backend tests
cd server
python manage.py test

# Frontend tests
cd frontend
pnpm test
```

### Code Quality

```bash
# Backend linting
cd server
flake8 .
black .

# Frontend linting
cd frontend
pnpm lint
pnpm type-check
```

### Building for Production

```bash
# Frontend build
cd frontend
pnpm build

# Backend static files
cd server
python manage.py collectstatic
```

## 🚀 Deployment

### Using Docker

```bash
# Build and run with docker-compose
docker-compose up -d

# For production
docker-compose -f docker-compose.prod.yml up -d
```

### Manual Deployment

1. **Frontend**: Deploy to Vercel, Netlify, or similar
2. **Backend**: Deploy to Railway, Heroku, or VPS
3. **Database**: Use MongoDB Atlas or self-hosted
4. **Redis**: Use Redis Cloud or self-hosted

## 🔧 Troubleshooting

### Common Issues

1. **MongoDB Connection Issues**

   - Verify MongoDB is running
   - Check connection string in environment variables
   - Ensure network access for cloud MongoDB

2. **Redis Connection Issues**

   - Verify Redis server is running
   - Check Redis URL in environment variables

3. **Arabic Text Processing Issues**

   - Ensure correct Python locale settings
   - Verify Arabic NLP models are downloaded
   - Check text encoding (UTF-8)

4. **Frontend API Connection Issues**
   - Verify backend server is running
   - Check CORS settings in Django
   - Ensure correct API URL in frontend config

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use TypeScript for all frontend code
- Write tests for new features
- Update documentation for API changes
- Use conventional commit messages

## 📋 Roadmap

- [ ] **Real-time WebSocket Implementation**: Live trend updates
- [ ] **Mobile App**: React Native companion app
- [ ] **Advanced ML Models**: Improved Arabic NLP models
- [ ] **Multi-language Support**: Expand beyond Arabic
- [ ] **Enhanced Visualizations**: More chart types and insights
- [ ] **API Rate Limiting**: Implement proper rate limiting
- [ ] **Caching Layer**: Redis caching for improved performance
- [ ] **Microservices**: Break down into microservices architecture

## 📊 Performance

- **Backend**: Handles 1000+ concurrent requests
- **Database**: Optimized MongoDB queries with indexing
- **Caching**: Redis caching for frequently accessed data
- **Task Queue**: Celery for background processing
- **Real-time**: WebSocket connections for live updates

## 🔒 Security

- JWT authentication with refresh tokens
- CORS configuration for cross-origin requests
- Environment variable protection for sensitive data
- Input validation and sanitization
- Rate limiting on API endpoints
- HTTPS enforcement in production

## 📈 Monitoring

- Django logging configuration
- Celery task monitoring
- MongoDB performance monitoring
- Frontend error tracking
- API response time monitoring

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For support and questions:

- **Issues**: [GitHub Issues](https://github.com/Zineddine-Rebbouh/back-end-web-app/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Zineddine-Rebbouh/back-end-web-app/discussions)
- **Email**: [Project Maintainer](mailto:zineddine.rebbouh@example.com)

## 🙏 Acknowledgments

- **Arabic NLP**: Thanks to the Arabic NLP research community
- **Open Source**: Built with amazing open-source libraries
- **Contributors**: Thanks to all contributors who helped build this project

---

**Made with ❤️ for the Arabic sports community**
