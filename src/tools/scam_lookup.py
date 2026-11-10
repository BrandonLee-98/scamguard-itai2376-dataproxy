import os
import json
import requests

def lookup_scam_database(query: str) -> dict:
    """
    Queries live Tavily Web Search API targeting FTC/AARP threat intelligence data,
    with automatic try-except error handling falling back to local JSON scam database.
    """
    try:
        api_key = os.getenv("SEARCH_API_KEY")
        if not api_key or api_key == "placeholder":
            raise ValueError("Search API key not configured or is a placeholder.")
            
        # Direct Tavily API request targeting FTC/AARP advisories
        response = requests.post(
            "https://api.tavily.com/search",
            json={"api_key": api_key, "query": f"FTC AARP scam alert {query}", "max_results": 2}
        )
        
        if response.status_code != 200:
            raise Exception(f"API returned status code {response.status_code}")
            
        results = response.json().get("results", [])
        formatted_data = "\n".join([r.get("content", "") for r in results])
        
        return {
            "status": "success",
            "source": "live_api",
            "data": formatted_data or "No detailed results found online."
        }
    except Exception as e:
        # Fallback: Load from local JSON backup database (src/tools/scam_database.json)
        try:
            with open("src/tools/scam_database.json", "r") as f:
                db = json.load(f)
                scams = db.get("scams", [])
        except Exception:
            scams = []
            
        query_lower = query.lower()
        matched_description = "General scam pattern: Verify independently through official channels."
        
        for scam in scams:
            if any(kw in query_lower for kw in scam.get("keywords", [])) or scam.get("category", "").lower() in query_lower:
                matched_description = f"[{scam['category']}] {scam['description']} Red Flags: {', '.join(scam['red_flags'])}. Safe Action: {scam['safe_action']}"
                break
                
        return {
            "status": "fallback",
            "error": str(e),
            "data": matched_description
        }
