import os
import requests

# Local backup database for tool failure fallback
LOCAL_SCAM_BACKEND = {
    "tech support": "Fake tech support pop-ups claim your computer has a virus and prompt you to call a number for paid support.",
    "grandchild": "Imposter scams involve someone posing as a family member in an urgent emergency demanding immediate wire transfers.",
    "irs": "Government impersonation scams threaten arrest or penalties unless paid immediately via gift cards or crypto."
}

def lookup_scam_database(query: str) -> dict:
    try:
        api_key = os.getenv("SEARCH_API_KEY")
        if not api_key or api_key == "placeholder":
            raise ValueError("Search API key not configured or is a placeholder.")
            
        # Direct Tavily API request
        response = requests.post(
            "https://api.tavily.com/search",
            json={"api_key": api_key, "query": query, "max_results": 2}
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
        # Fallback to local backup dictionary to prevent crashes
        query_lower = query.lower()
        matched_fallback = None
        for key, description in LOCAL_SCAM_BACKEND.items():
            if key in query_lower:
                matched_fallback = description
                break
                
        return {
            "status": "fallback",
            "error": str(e),
            "data": matched_fallback or "General scam pattern: Verify independently through official channels."
        }
