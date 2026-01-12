

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.heuristic import HeuristicAnalyzer

@pytest.fixture
def analyzer():
    
    return HeuristicAnalyzer()

class TestEmotionalLanguage:
    
    
    def test_neutral_text(self, analyzer):
        
        text = "The company announced quarterly earnings today. Revenue increased by 5%."
        result = analyzer.analyze(text)
        
        assert result['indicators']['emotional_language'] < 0.3
        assert result['fake_probability'] < 0.5
    
    def test_highly_emotional_text(self, analyzer):
        
        text = "SHOCKING! This UNBELIEVABLE scandal reveals the DEVASTATING truth!"
        result = analyzer.analyze(text)
        
        assert result['indicators']['emotional_language'] >= 0.2
    
    def test_mixed_emotional_text(self, analyzer):
        
        text = "In a surprising turn of events, the amazing discovery was announced."
        result = analyzer.analyze(text)
        
        assert 'emotional_language' in result['indicators']

class TestClickbaitPatterns:
    
    
    def test_no_clickbait(self, analyzer):
        
        text = "The government announced new policies for the upcoming fiscal year."
        result = analyzer.analyze(text)
        
        assert result['indicators']['clickbait_patterns'] == 0.0
    
    def test_clickbait_detected(self, analyzer):
        
        text = "You won't believe what happened next! Doctors hate this one simple trick!"
        result = analyzer.analyze(text)
        
        assert result['indicators']['clickbait_patterns'] >= 0.4
    
    def test_multiple_clickbait_patterns(self, analyzer):
        
        text = "BREAKING: The truth about this secret they don't want you to know! Must see!"
        result = analyzer.analyze(text)
        
        assert result['indicators']['clickbait_patterns'] >= 0.4

class TestPunctuation:
    
    
    def test_normal_punctuation(self, analyzer):
        
        text = "This is a normal sentence. Here is another one. And a question?"
        result = analyzer.analyze(text)
        
        assert result['indicators']['excessive_punctuation'] < 0.5
    
    def test_excessive_exclamation(self, analyzer):
        
        text = "This is amazing!!! You have to see this!!!! Incredible!!!!"
        result = analyzer.analyze(text)
        
        assert result['indicators']['excessive_punctuation'] >= 0.3
    
    def test_repeated_punctuation(self, analyzer):
        
        text = "What??? How is this possible?!?! This is crazy!!!"
        result = analyzer.analyze(text)
        
        assert result['indicators']['excessive_punctuation'] >= 0.3

class TestCapsRatio:
    
    
    def test_normal_caps(self, analyzer):
        
        text = "The President announced new measures. Congress is expected to vote soon."
        result = analyzer.analyze(text)
        
        assert result['indicators']['caps_ratio'] < 0.5
    
    def test_excessive_caps(self, analyzer):
        
        text = "THIS IS ALL CAPS TEXT THAT SHOULD BE DETECTED AS SUSPICIOUS"
        result = analyzer.analyze(text)
        
        assert result['indicators']['caps_ratio'] >= 0.7
    
    def test_mixed_caps(self, analyzer):
        
        text = "BREAKING NEWS: Important announcement from the White House today."
        result = analyzer.analyze(text)
        
        assert result['indicators']['caps_ratio'] > 0

class TestOverallAnalysis:
    
    
    def test_result_structure(self, analyzer):
        
        text = "Sample news article text for testing."
        result = analyzer.analyze(text)
        
        assert 'model_name' in result
        assert result['model_name'] == 'heuristic'
        assert 'fake_probability' in result
        assert 'confidence' in result
        assert 'processing_time' in result
        assert 'indicators' in result
        assert 'indicator_details' in result
    
    def test_probability_range(self, analyzer):
        
        texts = [
            "Normal news article text.",
            "SHOCKING UNBELIEVABLE NEWS!!!",
            "You won't believe what doctors found!"
        ]
        
        for text in texts:
            result = analyzer.analyze(text)
            assert 0.0 <= result['fake_probability'] <= 1.0
            assert 0.0 <= result['confidence'] <= 1.0
    
    def test_empty_text(self, analyzer):
        
        result = analyzer.analyze("")
        
        assert result['fake_probability'] == 0.0
        assert result['confidence'] == 0.0
    
    def test_whitespace_only(self, analyzer):
        
        result = analyzer.analyze("   \n\t   ")
        
        assert result['fake_probability'] == 0.0
    
    def test_indicator_details_structure(self, analyzer):
        
        text = "Sample article with some shocking claims!"
        result = analyzer.analyze(text)
        
        for detail in result['indicator_details']:
            assert 'name' in detail
            assert 'score' in detail
            assert 'severity' in detail
            assert 'description' in detail

class TestSeverityLevels:
    
    
    def test_low_severity(self, analyzer):
        
        text = "The weather forecast indicates rain tomorrow."
        result = analyzer.analyze(text)
        
        severities = [d['severity'] for d in result['indicator_details']]
        assert 'LOW' in severities
    
    def test_high_severity_detection(self, analyzer):
        
        text = "SHOCKING!!! UNBELIEVABLE NEWS that doctors hate - you won't believe this!!!"
        result = analyzer.analyze(text)
        
        severities = [d['severity'] for d in result['indicator_details']]
        assert 'HIGH' in severities or 'MEDIUM' in severities

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
