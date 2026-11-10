import re

def analyze_safety(input_text: str) -> dict:
    try:
        # Check for common suspicious keywords or URL patterns typical of scams
        suspicious_patterns = [r'http[s]?://[^\s]+', r'\b(verify|update|suspended|urgent|prize|winner|bank|irs)\b']
        found_flags = []
        
        for pattern in suspicious_patterns:
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
        return {
            "status": "error",
            "message": f"Analysis failed: {str(e)}",
            "fallback": "Unable to verify input safely. Do not click links or share information."
        }
