

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import os
import logging

logger = logging.getLogger(__name__)

@dataclass
class Config:
    
    
    hf_api_key: str = ""
    gemini_api_key: str = ""
    groq_api_key: str = ""
    
    hf_daily_quota: int = 30000
    gemini_daily_quota: int = 1500
    groq_daily_quota: int = 14400
    
    ensemble_weights: Dict[str, float] = field(default_factory=lambda: {
        "huggingface": 0.40,
        "llm": 0.35,
        "heuristic": 0.25
    })
    
    fake_threshold: float = 0.7
    real_threshold: float = 0.3
    min_confidence: float = 0.6
    
    max_text_length: int = 5000
    min_text_length: int = 50
    
    cache_ttl_hours: int = 24
    request_timeout: int = 30
    model_timeout: int = 10
    
    hf_model_id: str = "hamzab/roberta-fake-news-classification"
    
    @classmethod
    def from_secrets(cls, secrets: Optional[Any] = None) -> "Config":
        
        config = cls()
        
        config.hf_api_key = os.environ.get("HF_API_KEY", "")
        config.gemini_api_key = os.environ.get("GEMINI_API_KEY", "")
        config.groq_api_key = os.environ.get("GROQ_API_KEY", "")
        
        if secrets is None:
            logger.warning("No secrets provided, using environment variables or defaults")
            return config
        
        try:
            config.hf_api_key = secrets.get("HF_API_KEY", config.hf_api_key)
            config.gemini_api_key = secrets.get("GEMINI_API_KEY", config.gemini_api_key)
            config.groq_api_key = secrets.get("GROQ_API_KEY", config.groq_api_key)
            
            config.hf_daily_quota = int(secrets.get("HF_DAILY_QUOTA", 30000))
            config.gemini_daily_quota = int(secrets.get("GEMINI_DAILY_QUOTA", 1500))
            config.groq_daily_quota = int(secrets.get("GROQ_DAILY_QUOTA", 14400))
            
            if "ensemble_weights" in secrets:
                weights = dict(secrets["ensemble_weights"])
                weight_sum = sum(weights.values())
                if 0.99 <= weight_sum <= 1.01:
                    config.ensemble_weights = weights
                else:
                    logger.warning(f"Ensemble weights sum to {weight_sum}, not 1.0. Using defaults.")
            
            config.fake_threshold = float(secrets.get("FAKE_THRESHOLD", 0.7))
            config.real_threshold = float(secrets.get("REAL_THRESHOLD", 0.3))
            config.min_confidence = float(secrets.get("MIN_CONFIDENCE", 0.6))
            
            config.max_text_length = int(secrets.get("MAX_TEXT_LENGTH", 5000))
            config.min_text_length = int(secrets.get("MIN_TEXT_LENGTH", 50))
            
            config.cache_ttl_hours = int(secrets.get("CACHE_TTL_HOURS", 24))
            config.request_timeout = int(secrets.get("REQUEST_TIMEOUT", 30))
            config.model_timeout = int(secrets.get("MODEL_TIMEOUT", 10))
            
            logger.info("Configuration loaded successfully from secrets")
            
        except Exception as e:
            logger.error(f"Error loading configuration: {e}. Using defaults.")
        
        return config
    
    def has_hf_key(self) -> bool:
        
        return bool(self.hf_api_key and self.hf_api_key != "hf_your_huggingface_api_key_here")
    
    def has_gemini_key(self) -> bool:
        
        return bool(self.gemini_api_key and self.gemini_api_key != "your_gemini_api_key_here")
    
    def has_groq_key(self) -> bool:
        
        return bool(self.groq_api_key and self.groq_api_key != "your_groq_api_key_here")
    
    def get_active_models(self) -> list:
        
        models = ["heuristic"]
        
        if self.has_hf_key():
            models.append("huggingface")
        if self.has_gemini_key():
            models.append("gemini")
        if self.has_groq_key():
            models.append("groq")
            
        return models
    
    def to_dict(self) -> Dict[str, Any]:
        
        return {
            "hf_api_key": "***" if self.hf_api_key else "Not set",
            "gemini_api_key": "***" if self.gemini_api_key else "Not set",
            "groq_api_key": "***" if self.groq_api_key else "Not set",
            "hf_daily_quota": self.hf_daily_quota,
            "gemini_daily_quota": self.gemini_daily_quota,
            "groq_daily_quota": self.groq_daily_quota,
            "ensemble_weights": self.ensemble_weights,
            "fake_threshold": self.fake_threshold,
            "real_threshold": self.real_threshold,
            "min_confidence": self.min_confidence,
            "max_text_length": self.max_text_length,
            "min_text_length": self.min_text_length,
            "cache_ttl_hours": self.cache_ttl_hours,
            "request_timeout": self.request_timeout,
            "model_timeout": self.model_timeout,
            "active_models": self.get_active_models()
        }
