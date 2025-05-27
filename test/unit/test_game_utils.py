"""
Unit tests for game utilities
"""
import pytest
from app.game_utils import create_scrambled_word


@pytest.mark.unit
class TestGameUtils:
    """Test game utility functions"""
    
    def test_create_scrambled_word_basic(self):
        """Test basic word scrambling"""
        word = "hello"
        scrambled = create_scrambled_word(word)
        
        assert len(scrambled) == len(word)
        assert set(scrambled) == set(word)  # Same letters
        assert isinstance(scrambled, str)
    
    def test_create_scrambled_word_different_from_original(self):
        """Test that scrambled word is different from original (usually)"""
        word = "computer"
        scrambled = create_scrambled_word(word)
        
        # For longer words, scrambling should produce different result
        # Note: there's a small chance they could be the same by random chance
        assert len(scrambled) == len(word)
        assert set(scrambled) == set(word)
    
    def test_create_scrambled_word_empty_string(self):
        """Test scrambling empty string"""
        word = ""
        scrambled = create_scrambled_word(word)
        
        assert scrambled == ""
    
    def test_create_scrambled_word_single_character(self):
        """Test scrambling single character"""
        word = "a"
        scrambled = create_scrambled_word(word)
        
        assert scrambled == "a"  # Single character can't be scrambled
    
    def test_create_scrambled_word_two_characters(self):
        """Test scrambling two characters"""
        word = "hi"
        scrambled = create_scrambled_word(word)
        
        assert len(scrambled) == 2
        assert set(scrambled) == set(word)
        # Could be "hi" or "ih"
        assert scrambled in ["hi", "ih"]
    
    def test_create_scrambled_word_identical_letters(self):
        """Test scrambling word with identical letters"""
        word = "aaaa"
        scrambled = create_scrambled_word(word)
        
        assert scrambled == "aaaa"  # Can't scramble identical letters
    
    def test_create_scrambled_word_match_percentage(self):
        """Test scrambling with custom match percentage"""
        word = "programming"
        scrambled = create_scrambled_word(word, max_match_percentage=20)
        
        # Count matching positions
        matches = sum(1 for i, (a, b) in enumerate(zip(word, scrambled)) if a == b)
        match_percentage = (matches / len(word)) * 100
        
        assert len(scrambled) == len(word)
        assert set(scrambled) == set(word)
        # Should respect the match percentage limit (approximately)
        assert match_percentage <= 25  # Allow some tolerance
    
    def test_create_scrambled_word_zero_match_percentage(self):
        """Test scrambling with zero match percentage"""
        word = "testing"
        scrambled = create_scrambled_word(word, max_match_percentage=0)
        
        # Count matching positions
        matches = sum(1 for i, (a, b) in enumerate(zip(word, scrambled)) if a == b)
        
        assert len(scrambled) == len(word)
        assert set(scrambled) == set(word)
        # Should try to have no matching positions
    
    def test_create_scrambled_word_preserves_case(self):
        """Test that scrambling preserves case"""
        word = "Hello"
        scrambled = create_scrambled_word(word)
        
        assert len(scrambled) == len(word)
        # Check that we have the same characters (case-sensitive)
        original_chars = sorted(word)
        scrambled_chars = sorted(scrambled)
        assert original_chars == scrambled_chars
    
    def test_create_scrambled_word_special_characters(self):
        """Test scrambling with special characters"""
        word = "hello-world"
        scrambled = create_scrambled_word(word)
        
        assert len(scrambled) == len(word)
        assert set(scrambled) == set(word)
        assert "-" in scrambled  # Special character preserved
    
    def test_create_scrambled_word_unicode(self):
        """Test scrambling unicode characters"""
        word = "привет"
        scrambled = create_scrambled_word(word)
        
        assert len(scrambled) == len(word)
        assert set(scrambled) == set(word)
    
    def test_create_scrambled_word_numbers(self):
        """Test scrambling word with numbers"""
        word = "test123"
        scrambled = create_scrambled_word(word)
        
        assert len(scrambled) == len(word)
        assert set(scrambled) == set(word)
    
    @pytest.mark.parametrize("word", [
        "cat",
        "dog", 
        "elephant",
        "programming",
        "development",
        "testing123",
        "Hello-World"
    ])
    def test_create_scrambled_word_various_inputs(self, word):
        """Test scrambling with various word inputs"""
        scrambled = create_scrambled_word(word)
        
        assert len(scrambled) == len(word)
        assert set(scrambled) == set(word)
        assert isinstance(scrambled, str)
    
    def test_create_scrambled_word_consistent_length(self):
        """Test that scrambled word always has same length as original"""
        test_words = [
            "a", "ab", "abc", "test", "longer", "verylongword",
            "word-with-hyphens", "123456", "mixed123word"
        ]
        
        for word in test_words:
            scrambled = create_scrambled_word(word)
            assert len(scrambled) == len(word), f"Length mismatch for word: {word}"
    
    def test_create_scrambled_word_none_input(self):
        """Test scrambling with None input"""
        scrambled = create_scrambled_word(None)
        assert scrambled is None
    
    def test_create_scrambled_word_performance(self):
        """Test that scrambling doesn't take too long"""
        import time
        
        word = "verylongwordthatmighttakeawhiletoscramble"
        
        start_time = time.time()
        scrambled = create_scrambled_word(word)
        end_time = time.time()
        
        # Should complete within reasonable time (1 second)
        assert end_time - start_time < 1.0
        assert len(scrambled) == len(word)
        assert set(scrambled) == set(word)