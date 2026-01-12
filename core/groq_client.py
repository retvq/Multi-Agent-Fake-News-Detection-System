

import aiohttp
import asyncio
import time
import json
import re
import logging
from datetime import datetime, date
from typing import Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)

class QuotaExceededError(Exception):
    
    pass

class GroqClient:
    
    
    API_URL = "https://api.groq.com/openai/v1/chat/completions"
    MODEL_ID = "llama-3.1-8b-instant"
    
    SYSTEM_PROMPT = 

    def __init__(
        self,
        api_key: str,
        daily_quota: int = 14400,
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
        
        logger.info(f"GroqClient initialized with quota {daily_quota}")
    
    def _check_quota_reset(self) -> None:
        
        today = date.today()
        if today > self.last_reset_date:
            logger.info(f"Resetting Groq quota (new day: {today})")
            self.usage_today = 0
            self.last_reset_date = today
    
    def _check_quota(self) -> None:
        
        self._check_quota_reset()
        if self.usage_today >= self.daily_quota:
            raise QuotaExceededError(
                f"Groq daily quota exceeded ({self.usage_today}/{self.daily_quota})"
            )
    
    def is_available(self) -> bool:
        
        if not self.api_key:
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
    
    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError)),
        reraise=True
    )
    async def _make_request(self, text: str) -> Dict[str, Any]:
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.MODEL_ID,
            "messages": [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": f"Analyze this text:\n\n{text[:3000]}"}
            ],
            "max_tokens": 500,
            "temperature": 0.1,
            "response_format": {"type": "json_object"}
        }
        
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(self.API_URL, json=payload, headers=headers) as response:
                if response.status == 429:
                    raise QuotaExceededError("Rate limit exceeded")
                elif response.status != 200:
                    error_text = await response.text()
                    raise aiohttp.ClientError(f"API error {response.status}: {error_text}")
                
                return await response.json()
    
    async def predict(self, text: str) -> Dict[str, Any]:
        
        start_time = time.time()
        
        try:
            self._check_quota()
            response = await self._make_request(text)
            self.usage_today += 1
            
            result = self._parse_response(response)
            processing_time = time.time() - start_time
            
            self.success_count += 1
            self.last_success_time = datetime.now()
            self._total_latency += processing_time
            
            return {
                "model_name": "groq",
                "fake_probability": result["fake_probability"],
                "confidence": result["confidence"],
                "processing_time": round(processing_time, 4),
                "reasoning": result.get("reasoning", ""),
                "red_flags": result.get("red_flags", []),
                "raw_response": response
            }
            
        except QuotaExceededError:
            self.error_count += 1
            raise
        except Exception as e:
            self.error_count += 1
            logger.error(f"Groq prediction failed: {e}")
            raise
    
    def _parse_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        
        try:
            choices = response.get("choices", [])
            if not choices:
                return self._default_result()
            
            message = choices[0].get("message", {})
            content = message.get("content", "")
            
            if not content:
                return self._default_result()
            
            try:
                result = json.loads(content)
            except json.JSONDecodeError:
                json_match = re.search(r'\{[^{}]*\}', content, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    return self._default_result()
            
            fake_probability = float(result.get("fake_probability", 0.5))
            confidence = float(result.get("confidence", 0.5))
            
            return {
                "fake_probability": round(max(0.0, min(1.0, fake_probability)), 4),
                "confidence": round(max(0.0, min(1.0, confidence)), 4),
                "reasoning": result.get("reasoning", ""),
                "red_flags": result.get("red_flags", [])
            }
            
        except Exception as e:
            logger.error(f"Failed to parse Groq response: {e}")
            return self._default_result()
    
    def _default_result(self) -> Dict[str, Any]:
        
        return {
            "fake_probability": 0.5,
            "confidence": 0.5,
            "reasoning": "Unable to analyze",
            "red_flags": []
        }
