

import re
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)

def validate_text_length(
    text: str,
    min_length: int = 50,
    max_length: int = 5000
) -> Tuple[bool, str]:
    
    if not text or not text.strip():
        return False, "Please enter some text to analyze."
    
    text = text.strip()
    length = len(text)
    
    if length < min_length:
        remaining = min_length - length
        return False, f"Text is too short. Need {remaining} more characters (minimum {min_length})."
    
    if length > max_length:
        excess = length - max_length
        return False, f"Text is too long by {excess} characters (maximum {max_length})."
    
    return True, f"✓ Valid text ({length} characters)"

def validate_url(url: str) -> Tuple[bool, str]:
    
    if not url or not url.strip():
        return True, ""
    
    url = url.strip()
    
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    
    if re.match(pattern, url, re.IGNORECASE):
        return True, "✓ Valid URL"
    else:
        return False, "Please enter a valid URL (starting with http:// or https://)"

def validate_source_name(source: str) -> Tuple[bool, str]:
    
    if not source or not source.strip():
        return True, ""
    
    source = source.strip()
    
    if len(source) < 2:
        return False, "Source name too short (minimum 2 characters)"
    
    if len(source) > 100:
        return False, "Source name too long (maximum 100 characters)"
    
    return True, "✓ Valid source"

def get_character_count_display(text: str, max_length: int = 5000) -> Tuple[str, str]:
    
    length = len(text) if text else 0
    remaining = max_length - length
    
    if length == 0:
        return "Enter text to analyze", "empty"
    elif length < 50:
        needed = 50 - length
        return f"Need {needed} more characters (minimum 50)", "short"
    elif length <= max_length:
        return f"{length} characters ({remaining} remaining)", "valid"
    else:
        excess = length - max_length
        return f"Text too long by {excess} characters", "long"

def sanitize_text(text: str) -> str:
    
    if not text:
        return ""
    
    text = text.replace('\x00', '')
    
    text = ' '.join(text.split())
    
    text = ''.join(
        char for char in text
        if char.isprintable() or char in '\n\t'
    )
    
    return text.strip()
