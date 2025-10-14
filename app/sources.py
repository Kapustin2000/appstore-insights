"""
Data sources module for fetching app information and reviews from iTunes API.
"""
import time
import requests
from typing import Dict, List, Any


def fetch_app_info(app_id: str, country: str) -> Dict[str, Any]:
    """
    Fetch app information from iTunes Lookup API.
    
    Args:
        app_id: Apple App Store app ID
        country: Country code (2-letter)
        
    Returns:
        Dictionary with status and app details
    """
    try:
        r = requests.get(
            "https://itunes.apple.com/lookup",
            params={"id": app_id, "country": country},
            headers={"User-Agent": "storelytics/1.0"},
            timeout=15
        )
        r.raise_for_status()
        js = r.json()
        
        if js.get("resultCount", 0) == 0:
            return {"status": "not_found", "details": None}
            
        res = js["results"][0]
        return {
            "status": "success",
            "details": {
                "appId": res.get("trackId"),
                "name": res.get("trackName"),
                "bundleId": res.get("bundleId"),
                "genres": res.get("genres", []),
                "genreIds": res.get("genreIds", []),
                "rating": res.get("averageUserRating"),
                "ratingCount": res.get("userRatingCount"),
                "price": res.get("price", 0.0),
                "locales": res.get("languageCodesISO2A", []),
                "releaseDate": res.get("releaseDate"),
                "lastUpdate": res.get("currentVersionReleaseDate"),
                "seller": res.get("sellerName"),
                "url": res.get("trackViewUrl")
            }
        }
    except requests.RequestException as e:
        return {"status": "error", "error": str(e)}


def fetch_reviews_paged(app_id: str, country: str, limit: int = 300, delay: float = 1.0) -> Dict[str, Any]:
    """
    Fetch app reviews with pagination from iTunes RSS API.
    
    Args:
        app_id: Apple App Store app ID
        country: Country code (2-letter)
        limit: Maximum number of reviews to fetch
        delay: Delay between requests in seconds
        
    Returns:
        Dictionary with status, items, and metadata
    """
    headers = {"User-Agent": "storelytics/1.0"}
    seen, items, page = set(), [], 1
    pages_fetched = 0
    
    while len(items) < limit:
        url = f"https://itunes.apple.com/{country}/rss/customerreviews/id={app_id}/sortBy=mostRecent/page={page}/json"
        
        try:
            r = requests.get(url, headers=headers, timeout=15)
            if r.status_code != 200:
                break
                
            js = r.json()
            feed = js.get("feed", {}) if isinstance(js.get("feed"), dict) else {}
            entries = feed.get("entry", [])
            
            # Handle case where entries might be a single dict instead of list
            if isinstance(entries, dict):
                entries = [entries]
                
            added = 0
            for e in entries:
                if not isinstance(e, dict) or "im:rating" not in e:
                    continue
                    
                rid = (e.get("id", {}) or {}).get("label")
                if rid and rid not in seen:
                    seen.add(rid)
                    items.append({
                        "reviewId": rid,
                        "rating": int((e.get("im:rating", {}) or {}).get("label", "0")),
                        "title": (e.get("title", {}) or {}).get("label"),
                        "content": (e.get("content", {}) or {}).get("label"),
                        "updated": (e.get("updated", {}) or {}).get("label"),
                        "version": (e.get("im:version", {}) or {}).get("label"),
                        "author": ((e.get("author", {}) or {}).get("name", {}) or {}).get("label"),
                    })
                    added += 1
                    if len(items) >= limit:
                        break
                        
            pages_fetched += 1
            
            # Check for next page
            links = feed.get("link", [])
            if isinstance(links, dict):
                links = [links]
                
            has_next = any(
                (l.get("attributes", {}) or {}).get("rel") == "next" 
                for l in links if isinstance(l, dict)
            )
            
            if not has_next or added == 0:
                break
                
            page += 1
            if delay:
                time.sleep(delay)
                
        except requests.RequestException as e:
            return {"status": "error", "error": str(e)}
    
    return {
        "status": "success",
        "items": items,
        "meta": {"pages_fetched": pages_fetched}
    }
