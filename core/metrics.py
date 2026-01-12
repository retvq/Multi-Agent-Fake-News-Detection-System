

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from collections import deque
import statistics

logger = logging.getLogger(__name__)

@dataclass
class PredictionRecord:
    
    timestamp: datetime
    prediction: str
    fake_probability: float
    confidence: float
    processing_time: float
    models_used: List[str]
    cached: bool
    text_preview: str

@dataclass
class ErrorRecord:
    
    timestamp: datetime
    severity: str
    message: str
    component: str
    details: Optional[str] = None

class MetricsTracker:
    
    
    def __init__(
        self,
        max_predictions: int = 1000,
        max_errors: int = 100
    ):
        
        self.max_predictions = max_predictions
        self.max_errors = max_errors
        self.predictions: deque = deque(maxlen=max_predictions)
        self.errors: deque = deque(maxlen=max_errors)
        self.session_start = datetime.now()
        
        self._total_predictions = 0
        self._total_fake = 0
        self._total_real = 0
        self._total_uncertain = 0
        self._total_cached = 0
        self._total_latency = 0.0
        
        logger.info("MetricsTracker initialized")
    
    def record_prediction(
        self,
        result: Dict[str, Any],
        text: str = ""
    ) -> None:
        
        try:
            record = PredictionRecord(
                timestamp=datetime.now(),
                prediction=result.get("prediction", "UNCERTAIN"),
                fake_probability=result.get("fake_probability", 0.5),
                confidence=result.get("confidence", 0.5),
                processing_time=result.get("processing_time", 0.0),
                models_used=result.get("models_used", []),
                cached=result.get("cached", False),
                text_preview=text[:100] + "..." if len(text) > 100 else text
            )
            
            self.predictions.append(record)
            
            self._total_predictions += 1
            self._total_latency += record.processing_time
            
            if record.prediction == "FAKE":
                self._total_fake += 1
            elif record.prediction == "REAL":
                self._total_real += 1
            else:
                self._total_uncertain += 1
            
            if record.cached:
                self._total_cached += 1
            
            logger.debug(f"Recorded prediction: {record.prediction}")
            
        except Exception as e:
            logger.error(f"Failed to record prediction: {e}")
    
    def record_error(
        self,
        error: Exception,
        component: str,
        severity: str = "ERROR"
    ) -> None:
        
        try:
            record = ErrorRecord(
                timestamp=datetime.now(),
                severity=severity,
                message=str(error),
                component=component,
                details=error.__class__.__name__
            )
            
            self.errors.append(record)
            logger.debug(f"Recorded {severity} in {component}: {error}")
            
        except Exception as e:
            logger.error(f"Failed to record error: {e}")
    
    def get_prediction_stats(self) -> Dict[str, Any]:
        
        if self._total_predictions == 0:
            return {
                "total_predictions": 0,
                "fake_count": 0,
                "real_count": 0,
                "uncertain_count": 0,
                "fake_percentage": 0,
                "real_percentage": 0,
                "uncertain_percentage": 0,
                "avg_confidence": 0,
                "avg_latency": 0,
                "cache_hit_rate": 0
            }
        
        total = self._total_predictions
        
        return {
            "total_predictions": total,
            "fake_count": self._total_fake,
            "real_count": self._total_real,
            "uncertain_count": self._total_uncertain,
            "fake_percentage": round(self._total_fake / total * 100, 1),
            "real_percentage": round(self._total_real / total * 100, 1),
            "uncertain_percentage": round(self._total_uncertain / total * 100, 1),
            "avg_confidence": round(
                sum(p.confidence for p in self.predictions) / len(self.predictions), 4
            ) if self.predictions else 0,
            "avg_latency": round(self._total_latency / total, 4),
            "cache_hit_rate": round(self._total_cached / total * 100, 1)
        }
    
    def get_latency_percentiles(self) -> Dict[str, float]:
        
        if not self.predictions:
            return {"p50": 0, "p95": 0, "p99": 0}
        
        latencies = sorted(p.processing_time for p in self.predictions)
        n = len(latencies)
        
        def percentile(p):
            k = (n - 1) * (p / 100)
            f = int(k)
            c = min(f + 1, n - 1)
            if f == c:
                return latencies[f]
            return latencies[f] * (c - k) + latencies[c] * (k - f)
        
        return {
            "p50": round(percentile(50), 4),
            "p95": round(percentile(95), 4),
            "p99": round(percentile(99), 4)
        }
    
    def get_recent_predictions(self, limit: int = 10) -> List[Dict[str, Any]]:
        
        recent = list(self.predictions)[-limit:]
        recent.reverse()
        
        return [
            {
                "timestamp": p.timestamp.isoformat(),
                "prediction": p.prediction,
                "fake_probability": p.fake_probability,
                "confidence": p.confidence,
                "processing_time": p.processing_time,
                "models_used": p.models_used,
                "cached": p.cached,
                "text_preview": p.text_preview
            }
            for p in recent
        ]
    
    def get_recent_errors(self, limit: int = 20, severity: Optional[str] = None) -> List[Dict[str, Any]]:
        
        errors = list(self.errors)
        if severity:
            errors = [e for e in errors if e.severity == severity]
        
        errors.reverse()
        errors = errors[:limit]
        
        return [
            {
                "timestamp": e.timestamp.isoformat(),
                "severity": e.severity,
                "message": e.message,
                "component": e.component,
                "details": e.details
            }
            for e in errors
        ]
    
    def get_session_info(self) -> Dict[str, Any]:
        
        uptime = datetime.now() - self.session_start
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        return {
            "session_start": self.session_start.isoformat(),
            "uptime": f"{uptime.days}d {hours}h {minutes}m {seconds}s",
            "uptime_seconds": uptime.total_seconds(),
            "predictions_per_hour": round(
                self._total_predictions / max(uptime.total_seconds() / 3600, 0.001), 2
            )
        }
    
    def get_model_usage(self) -> Dict[str, int]:
        
        usage = {}
        for p in self.predictions:
            for model in p.models_used:
                usage[model] = usage.get(model, 0) + 1
        return usage
    
    def get_all_stats(self) -> Dict[str, Any]:
        
        return {
            "predictions": self.get_prediction_stats(),
            "latency": self.get_latency_percentiles(),
            "session": self.get_session_info(),
            "model_usage": self.get_model_usage(),
            "error_count": len(self.errors)
        }
