

import asyncio
import time
import logging
from datetime import datetime, date
from typing import Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor

try:
    from huggingface_hub import InferenceClient
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False

logger = logging.getLogger(__name__)

class QuotaExceededError(Exception):
    
    pass

class HuggingFaceClient:
    
    
    MODEL_ID = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    
    def __init__(
        self,
        api_key: str,
        daily_quota: int = 30000,
        timeout: int = 10
    ):
        self.api_key = api_key
        self.daily_quota = daily_quota
        self.timeout = timeout
        self.usage_today = 0
        self.last_reset_date = date.today()
        self.last_success_time: Optional[datetime] = None
        self.success_count = 0
        self.error_count = 0
        self._total_latency = 0.0
        self._executor = ThreadPoolExecutor(max_workers=2)
        
        if HF_AVAILABLE and api_key:
            self._client = InferenceClient(token=api_key)
        else:
            self._client = None
        
        logger.info(f"HuggingFaceClient initialized with sentiment model")
    
    def _check_quota_reset(self) -> None:
        today = date.today()
        if today > self.last_reset_date:
            self.usage_today = 0
            self.last_reset_date = today
    
    def _check_quota(self) -> None:
        self._check_quota_reset()
        if self.usage_today >= self.daily_quota:
            raise QuotaExceededError(f"HuggingFace quota exceeded")
    
    def is_available(self) -> bool:
        if not self.api_key or not HF_AVAILABLE or not self._client:
            return False
        self._check_quota_reset()
        return self.usage_today < self.daily_quota
    
    def get_quota_usage(self) -> Dict[str, Any]:
        self._check_quota_reset()
        return {
            "used": self.usage_today,
            "total": self.daily_quota,
            "remaining": max(0, self.daily_quota - self.usage_today),
            "percentage": (self.usage_today / self.daily_quota) * 100 if self.daily_quota > 0 else 0,
            "reset_date": self.last_reset_date.isoformat()
        }
    
    def get_health_stats(self) -> Dict[str, Any]:
        total_requests = self.success_count + self.error_count
        return {
            "status": "healthy" if self.is_available() else "unavailable",
            "last_success": self.last_success_time.isoformat() if self.last_success_time else None,
            "success_rate": (self.success_count / total_requests * 100) if total_requests > 0 else 100,
            "avg_latency": (self._total_latency / self.success_count) if self.success_count > 0 else 0,
            "quota": self.get_quota_usage()
        }
    
    def _sync_classify(self, text: str) -> Any:
        return self._client.text_classification(
            text[:512],
            model=self.MODEL_ID
        )
    
    async def predict(self, text: str) -> Dict[str, Any]:
        start_time = time.time()
        
        try:
            self._check_quota()
            
            if not self._client:
                raise RuntimeError("HuggingFace client not initialized")
            
            loop = asyncio.get_event_loop()
            response = await asyncio.wait_for(
                loop.run_in_executor(self._executor, self._sync_classify, text),
                timeout=self.timeout
            )
            
            self.usage_today += 1
            result = self._parse_response(response)
            processing_time = time.time() - start_time
            
            self.success_count += 1
            self.last_success_time = datetime.now()
            self._total_latency += processing_time
            
            return {
                "model_name": "huggingface",
                "fake_probability": result["fake_probability"],
                "confidence": result["confidence"],
                "processing_time": round(processing_time, 4),
                "sentiment": result["sentiment"],
                "raw_response": str(response)
            }
            
        except QuotaExceededError:
            self.error_count += 1
            raise
        except Exception as e:
            self.error_count += 1
            logger.error(f"HuggingFace prediction failed: {e}")
            raise
    
    def _parse_response(self, response: Any) -> Dict[str, float]:
        
        try:
            scores = {}
            for item in response:
                label = getattr(item, 'label', '').lower()
                score = getattr(item, 'score', 0.0)
                scores[label] = score
            
            negative = scores.get('negative', 0.0)
            neutral = scores.get('neutral', 0.0)
            positive = scores.get('positive', 0.0)
            
            fake_probability = (
                negative * 0.85 +
                positive * 0.4 +
                neutral * 0.15
            )
            
            fake_probability = max(0.0, min(1.0, fake_probability))
            
            max_score = max(negative, neutral, positive)
            confidence = max_score
            
            if negative >= neutral and negative >= positive:
                sentiment = "negative"
            elif neutral >= negative and neutral >= positive:
                sentiment = "neutral"
            else:
                sentiment = "positive"
            
            return {
                "fake_probability": round(fake_probability, 4),
                "confidence": round(confidence, 4),
                "sentiment": sentiment
            }
            
        except Exception as e:
            logger.error(f"Failed to parse HuggingFace response: {e}")
            return {"fake_probability": 0.5, "confidence": 0.5, "sentiment": "unknown"}
