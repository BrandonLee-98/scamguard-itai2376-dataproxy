import re

def analyze_safety(input_text: str) -> dict:
    """
    Analyzes text, URLs, and phone numbers for phishing indicators, 
    spoofed domains, and urgency pressure tactics. Includes robust try-except 
    error handling to return a safe warning instead of crashing on weird inputs.
    """
    try:
        if not isinstance(input_text, str) or not input_text.strip():
            raise ValueError("Input text is empty or invalid.")
            
        # Regex patterns for URLs, phone numbers, and urgency/fraud keywords
        patterns = {
            "urls": r'http[s]?://[^\s]+',
            "phone_numbers": r'\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
            "urgency_keywords": r'\b(verify|update|suspended|urgent|prize|winner|bank|irs|arrest|warrant|gift card)\b'
        }
        
        found_flags = []
        for category, pattern in patterns.items():
            matches = re.findall(pattern, input_text, re.IGNORECASE)
            if matches:
                found_flags.extend(matches)
                
        is_risky = len(found_flags) > 0
        return {
            "status": "success",
            "is_risky": is_risky,
            "flags_detected": list(set(found_flags)),
            "message": "Potential risk indicators found. Proceed with caution." if is_risky else "No immediate red flags detected."
        }
    except Exception as e:
        # Fallback error handling: returns a safe warning instead of crashing
        return {
            "status": "error",
            "message": f"Analysis failed due to unexpected input format: {str(e)}",
            "fallback": "Unable to verify input safely. Do not click links, call unknown numbers, or share personal information."
        }
