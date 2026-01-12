

import re
import time
from typing import Dict, Any, List, Set
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class IndicatorResult:
    
    name: str
    score: float
    severity: str
    description: str
    matches: List[str] = None

class HeuristicAnalyzer:
    
    
    EMOTIONAL_WORDS: Set[str] = {
        "shocking", "unbelievable", "incredible", "astonishing", "mindblowing",
        "jaw-dropping", "bombshell", "explosive", "stunning", "outrageous",
        "terrifying", "horrifying", "alarming", "devastating", "catastrophic",
        "dangerous", "deadly", "crisis", "emergency", "urgent",
        "disgraceful", "scandalous", "corrupt", "evil", "sinister",
        "betrayal", "conspiracy", "coverup", "exposed", "revealed",
        "amazing", "revolutionary", "breakthrough", "miracle", "secret",
        "banned", "censored", "forbidden", "hidden", "suppressed",
        "never", "always", "everyone", "nobody", "completely", "totally",
        "absolutely", "definitely", "proven", "confirmed"
    }
    
    CLICKBAIT_PATTERNS: List[str] = [
        r"you\s+won'?t\s+believe",
        r"what\s+happens?\s+next",
        r"doctors?\s+hate\s+(him|her|this|them)",
        r"this\s+one\s+(simple|weird|strange)\s+trick",
        r"the\s+truth\s+about",
        r"exposed:?\s+",
        r"breaking:?\s+",
        r"must\s+(see|read|watch)",
        r"click\s+here\s+to",
        r"share\s+before\s+(it'?s?\s+)?deleted",
        r"they\s+don'?t\s+want\s+you\s+to\s+know",
        r"is\s+this\s+the\s+end\s+of",
        r"finally\s+revealed",
        r"\d+\s+reasons?\s+why",
        r"number\s+\d+\s+will\s+(shock|surprise|amaze)"
    ]
    
    _compiled_patterns: List[re.Pattern] = None
    
    def __init__(self):
        
        if HeuristicAnalyzer._compiled_patterns is None:
            HeuristicAnalyzer._compiled_patterns = [
                re.compile(pattern, re.IGNORECASE)
                for pattern in self.CLICKBAIT_PATTERNS
            ]
        logger.info("HeuristicAnalyzer initialized")
    
    def analyze(self, text: str) -> Dict[str, Any]:
        
        start_time = time.time()
        
        if not text or not text.strip():
            return self._empty_result(time.time() - start_time)
        
        text_lower = text.lower()
        text_stripped = text.strip()
        
        emotional_result = self._analyze_emotional_language(text_lower)
        clickbait_result = self._analyze_clickbait_patterns(text_lower)
        punctuation_result = self._analyze_excessive_punctuation(text_stripped)
        caps_result = self._analyze_caps_ratio(text_stripped)
        
        indicators = {
            "emotional_language": emotional_result.score,
            "clickbait_patterns": clickbait_result.score,
            "excessive_punctuation": punctuation_result.score,
            "caps_ratio": caps_result.score
        }
        
        indicator_details = [
            emotional_result,
            clickbait_result,
            punctuation_result,
            caps_result
        ]
        
        weights = {
            "emotional_language": 0.25,
            "clickbait_patterns": 0.35,
            "excessive_punctuation": 0.20,
            "caps_ratio": 0.20
        }
        
        fake_probability = sum(
            indicators[key] * weights[key]
            for key in indicators
        )
        
        avg_extremity = sum(
            abs(score - 0.5) * 2
            for score in indicators.values()
        ) / len(indicators)
        confidence = min(0.5 + avg_extremity * 0.5, 0.85)
        
        processing_time = time.time() - start_time
        
        return {
            "model_name": "heuristic",
            "fake_probability": round(fake_probability, 4),
            "confidence": round(confidence, 4),
            "processing_time": round(processing_time, 4),
            "indicators": indicators,
            "indicator_details": [
                {
                    "name": ind.name,
                    "score": ind.score,
                    "severity": ind.severity,
                    "description": ind.description,
                    "matches": ind.matches
                }
                for ind in indicator_details
            ]
        }
    
    def _analyze_emotional_language(self, text_lower: str) -> IndicatorResult:
        
        words = set(re.findall(r'\b[a-z]+\b', text_lower))
        matches = words.intersection(self.EMOTIONAL_WORDS)
        
        word_count = len(words)
        if word_count == 0:
            score = 0.0
        else:
            density = len(matches) / word_count
            score = min(density * 33, 1.0)
        
        severity = self._get_severity(score)
        
        return IndicatorResult(
            name="Emotional Language",
            score=round(score, 4),
            severity=severity,
            description=f"Found {len(matches)} emotionally charged words",
            matches=list(matches)[:5]
        )
    
    def _analyze_clickbait_patterns(self, text_lower: str) -> IndicatorResult:
        
        matches = []
        
        for pattern in self._compiled_patterns:
            found = pattern.findall(text_lower)
            if found:
                matches.extend(found if isinstance(found[0], str) else [m[0] for m in found])
        
        if len(matches) == 0:
            score = 0.0
        elif len(matches) == 1:
            score = 0.4
        elif len(matches) == 2:
            score = 0.7
        else:
            score = 1.0
        
        severity = self._get_severity(score)
        
        return IndicatorResult(
            name="Clickbait Patterns",
            score=round(score, 4),
            severity=severity,
            description=f"Found {len(matches)} clickbait pattern(s)",
            matches=matches[:5]
        )
    
    def _analyze_excessive_punctuation(self, text: str) -> IndicatorResult:
        
        total_chars = len(text)
        if total_chars == 0:
            return IndicatorResult(
                name="Excessive Punctuation",
                score=0.0,
                severity="LOW",
                description="No text to analyze",
                matches=[]
            )
        
        exclamations = text.count('!')
        questions = text.count('?')
        emphatic_chars = exclamations + questions
        
        repeated = len(re.findall(r'[!?]{2,}', text))
        
        ratio = emphatic_chars / total_chars
        
        if ratio > 0.05:
            score = 1.0
        elif ratio > 0.02:
            score = 0.5 + (ratio - 0.02) / 0.03 * 0.5
        else:
            score = ratio / 0.02 * 0.5
        
        score = min(score + repeated * 0.1, 1.0)
        
        severity = self._get_severity(score)
        
        return IndicatorResult(
            name="Excessive Punctuation",
            score=round(score, 4),
            severity=severity,
            description=f"Found {exclamations}x '!' and {questions}x '?' ({ratio:.1%} of text)",
            matches=[f"!×{exclamations}", f"?×{questions}"] if emphatic_chars > 0 else []
        )
    
    def _analyze_caps_ratio(self, text: str) -> IndicatorResult:
        
        letters = [c for c in text if c.isalpha()]
        total_letters = len(letters)
        
        if total_letters == 0:
            return IndicatorResult(
                name="ALL CAPS Usage",
                score=0.0,
                severity="LOW",
                description="No letters to analyze",
                matches=[]
            )
        
        uppercase = sum(1 for c in letters if c.isupper())
        ratio = uppercase / total_letters
        
        caps_words = re.findall(r'\b[A-Z]{3,}\b', text)
        
        if ratio > 0.5:
            score = 1.0
        elif ratio > 0.3:
            score = 0.5 + (ratio - 0.3) / 0.2 * 0.5
        else:
            score = ratio / 0.3 * 0.5
        
        severity = self._get_severity(score)
        
        return IndicatorResult(
            name="ALL CAPS Usage",
            score=round(score, 4),
            severity=severity,
            description=f"{ratio:.1%} uppercase letters, {len(caps_words)} ALL CAPS words",
            matches=caps_words[:5]
        )
    
    def _get_severity(self, score: float) -> str:
        
        if score >= 0.7:
            return "HIGH"
        elif score >= 0.4:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _empty_result(self, processing_time: float) -> Dict[str, Any]:
        
        return {
            "model_name": "heuristic",
            "fake_probability": 0.0,
            "confidence": 0.0,
            "processing_time": round(processing_time, 4),
            "indicators": {
                "emotional_language": 0.0,
                "clickbait_patterns": 0.0,
                "excessive_punctuation": 0.0,
                "caps_ratio": 0.0
            },
            "indicator_details": []
        }
