# Apple Store Parser API

🚀 **FastAPI-based API for comprehensive Apple App Store data collection and preprocessing**

A professional, scalable API for fetching app information, collecting reviews, and performing text preprocessing with advanced analytics capabilities.

## ✨ Features

- 🍎 **App Information**: Fetch detailed app metadata from iTunes API
- 📝 **Review Collection**: Retrieve and paginate app reviews with configurable limits
- 🧹 **Text Preprocessing**: Clean, normalize, and tokenize review text
- 📊 **Analytics**: Generate summary statistics and language distribution
- 🎭 **Sentiment Analysis**: Advanced sentiment analysis using VADER with hybrid scoring
- 🔍 **Insights Generation**: Extract negative phrases and generate actionable insights
- 🏗️ **Scalable Architecture**: Clean, modular codebase with separation of concerns
- 📚 **Auto-generated Docs**: Interactive API documentation with Swagger/ReDoc
- 🔧 **Configurable**: Flexible parameters for data collection and processing
- 🧪 **Well-tested**: Comprehensive test suite with mocking and validation
- 📦 **Production-ready**: Professional project structure with proper error handling

## 🏗️ Project Structure

```
apple-store-parser/
├── app/                          # Main application
│   ├── __init__.py
│   ├── main.py                   # FastAPI application entry point
│   ├── api/                      # API layer
│   │   ├── __init__.py
│   │   └── routes.py            # All API endpoints
│   ├── core/                     # Core configuration
│   │   ├── __init__.py
│   │   ├── config.py            # Application settings
│   │   └── exceptions.py        # Custom exceptions
│   ├── services/                 # Business logic layer
│   │   ├── __init__.py
│   │   ├── app_service.py       # iTunes API integration
│   │   ├── review_service.py    # Review processing service
│   │   ├── text_service.py      # Text preprocessing service
│   │   ├── sentiment_service.py # Sentiment analysis service
│   │   └── insights_service.py  # Insights generation service
│   ├── models/                   # Data models
│   │   ├── __init__.py
│   │   ├── requests.py          # Request models
│   │   ├── responses.py         # Response models
│   │   ├── schemas.py           # Data schemas
│   │   └── analyze.py           # Analysis models
│   └── utils/                    # Utilities
│       ├── __init__.py
│       ├── validators.py        # Input validation
│       └── helpers.py           # Helper functions
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── test_api/                # API tests
│   ├── test_services/           # Service tests
│   └── test_utils/              # Utility tests
├── data/                         # Data storage (gitignored)
├── docs/                         # Documentation
├── scripts/                      # Utility scripts
├── pyproject.toml               # Project configuration
├── README.md                    # This file
└── .gitignore                   # Git ignore rules
```

## 🚀 Quick Start

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd apple-store-parser
```

2. **Install dependencies:**
```bash
pip install -e .
```

3. **For development:**
```bash
pip install -e ".[dev]"
```

### Running the API

**Start the server:**
```bash
python -m app.main
```

**Or using uvicorn directly:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Access the API:**
- API: `http://localhost:8000`
- Interactive docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 📚 API Documentation

### 🎯 Main Endpoints

#### 1. Collect and Preprocess

**Comprehensive data collection and preprocessing in one call:**

```http
POST /app/collect-and-preprocess
```

#### 2. Analyze Reviews 🆕

**Advanced sentiment analysis and insights generation:**

```http
POST /app/analyze
```

**Collect and Preprocess Request Body:**
```json
{
  "app_id": "1459969523",
  "country": "us",
  "review_limit": 300,
  "keep_emojis": false,
  "lowercase": true,
  "min_tokens": 3,
  "save_raw": false
}
```

**Example Response (Nebula: Horoscope & Astrology):**
```json
{
  "status": "ok",
  "meta": {
    "app_id": "1459969523",
    "country": "us",
    "collected_reviews": 50,
    "pages_fetched": 1,
    "processing_time_ms": 1398
  },
  "app_info": {
    "appId": 1459969523,
    "name": "Nebula: Horoscope & Astrology",
    "bundleId": "com.genesismedia.Nebula.Horoscope",
    "genres": ["Lifestyle", "Reference"],
    "rating": 4.59807,
    "ratingCount": 162790,
    "price": 0.0,
    "seller": "OBRIO LIMITED"
  },
  "summary": {
    "mean_star": 4.18,
    "by_star": {"5": 35, "4": 5, "3": 2, "1": 8},
    "lang_distribution": {"en": 1.0, "other": 0.0}
  },
  "data": {
    "raw_reviews": [
      {
        "reviewId": "1",
        "rating": 5,
        "title": "Informative journey",
        "content": "Each chat feels like part of a personal journey. The guidance is helpful and gives me peace every time."
      }
    ],
    "clean_reviews": [
      {
        "reviewId": "1",
        "clean_text": "informative journey each chat feels like part of personal journey guidance helpful gives peace every time",
        "tokens": ["informative", "journey", "each", "chat", "feels", "like", "part", "personal", "journey", "guidance", "helpful", "gives", "peace", "every", "time"],
        "token_count": 15
      }
    ]
  }
}
```

**Analyze Endpoint Request Body:**
```json
{
  "app_id": "1459969523",
  "country": "us",
  "review_limit": 300,
  "use_cached_collect": true,
  "sentiment_model": "vader",
  "ngram_range": [1, 2],
  "min_df": 2,
  "top_k_phrases": 20,
  "weights": {"text": 0.6, "stars": 0.4},
  "recency_cutoffs_days": [90, 365],
  "reviews_override": null
}
```

**Analyze Endpoint Response:**
```json
{
  "status": "ok",
  "meta": {
    "app_id": "1459969523",
    "country": "us",
    "analyzed": 100,
    "processing_time_ms": 2468
  },
  "sentiment_overview": {
    "pos": 0.79,
    "neu": 0.07,
    "neg": 0.14,
    "mean_star": 4.09
  },
  "top_negative_phrases": [
    {
      "phrase": "app",
      "score": 3.768,
      "count": 11,
      "share_neg": 0.557
    },
    {
      "phrase": "scam",
      "score": 4.083,
      "count": 15,
      "share_neg": 0.246
    },
    {
      "phrase": "subscription",
      "score": 3.267,
      "count": 16,
      "share_neg": 0.262
    }
  ],
  "insights": [
    {
      "priority": 1,
      "area": "General",
      "issue": "app",
      "why": "56% negative sentiment; strong negative sentiment; recent reviews",
      "action": "Investigate the issue, gather additional information",
      "impact": "medium"
    },
    {
      "priority": 2,
      "area": "General",
      "issue": "scam",
      "why": "25% negative sentiment; strong negative sentiment; recent reviews",
      "action": "Investigate the issue, gather additional information",
      "impact": "low"
    },
    {
      "priority": 3,
      "area": "Pricing/IAP",
      "issue": "subscription",
      "why": "26% negative sentiment; strong negative sentiment; recent reviews",
      "action": "Open basic features, add free trial, transparent pricing",
      "impact": "low"
    }
  ],
  "debug": {
    "model": "vader",
    "thresholds": {"neg": -0.2, "pos": 0.2},
    "low_sample": false,
    "no_negative_signal": false
  }
}
```

**Parameters:**

**Collect and Preprocess:**
- `app_id` (required): Apple App Store app ID
  - Supports formats: `1459969523`, `id1459969523`, `ID1459969523`
  - Automatically cleaned and validated
- `country` (optional): Country code (default: `us`)
  - Must be 2-letter ISO code (e.g., `us`, `gb`, `de`)
- `review_limit` (optional): Max reviews to collect (default: `300`, range: 1-2000)
- `keep_emojis` (optional): Keep emojis in cleaned text (default: `false`)
- `lowercase` (optional): Convert text to lowercase (default: `true`)
- `min_tokens` (optional): Min tokens for review inclusion (default: `3`)
- `save_raw` (optional): Save raw data to file (default: `false`)

**Analyze Endpoint:**
- `app_id` (required): Apple App Store app ID
- `country` (optional): Country code (default: `us`)
- `review_limit` (optional): Max reviews to analyze (default: `300`, max: `2000`)
- `use_cached_collect` (optional): Use cached collection (default: `true`)
- `sentiment_model` (optional): Sentiment model (default: `vader`)
- `ngram_range` (optional): N-gram range for phrases (default: `[1, 2]`)
- `min_df` (optional): Min document frequency (default: `2`)
- `top_k_phrases` (optional): Number of top phrases (default: `20`)
- `weights` (optional): Text vs stars weights (default: `{"text": 0.6, "stars": 0.4}`)
- `recency_cutoffs_days` (optional): Recency cutoffs (default: `[90, 365]`)
- `reviews_override` (optional): Custom reviews data (default: `null`)

**Example Usage:**

**Collect and Preprocess:**
```bash
curl -X POST "http://localhost:8000/app/collect-and-preprocess" \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "1459969523",
    "country": "us",
    "review_limit": 100,
    "keep_emojis": false,
    "lowercase": true,
    "min_tokens": 3,
    "save_raw": false
  }'
```

**Analyze Reviews:**
```bash
curl -X POST "http://localhost:8000/app/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "1459969523",
    "country": "us",
    "review_limit": 200,
    "sentiment_model": "vader",
    "top_k_phrases": 10,
    "weights": {"text": 0.7, "stars": 0.3}
  }'
```

**Example: Analyzing Nebula: Horoscope & Astrology**
```bash
# Get app information
curl "http://localhost:8000/app/1459969523/info?country=us"

# Collect and preprocess reviews
curl -X POST "http://localhost:8000/app/collect-and-preprocess" \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "1459969523",
    "country": "us",
    "review_limit": 300
  }'

# Analyze sentiment and generate insights
curl -X POST "http://localhost:8000/app/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "1459969523",
    "country": "us",
    "review_limit": 300,
    "sentiment_model": "vader",
    "top_k_phrases": 15
  }'
```

**Response:**
```json
{
  "status": "ok",
  "meta": {
    "app_id": "1459969523",
    "country": "us",
    "collected_reviews": 95,
    "pages_fetched": 1,
    "processing_time_ms": 1247
  },
  "app_info": {
    "appId": 1459969523,
    "name": "Lucidly",
    "bundleId": "com.omarpaniagua.lucidly",
    "genres": ["Lifestyle", "Health & Fitness"],
    "rating": 3.28,
    "ratingCount": 18,
    "price": 0.0,
    "locales": ["EN"],
    "releaseDate": "2021-05-22T07:00:00Z",
    "lastUpdate": "2025-03-03T17:21:32Z",
    "url": "https://apps.apple.com/us/app/lucidly/id1459969523"
  },
  "summary": {
    "mean_star": 3.2,
    "by_star": {"5": 12, "4": 8, "3": 15, "2": 25, "1": 35},
    "lang_distribution": {"en": 0.89, "other": 0.11}
  },
  "data": {
    "raw_reviews": [/* first 50 raw reviews */],
    "clean_reviews": [/* first 50 cleaned reviews with tokens */]
  },
  "analysis_stub": {
    "sentiment": null,
    "topics": null,
    "insights": null
  }
}
```

### 📱 Additional Endpoints

#### Get App Information
```http
GET /app/{app_id}/info?country=us
```

#### Get App Reviews (Fixed 100 reviews)
```http
GET /app/{app_id}/reviews?country=us
```

#### Health Check
```http
GET /app/health
```

#### API Information
```http
GET /app/
```

## 🔧 Configuration

The application uses a centralized configuration system in `app/core/config.py`:

```python
class Settings(BaseModel):
    # API settings
    app_name: str = "Apple Store Parser API"
    app_version: str = "0.1.0"
    debug: bool = False
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    # iTunes API settings
    itunes_timeout: int = 15
    itunes_user_agent: str = "storelytics/1.0"
    
    # Review collection settings
    default_review_limit: int = 300
    max_review_limit: int = 2000
    default_delay: float = 1.0
    
    # Text processing settings
    default_min_tokens: int = 3
    default_keep_emojis: bool = False
    default_lowercase: bool = True
    
    # Data storage
    data_dir: str = "data"
    
    model_config = ConfigDict(env_file=".env", case_sensitive=False, extra="ignore")
```

## 🧪 Testing

**Run all tests:**
```bash
pytest
```

**Run with verbose output:**
```bash
pytest -v
```

**Run specific test categories:**
```bash
# API tests
pytest tests/test_api/

# Service tests
pytest tests/test_services/

# Utility tests
pytest tests/test_utils/
```

## 🛠️ Development

### Code Quality

**Formatting:**
```bash
black app/ tests/
isort app/ tests/
```

**Linting:**
```bash
flake8 app/ tests/
mypy app/
```

**Pre-commit hooks:**
```bash
pre-commit install
pre-commit run --all-files
```

### Adding New Features

1. **New API Endpoint:**
   - Add route in `app/api/routes.py`
   - Create request/response models in `app/models/`
   - Add business logic in `app/services/`

2. **New Service:**
   - Create service class in `app/services/`
   - Add corresponding tests in `tests/test_services/`

3. **New Utility:**
   - Add function in `app/utils/`
   - Add tests in `tests/test_utils/`

## 📊 Data Processing Pipeline

The API implements a sophisticated data processing pipeline:

1. **Input Validation**: Clean and validate app IDs and parameters
2. **Data Collection**: Fetch app metadata and paginate through reviews
3. **Text Preprocessing**: 
   - HTML entity decoding
   - Unicode normalization
   - URL/email/mention removal
   - Emoji handling (optional)
   - Case normalization
   - Whitespace cleanup
4. **Tokenization**: Extract meaningful tokens using regex patterns
5. **Filtering**: Remove reviews below minimum token threshold
6. **Analytics**: Calculate summary statistics and language distribution
7. **Response Assembly**: Combine raw and processed data with metadata

## 🚨 Error Handling

The API provides comprehensive error handling with appropriate HTTP status codes:

- **400 Bad Request**: Invalid input parameters
- **404 Not Found**: App or reviews not found
- **502 Bad Gateway**: iTunes API errors
- **503 Service Unavailable**: External service issues
- **500 Internal Server Error**: Unexpected server errors

## 📈 Performance Features

- **Pagination**: Efficient review collection with configurable limits
- **Rate Limiting**: Built-in delays to respect API limits
- **Response Limiting**: Automatic truncation of large responses
- **Caching Ready**: Architecture supports easy caching integration
- **Async Support**: FastAPI's async capabilities for high concurrency

## 🔒 Security Features

- **Input Validation**: Comprehensive parameter validation
- **Error Sanitization**: Safe error messages without sensitive data
- **Rate Limiting**: Built-in request throttling
- **User-Agent**: Proper identification for API requests

## 📦 Dependencies

**Core Dependencies:**
- `fastapi>=0.104.0` - Web framework
- `uvicorn[standard]>=0.24.0` - ASGI server
- `requests>=2.25.0` - HTTP client
- `pydantic>=2.0.0` - Data validation
- `beautifulsoup4>=4.12.0` - HTML parsing
- `lxml>=4.9.0` - XML/HTML parser
- `emoji>=2.8.0` - Emoji handling
- `ftfy>=6.1.0` - Text fixing

**Development Dependencies:**
- `pytest>=7.0` - Testing framework
- `pytest-asyncio>=0.21.0` - Async testing
- `black>=23.0` - Code formatting
- `flake8>=6.0` - Linting
- `mypy>=1.0` - Type checking
- `isort>=5.0` - Import sorting

## 🆕 New Features: Sentiment Analysis & Insights

### Sentiment Analysis
- **VADER Integration**: Advanced sentiment analysis using NLTK's VADER
- **Hybrid Scoring**: Combines text sentiment with star ratings for better accuracy
- **Configurable Thresholds**: Customizable positive/negative classification
- **Multi-language Support**: Works with English and other languages

### Insights Generation
- **Negative Phrase Extraction**: TF-IDF based phrase identification from negative reviews
- **Actionable Recommendations**: Prioritized insights with specific actions
- **Area Classification**: Automatic categorization (Monetization, UX, Quality, etc.)
- **Recency Weighting**: Time-based importance scoring for insights
- **Impact Assessment**: High/medium/low impact classification

### Example Analysis Output (Nebula: Horoscope & Astrology)
```json
{
  "sentiment_overview": {
    "pos": 0.79,
    "neu": 0.07, 
    "neg": 0.14,
    "mean_star": 4.09
  },
  "top_negative_phrases": [
    {
      "phrase": "app",
      "score": 3.768,
      "count": 11,
      "share_neg": 0.557
    },
    {
      "phrase": "scam",
      "score": 4.083,
      "count": 15,
      "share_neg": 0.246
    }
  ],
  "insights": [
    {
      "priority": 1,
      "area": "General",
      "issue": "app",
      "action": "Investigate the issue, gather additional information",
      "impact": "medium"
    },
    {
      "priority": 2,
      "area": "Pricing/IAP",
      "issue": "subscription",
      "action": "Open basic features, add free trial, transparent pricing",
      "impact": "low"
    }
  ]
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`pytest`)
6. Format your code (`black app/ && isort app/`)
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Mykhailo Kapustin** - [kapustinomm@gmail.com](mailto:kapustinomm@gmail.com)

## 🙏 Acknowledgments

- Apple iTunes API for providing app data
- FastAPI team for the excellent web framework
- All contributors and users of this project

---

**⭐ If you find this project useful, please give it a star!**