

import pytest
import sys
import os
import asyncio
from unittest.mock import Mock, AsyncMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import Config
from core.ensemble import EnsemblePredictor

@pytest.fixture
def config():
    
    return Config(
        hf_api_key="",
        gemini_api_key="",
        groq_api_key="",
        ensemble_weights={
            "huggingface": 0.40,
            "llm": 0.35,
            "heuristic": 0.25
        },
        fake_threshold=0.7,
        real_threshold=0.3,
        min_confidence=0.6
    )

@pytest.fixture
def config_with_keys():
    
    return Config(
        hf_api_key="hf_test_key",
        gemini_api_key="test_gemini_key",
        groq_api_key="test_groq_key",
        ensemble_weights={
            "huggingface": 0.40,
            "llm": 0.35,
            "heuristic": 0.25
        }
    )

@pytest.fixture
def ensemble(config):
    
    return EnsemblePredictor(config)

class TestEnsembleInitialization:
    
    
    def test_initialization(self, ensemble):
        
        assert ensemble.heuristic is not None
        assert ensemble.hf_client is not None
        assert ensemble.gemini_client is not None
        assert ensemble.groq_client is not None
    
    def test_heuristic_only_mode(self, config):
        
        ensemble = EnsemblePredictor(config)
        active_models = config.get_active_models()
        
        assert 'heuristic' in active_models
        assert len(active_models) == 1

class TestVerdictDetermination:
    
    
    def test_fake_verdict(self, ensemble):
        
        verdict = ensemble._determine_verdict(0.85, 0.8)
        assert verdict == "FAKE"
    
    def test_real_verdict(self, ensemble):
        
        verdict = ensemble._determine_verdict(0.15, 0.8)
        assert verdict == "REAL"
    
    def test_uncertain_verdict_mid_prob(self, ensemble):
        
        verdict = ensemble._determine_verdict(0.5, 0.8)
        assert verdict == "UNCERTAIN"
    
    def test_uncertain_low_confidence(self, ensemble):
        
        verdict = ensemble._determine_verdict(0.85, 0.4)
        assert verdict == "UNCERTAIN"

class TestResultAggregation:
    
    
    def test_single_model_aggregation(self, ensemble):
        
        model_results = [{
            "model_name": "heuristic",
            "fake_probability": 0.6,
            "confidence": 0.7,
            "processing_time": 0.01,
            "indicators": {"emotional_language": 0.3},
            "indicator_details": []
        }]
        
        result = ensemble._aggregate_results(model_results)
        
        assert result['prediction'] in ['FAKE', 'REAL', 'UNCERTAIN']
        assert 0 <= result['fake_probability'] <= 1
        assert 'models_used' in result
        assert 'heuristic' in result['models_used']
    
    def test_multiple_model_aggregation(self, ensemble):
        
        model_results = [
            {
                "model_name": "heuristic",
                "fake_probability": 0.8,
                "confidence": 0.7,
                "processing_time": 0.01,
                "indicators": {},
                "indicator_details": []
            },
            {
                "model_name": "huggingface",
                "fake_probability": 0.75,
                "confidence": 0.85,
                "processing_time": 1.0
            }
        ]
        
        result = ensemble._aggregate_results(model_results)
        
        assert 0.7 <= result['fake_probability'] <= 0.85
        assert len(result['models_used']) == 2
    
    def test_empty_results_fallback(self, ensemble):
        
        result = ensemble._aggregate_results([])
        
        assert result['prediction'] == 'UNCERTAIN'
        assert result['fake_probability'] == 0.5
        assert len(result['models_used']) == 0

class TestExplanationGeneration:
    
    
    def test_fake_explanation(self, ensemble):
        
        explanation = ensemble._generate_explanation(
            prediction='FAKE',
            fake_probability=0.85,
            confidence=0.8,
            model_scores=[{"model_name": "heuristic", "fake_probability": 0.85}],
            indicators={"emotional_language": 0.7, "clickbait_patterns": 0.6}
        )
        
        assert "misinformation" in explanation.lower() or "fake" in explanation.lower()
        assert "85%" in explanation
    
    def test_real_explanation(self, ensemble):
        
        explanation = ensemble._generate_explanation(
            prediction='REAL',
            fake_probability=0.15,
            confidence=0.9,
            model_scores=[{"model_name": "heuristic", "fake_probability": 0.15}],
            indicators={}
        )
        
        assert "authentic" in explanation.lower()
    
    def test_explanation_includes_concerns(self, ensemble):
        
        explanation = ensemble._generate_explanation(
            prediction='FAKE',
            fake_probability=0.8,
            confidence=0.75,
            model_scores=[{"model_name": "heuristic", "fake_probability": 0.8}],
            indicators={"emotional_language": 0.7, "clickbait_patterns": 0.8}
        )
        
        assert "concerns" in explanation.lower() or "key" in explanation.lower()

class TestPredictionFlow:
    
    
    @pytest.mark.asyncio
    async def test_predict_returns_result(self, ensemble):
        
        text = "This is a sample news article for testing the prediction system."
        
        result = await ensemble.predict(text)
        
        assert 'prediction' in result
        assert result['prediction'] in ['FAKE', 'REAL', 'UNCERTAIN']
        assert 'fake_probability' in result
        assert 'confidence' in result
        assert 'processing_time' in result
        assert 'models_used' in result
        assert 'heuristic' in result['models_used']
    
    @pytest.mark.asyncio
    async def test_predict_with_suspicious_text(self, ensemble):
        
        text = "SHOCKING!!! You won't BELIEVE what doctors hate!!! EXPOSED!!!"
        
        result = await ensemble.predict(text)
        
        assert result['fake_probability'] >= 0.3

class TestSystemHealth:
    
    
    def test_health_structure(self, ensemble):
        
        health = ensemble.get_system_health()
        
        assert 'overall_status' in health
        assert 'active_models' in health
        assert 'huggingface' in health
        assert 'gemini' in health
        assert 'groq' in health
        assert 'heuristic' in health
    
    def test_heuristic_always_healthy(self, ensemble):
        
        health = ensemble.get_system_health()
        
        assert health['heuristic']['status'] == 'healthy'

class TestWeightedAveraging:
    
    
    def test_weights_applied_correctly(self, ensemble):
        
        model_results = [
            {
                "model_name": "heuristic",
                "fake_probability": 0.0,
                "confidence": 1.0,
                "processing_time": 0.01,
                "indicators": {},
                "indicator_details": []
            },
            {
                "model_name": "huggingface",
                "fake_probability": 1.0,
                "confidence": 1.0,
                "processing_time": 1.0
            }
        ]
        
        result = ensemble._aggregate_results(model_results)
        
        assert 0.5 <= result['fake_probability'] <= 0.7

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
