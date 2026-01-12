

from datetime import datetime
from typing import Any, Optional
import json

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def format_timestamp(
    timestamp: Any,
    format_string: str = "%Y-%m-%d %H:%M:%S"
) -> str:
    
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.fromisoformat(timestamp)
        except ValueError:
            return timestamp
    
    if isinstance(timestamp, datetime):
        return timestamp.strftime(format_string)
    
    return str(timestamp)

def format_relative_time(timestamp: datetime) -> str:
    
    if not isinstance(timestamp, datetime):
        try:
            timestamp = datetime.fromisoformat(str(timestamp))
        except (ValueError, TypeError):
            return "Unknown"
    
    now = datetime.now()
    diff = now - timestamp
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return "Just now"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    else:
        days = int(seconds / 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"

def format_percentage(value: float, decimal_places: int = 1) -> str:
    
    return f"{value * 100:.{decimal_places}f}%"

def format_probability(value: float) -> str:
    
    if value < 0.01:
        return "<1%"
    elif value > 0.99:
        return ">99%"
    else:
        return f"{value * 100:.0f}%"

def format_latency(seconds: float) -> str:
    
    if seconds < 0.001:
        return "<1ms"
    elif seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    else:
        return f"{seconds:.2f}s"

def format_file_size(bytes_count: int) -> str:
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_count < 1024:
            return f"{bytes_count:.1f} {unit}"
        bytes_count /= 1024
    return f"{bytes_count:.1f} TB"

def format_verdict_color(prediction: str) -> dict:
    
    colors = {
        'FAKE': {
            'bg': '#fee2e2',
            'border': '#ef4444',
            'text': '#991b1b',
            'icon': '❌'
        },
        'REAL': {
            'bg': '#d1fae5',
            'border': '#10b981',
            'text': '#065f46',
            'icon': '✅'
        },
        'UNCERTAIN': {
            'bg': '#fef3c7',
            'border': '#f59e0b',
            'text': '#92400e',
            'icon': '⚠️'
        }
    }
    return colors.get(prediction, colors['UNCERTAIN'])

def format_severity_color(severity: str) -> str:
    
    colors = {
        'LOW': '#10b981',
        'MEDIUM': '#f59e0b',
        'HIGH': '#ef4444'
    }
    return colors.get(severity, '#6b7280')

def result_to_json(result: dict, indent: int = 2) -> str:
    
    return json.dumps(result, indent=indent, default=str)

def format_model_name(name: str) -> str:
    
    names = {
        'heuristic': '🔍 Heuristic Analyzer',
        'huggingface': '🤗 HuggingFace RoBERTa',
        'together': '🦙 Together.ai Llama'
    }
    return names.get(name, name.title())
