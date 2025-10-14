# Apple Store Parser API

FastAPI-based API for fetching Apple App Store app information and reviews.

## Features

- 🍎 Fetch app information from Apple App Store
- 📝 Retrieve app reviews with ratings and content
- 🚀 Built with FastAPI for high performance
- 📚 Auto-generated API documentation
- 🔧 Configurable request limits and delays

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd apple-store-parser
```

2. Install dependencies:
```bash
pip install -e .
```

3. For development:
```bash
pip install -e ".[dev]"
```

## Usage

### Start the server

```bash
python -m app.main
```

Or using uvicorn directly:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### API Documentation

- Interactive docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Endpoints

#### Get App Information
```http
GET /app/{app_id}/info?country=us
```

**Parameters:**
- `app_id` (path): Apple App Store app ID
- `country` (query): Country code (default: us)

**Example:**
```bash
curl "http://localhost:8000/app/544007664/info?country=us"
```

#### Get App Reviews
```http
GET /app/{app_id}/reviews?country=us
```

**Parameters:**
- `app_id` (path): Apple App Store app ID
- `country` (query): Country code (default: us)

**Note:** Returns up to 100 reviews with a fixed 1-second delay between requests.

**Example:**
```bash
curl "http://localhost:8000/app/544007664/reviews?country=us"
```

#### Health Check
```http
GET /health
```

## Development

### Code Formatting
```bash
black app/
isort app/
```

### Linting
```bash
flake8 app/
mypy app/
```

### Testing
```bash
pytest
```

## Project Structure

```
apple-store-parser/
├── app/
│   ├── __init__.py
│   └── main.py          # FastAPI application
├── pyproject.toml       # Project configuration
└── README.md           # This file
```

## API Response Examples

### App Information Response
```json
{
  "status": "success",
  "details": {
    "resultCount": 1,
    "results": [
      {
        "trackId": 1566419183,
        "trackName": "Lucidly",
        "bundleId": "com.omarpaniagua.lucidly",
        "version": "1.15.1",
        "price": 0.0,
        "formattedPrice": "Free",
        "description": "Lucidly collects health readings while you are sleeping via the watch...",
        "averageUserRating": 3.27778,
        "userRatingCount": 18,
        "averageUserRatingForCurrentVersion": 3.27778,
        "userRatingCountForCurrentVersion": 18,
        "releaseDate": "2021-05-22T07:00:00Z",
        "currentVersionReleaseDate": "2025-03-03T17:21:32Z",
        "releaseNotes": "- updated setup with configuration video\n- minor updates to UI",
        "artistName": "5Path LLC",
        "artistId": 1544734236,
        "sellerName": "5Path LLC",
        "primaryGenreName": "Lifestyle",
        "genres": ["Lifestyle", "Health & Fitness"],
        "contentAdvisoryRating": "9+",
        "minimumOsVersion": "13.4",
        "fileSizeBytes": "115293184",
        "languageCodesISO2A": ["EN"],
        "screenshotUrls": [
          "https://is1-ssl.mzstatic.com/image/thumb/PurpleSource126/v4/60/ad/16/60ad1697-13ab-5784-80af-e7f6bdb2a0e9/90d38102-77df-4016-840b-c1561d641f2e_Apple_iPhone_8_Plus_Screenshot_0.png/392x696bb.png"
        ],
        "ipadScreenshotUrls": [
          "https://is1-ssl.mzstatic.com/image/thumb/PurpleSource126/v4/27/0c/20/270c203f-bea8-8826-a4ec-858e79b909a4/a5b29f61-1e38-48da-9891-fea580522081_Apple_iPad_Pro_13_Inch_Screenshot_0.png/576x768bb.png"
        ],
        "artworkUrl60": "https://is1-ssl.mzstatic.com/image/thumb/Purple211/v4/e7/ef/63/e7ef635b-f508-878c-ef9b-3ec5659f3b71/AppIcon-0-0-1x_U007emarketing-0-7-0-sRGB-85-220.png/60x60bb.jpg",
        "artworkUrl100": "https://is1-ssl.mzstatic.com/image/thumb/Purple211/v4/e7/ef/63/e7ef635b-f508-878c-ef9b-3ec5659f3b71/AppIcon-0-0-1x_U007emarketing-0-7-0-sRGB-85-220.png/100x100bb.jpg",
        "artworkUrl512": "https://is1-ssl.mzstatic.com/image/thumb/Purple211/v4/e7/ef/63/e7ef635b-f508-878c-ef9b-3ec5659f3b71/AppIcon-0-0-1x_U007emarketing-0-7-0-sRGB-85-220.png/512x512bb.jpg",
        "trackViewUrl": "https://apps.apple.com/us/app/lucidly/id1566419183?uo=4",
        "artistViewUrl": "https://apps.apple.com/us/developer/5path-llc/id1544734236?uo=4",
        "sellerUrl": "https://lucidlyapp.com/"
      }
    ]
  }
}
```

**Response Schema:**
- `status`: Response status (string)
- `details`: App information container
  - `resultCount`: Number of results returned (integer)
  - `results`: Array of app information objects
    - `trackId`: Unique app identifier (integer)
    - `trackName`: App name (string)
    - `bundleId`: App bundle identifier (string)
    - `version`: Current app version (string)
    - `price`: App price (number)
    - `formattedPrice`: Formatted price string (string)
    - `description`: App description (string)
    - `averageUserRating`: Average user rating (number)
    - `userRatingCount`: Total number of user ratings (integer)
    - `artistName`: Developer name (string)
    - `primaryGenreName`: Primary genre (string)
    - `genres`: List of genres (array of strings)
    - `contentAdvisoryRating`: Content advisory rating (string)
    - `minimumOsVersion`: Minimum required iOS version (string)
    - `screenshotUrls`: iPhone screenshot URLs (array of strings)
    - `ipadScreenshotUrls`: iPad screenshot URLs (array of strings)
    - `artworkUrl60/100/512`: App icon URLs (strings)
    - `trackViewUrl`: App Store URL (string)
    - `artistViewUrl`: Developer page URL (string)
    - `sellerUrl`: Seller website URL (string, optional)

### App Reviews Response
```json
{
  "status": "success",
  "count": 10,
  "items": [
    {
      "reviewId": "12663656997",
      "rating": 1,
      "title": "Scam",
      "content": "No rem alarm or sleep date this app is not work or it is way to buggy it had one job but did not do it please don't spend money on this app",
      "updated": "2025-05-16T13:34:52-07:00",
      "version": "1.15.1",
      "author": "vtcyctcfcgctu"
    },
    {
      "reviewId": "12302368049",
      "rating": 3,
      "title": "Waiting for update",
      "content": "I was so elated when I saw that there's finally an app that can wake you up during REM sleep...",
      "updated": "2025-02-12T06:52:13-07:00",
      "version": "1.15.0",
      "author": "DrMEEH"
    }
  ]
}
```

**Response Schema:**
- `status`: Response status (string)
- `count`: Number of reviews returned (integer, 0+)
- `items`: Array of review objects
  - `reviewId`: Unique review identifier (string)
  - `rating`: Star rating from 1-5 (integer)
  - `title`: Review title (string, optional)
  - `content`: Review content/body (string, optional)
  - `updated`: Last update timestamp (string, optional)
  - `version`: App version when review was written (string, optional)
  - `author`: Review author name (string, optional)

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Author

Mykhailo Kapustin - kapustinomm@gmail.com
