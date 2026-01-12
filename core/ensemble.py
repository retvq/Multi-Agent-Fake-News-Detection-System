

import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

from .config import Config
from .heuristic import HeuristicAnalyzer
from .hf_client import HuggingFaceClient, QuotaExceededError as HFQuotaError
from .gemini_client import GeminiClient, QuotaExceededError as GeminiQuotaError
from .groq_client import GroqClient, QuotaExceededError as GroqQuotaError

logger = logging.getLogger(__name__)

@dataclass
class PredictionResult:
    
    prediction: str
    fake_probability: float
    confidence: float
    processing_time: float
    models_used: List[str]
    model_scores: List[Dict[str, Any]]
    indicators: Dict[str, float]
    indicator_details: List[Dict[str, Any]]
    explanation: str
    timestamp: str
    cached: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        
        return {
            "prediction": self.prediction,
            "fake_probability": self.fake_probability,
            "confidence": self.confidence,
            "processing_time": self.processing_time,
            "models_used": self.models_used,
            "model_scores": self.model_scores,
            "indicators": self.indicators,
            "indicator_details": self.indicator_details,
            "explanation": self.explanation,
            "timestamp": self.timestamp,
            "cached": self.cached
        }

class EnsemblePredictor:
    
    
    def __init__(self, config: Config):
        
        self.config = config
        
        self.heuristic = HeuristicAnalyzer()
        
        self.hf_client = HuggingFaceClient(
            api_key=config.hf_api_key,
            daily_quota=config.hf_daily_quota,
            timeout=config.model_timeout
        )
        
        self.gemini_client = GeminiClient(
            api_key=config.gemini_api_key,
            daily_quota=config.gemini_daily_quota,
            timeout=config.model_timeout
        )
        
        self.groq_client = GroqClient(
            api_key=config.groq_api_key,
            daily_quota=config.groq_daily_quota,
            timeout=config.model_timeout
        )
        
        logger.info(
            f"EnsemblePredictor initialized. "
            f"Active models: {config.get_active_models()}"
        )
    
    async def predict(self, text: str) -> Dict[str, Any]:
        
        start_time = time.time()
        
        model_results = await self._run_models_parallel(text)
        
        result = self._aggregate_results(model_results)
        
        result["processing_time"] = round(time.time() - start_time, 4)
        result["timestamp"] = datetime.now().isoformat()
        
        logger.info(
            f"Ensemble prediction: {result['prediction']} "
            f"(prob={result['fake_probability']:.2f}, "
            f"conf={result['confidence']:.2f}, "
            f"models={result['models_used']})"
        )
        
        return result
    
    async def _run_models_parallel(self, text: str) -> List[Dict[str, Any]]:
        
        results = []
        
        try:
            heuristic_result = self.heuristic.analyze(text)
            results.append(heuristic_result)
        except Exception as e:
            logger.error(f"Heuristic analysis failed: {e}")
        
        if self.config.has_hf_key() and self.hf_client.is_available():
            try:
                hf_result = await self._run_with_timeout(
                    self.hf_client.predict(text),
                    self.config.model_timeout,
                    "huggingface"
                )
                results.append(hf_result)
            except Exception as e:
                logger.warning(f"HuggingFace failed: {e}")
        
        llm_result = await self._run_llm_with_fallback(text)
        if llm_result:
            results.append(llm_result)
        
        return results
    
    async def _run_llm_with_fallback(self, text: str) -> Optional[Dict[str, Any]]:
        
        if self.config.has_gemini_key() and self.gemini_client.is_available():
            try:
                result = await self._run_with_timeout(
                    self.gemini_client.predict(text),
                    self.config.model_timeout,
                    "gemini"
                )
                logger.info("Gemini prediction successful")
                return result
            except GeminiQuotaError as e:
                logger.warning(f"Gemini quota exceeded, falling back to Groq: {e}")
            except Exception as e:
                logger.warning(f"Gemini failed, falling back to Groq: {e}")
        
        if self.config.has_groq_key() and self.groq_client.is_available():
            try:
                result = await self._run_with_timeout(
                    self.groq_client.predict(text),
                    self.config.model_timeout,
                    "groq"
                )
                logger.info("Groq prediction successful (fallback)")
                return result
            except GroqQuotaError as e:
                logger.warning(f"Groq quota exceeded: {e}")
            except Exception as e:
                logger.warning(f"Groq failed: {e}")
        
        logger.warning("Both Gemini and Groq unavailable, using heuristic only")
        return None
    
    async def _run_with_timeout(
        self,
        coro,
        timeout: int,
        model_name: str
    ) -> Dict[str, Any]:
        
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            logger.warning(f"Model {model_name} timed out after {timeout}s")
            raise
    
    def _aggregate_results(
        self,
        model_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        
        if not model_results:
            return self._create_fallback_result()
        
        weighted_prob = 0.0
        weighted_conf = 0.0
        total_weight = 0.0
        
        models_used = []
        model_scores = []
        indicators = {}
        indicator_details = []
        
        weight_mapping = {
            "heuristic": "heuristic",
            "huggingface": "huggingface",
            "gemini": "llm",
            "groq": "llm"
        }
        
        for result in model_results:
            model_name = result.get("model_name", "unknown")
            models_used.append(model_name)
            
            weight_key = weight_mapping.get(model_name, model_name)
            weight = self.config.ensemble_weights.get(weight_key, 0.1)
            
            prob = result.get("fake_probability", 0.5)
            conf = result.get("confidence", 0.5)
            
            weighted_prob += prob * weight
            weighted_conf += conf * weight
            total_weight += weight
            
            model_scores.append({
                "model_name": model_name,
                "fake_probability": prob,
                "confidence": conf,
                "processing_time": result.get("processing_time", 0),
                "weight": weight
            })
            
            if model_name == "heuristic":
                indicators = result.get("indicators", {})
                indicator_details = result.get("indicator_details", [])
        
        if total_weight > 0:
            fake_probability = weighted_prob / total_weight
            confidence = weighted_conf / total_weight
        else:
            fake_probability = 0.5
            confidence = 0.5
        
        prediction = self._determine_verdict(fake_probability, confidence)
        
        explanation = self._generate_explanation(
            prediction, fake_probability, confidence, model_scores, indicators
        )
        
        return {
            "prediction": prediction,
            "fake_probability": round(fake_probability, 4),
            "confidence": round(confidence, 4),
            "models_used": models_used,
            "model_scores": model_scores,
            "indicators": indicators,
            "indicator_details": indicator_details,
            "explanation": explanation,
            "processing_time": 0,
            "timestamp": "",
            "cached": False
        }
    
    def _determine_verdict(
        self,
        fake_probability: float,
        confidence: float
    ) -> str:
        
        if confidence < self.config.min_confidence:
            return "UNCERTAIN"
        
        if fake_probability >= self.config.fake_threshold:
            return "FAKE"
        elif fake_probability <= self.config.real_threshold:
            return "REAL"
        else:
            return "UNCERTAIN"
    
    def _generate_explanation(
        self,
        prediction: str,
        fake_probability: float,
        confidence: float,
        model_scores: List[Dict[str, Any]],
        indicators: Dict[str, float]
    ) -> str:
        
        parts = []
        
        if prediction == "FAKE":
            parts.append(
                f"This article shows strong indicators of misinformation "
                f"(fake probability: {fake_probability*100:.0f}%)."
            )
        elif prediction == "REAL":
            parts.append(
                f"This article appears to be authentic "
                f"(fake probability: {fake_probability*100:.0f}%)."
            )
        else:
            parts.append(
                f"The analysis is inconclusive "
                f"(fake probability: {fake_probability*100:.0f}%)."
            )
        
        if len(model_scores) > 1:
            scores = [m["fake_probability"] for m in model_scores]
            min_score, max_score = min(scores), max(scores)
            if max_score - min_score < 0.2:
                parts.append("All models are in agreement.")
            else:
                parts.append(f"Model predictions vary from {min_score*100:.0f}% to {max_score*100:.0f}%.")
        
        high_indicators = [
            name for name, score in indicators.items()
            if score >= 0.5
        ]
        if high_indicators:
            formatted = ", ".join(name.replace("_", " ") for name in high_indicators)
            parts.append(f"Key concerns: {formatted}.")
        
        if confidence < 0.7:
            parts.append("Note: Confidence is moderate. Consider additional verification.")
        
        return " ".join(parts)
    
    def _create_fallback_result(self) -> Dict[str, Any]:
        
        return {
            "prediction": "UNCERTAIN",
            "fake_probability": 0.5,
            "confidence": 0.0,
            "models_used": [],
            "model_scores": [],
            "indicators": {},
            "indicator_details": [],
            "explanation": "Unable to analyze: all models failed. Please try again.",
            "processing_time": 0,
            "timestamp": datetime.now().isoformat(),
            "cached": False
        }
    
    def get_system_health(self) -> Dict[str, Any]:
        
        hf_health = self.hf_client.get_health_stats()
        gemini_health = self.gemini_client.get_health_stats()
        groq_health = self.groq_client.get_health_stats()
        
        api_healthy = (
            hf_health["status"] == "healthy" or 
            gemini_health["status"] == "healthy" or
            groq_health["status"] == "healthy"
        )
        overall_status = "healthy" if api_healthy else "degraded"
        
        return {
            "overall_status": overall_status,
            "active_models": self.config.get_active_models(),
            "huggingface": hf_health,
            "gemini": gemini_health,
            "groq": groq_health,
            "heuristic": {"status": "healthy"},
            "weights": self.config.ensemble_weights
        }
