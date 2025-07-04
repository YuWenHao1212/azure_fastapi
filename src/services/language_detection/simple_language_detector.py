"""
Simplified language detector for Taiwan job descriptions.
Only accepts: Pure Traditional Chinese, Pure English, or Traditional Chinese + English mix.
Rejects all other cases including Simplified Chinese, Japanese, Korean, etc.
"""

import time
import logging
from typing import NamedTuple, Set
from src.services.language_detection.detector import LanguageDetectionService, LanguageDetectionResult
from src.services.exceptions import UnsupportedLanguageError, LanguageDetectionError

logger = logging.getLogger(__name__)


class SimpleLanguageStats(NamedTuple):
    """Language composition statistics."""
    total_chars: int
    traditional_chinese_chars: int
    simplified_chinese_chars: int
    english_chars: int
    other_chars: int
    traditional_chinese_ratio: float
    english_ratio: float
    has_simplified: bool
    has_other_languages: bool


class SimplifiedLanguageDetector(LanguageDetectionService):
    """
    Simplified language detection that only accepts:
    1. Pure Traditional Chinese
    2. Pure English  
    3. Traditional Chinese + English mix
    
    Rejects everything else including Simplified Chinese, Japanese, Korean, etc.
    """
    
    # Threshold for mixed content
    TRADITIONAL_CHINESE_THRESHOLD = 0.20  # 20% threshold
    
    # Common Japanese/Korean characters to detect and reject
    JAPANESE_HIRAGANA_RANGE = ('\u3040', '\u309f')
    JAPANESE_KATAKANA_RANGE = ('\u30a0', '\u30ff')
    KOREAN_HANGUL_RANGE = ('\uac00', '\ud7af')
    
    def analyze_language_composition(self, text: str) -> SimpleLanguageStats:
        """
        Analyze text to determine language composition.
        Focus on detecting Traditional Chinese, English, and unwanted languages.
        """
        if not text:
            return SimpleLanguageStats(0, 0, 0, 0, 0, 0.0, 0.0, False, False)
        
        total_chars = 0
        traditional_chinese_chars = 0
        simplified_chinese_chars = 0
        english_chars = 0
        has_japanese = False
        has_korean = False
        has_other = False
        
        # Convert to set for faster lookup
        text_chars = set(text)
        
        # Check for Simplified Chinese characters
        simplified_found = len(text_chars.intersection(self.SIMPLIFIED_CHARS))
        traditional_found = len(text_chars.intersection(self.TRADITIONAL_CHARS))
        
        # Character-by-character analysis
        for char in text:
            # Skip whitespace and punctuation
            if char.isspace() or not char.isalnum():
                continue
                
            total_chars += 1
            
            # Check for Chinese characters
            if '\u4e00' <= char <= '\u9fff':
                # This is a Chinese character, will be counted in traditional/simplified
                # For simplified detection: characters that are exclusively simplified
                # For traditional detection: characters that appear in traditional or are shared
                
                if char in self.SIMPLIFIED_CHARS:
                    simplified_chinese_chars += 1
                # Count all Chinese characters as traditional for composition analysis
                # (this includes shared characters and traditional-only characters)
                traditional_chinese_chars += 1
            
            # Check for English
            elif char.isalpha() and ord(char) < 128:
                english_chars += 1
            
            # Check for Japanese
            elif (self.JAPANESE_HIRAGANA_RANGE[0] <= char <= self.JAPANESE_HIRAGANA_RANGE[1] or
                  self.JAPANESE_KATAKANA_RANGE[0] <= char <= self.JAPANESE_KATAKANA_RANGE[1]):
                has_japanese = True
            
            # Check for Korean
            elif self.KOREAN_HANGUL_RANGE[0] <= char <= self.KOREAN_HANGUL_RANGE[1]:
                has_korean = True
            
            # Other characters (numbers, symbols are OK, but other scripts are not)
            elif char.isalpha():
                # It's an alphabetic character but not English or Chinese
                has_other = True
        
        # Calculate ratios
        trad_chinese_ratio = traditional_chinese_chars / total_chars if total_chars > 0 else 0.0
        english_ratio = english_chars / total_chars if total_chars > 0 else 0.0
        
        # Determine if we have unwanted content
        # Only reject if simplified chars significantly outnumber traditional chars
        has_simplified = simplified_found > traditional_found and simplified_chinese_chars > 10
        has_other_languages = has_japanese or has_korean or has_other
        
        # Calculate other chars correctly (since we now double-count Chinese chars)
        chinese_chars = sum(1 for char in text if '\u4e00' <= char <= '\u9fff' and not char.isspace())
        other_chars = total_chars - chinese_chars - english_chars
        
        return SimpleLanguageStats(
            total_chars=total_chars,
            traditional_chinese_chars=traditional_chinese_chars,
            simplified_chinese_chars=simplified_chinese_chars,
            english_chars=english_chars,
            other_chars=other_chars,
            traditional_chinese_ratio=trad_chinese_ratio,
            english_ratio=english_ratio,
            has_simplified=has_simplified,
            has_other_languages=has_other_languages
        )
    
    async def detect_language(self, text: str) -> LanguageDetectionResult:
        """
        Detect language with simplified rules:
        - Only accept Pure Traditional Chinese, Pure English, or Trad Chinese + English mix
        - Reject everything else
        """
        start_time = time.time()
        
        try:
            # 1. Text length validation
            if len(text.strip()) < self.MIN_TEXT_LENGTH:
                raise LanguageDetectionError(
                    text_length=len(text.strip()),
                    reason=f"Text too short (minimum {self.MIN_TEXT_LENGTH} characters required)"
                )
            
            # 2. Analyze language composition
            stats = self.analyze_language_composition(text)
            
            logger.info(
                f"Language composition: "
                f"Trad Chinese={stats.traditional_chinese_ratio:.1%} ({stats.traditional_chinese_chars}), "
                f"English={stats.english_ratio:.1%} ({stats.english_chars}), "
                f"Simplified={stats.simplified_chinese_chars}, "
                f"Other={stats.other_chars}"
            )
            
            # 3. Reject if contains simplified Chinese
            if stats.has_simplified:
                logger.warning(f"Rejected: Contains Simplified Chinese ({stats.simplified_chinese_chars} chars)")
                raise UnsupportedLanguageError(
                    detected_language="zh-CN",
                    supported_languages=["en", "zh-TW"],
                    confidence=0.9,
                    user_specified=False
                )
            
            # 4. Reject if contains other languages
            if stats.has_other_languages:
                logger.warning("Rejected: Contains Japanese, Korean, or other non-supported languages")
                # Determine which unsupported language was detected
                detected_lang = "other"
                if stats.other_chars > 0:
                    # Try to identify the specific language
                    for char in text:
                        if self.JAPANESE_HIRAGANA_RANGE[0] <= char <= self.JAPANESE_HIRAGANA_RANGE[1] or \
                           self.JAPANESE_KATAKANA_RANGE[0] <= char <= self.JAPANESE_KATAKANA_RANGE[1]:
                            detected_lang = "ja"
                            break
                        elif self.KOREAN_HANGUL_RANGE[0] <= char <= self.KOREAN_HANGUL_RANGE[1]:
                            detected_lang = "ko"
                            break
                
                raise UnsupportedLanguageError(
                    detected_language=detected_lang,
                    supported_languages=["en", "zh-TW"],
                    confidence=0.9,
                    user_specified=False
                )
            
            # 5. Determine language based on composition
            total_valid_chars = stats.traditional_chinese_chars + stats.english_chars
            
            if total_valid_chars == 0:
                # No valid content
                raise LanguageDetectionError(
                    text_length=len(text),
                    reason="No valid Traditional Chinese or English content found"
                )
            
            # Calculate ratios based on valid characters only
            trad_chinese_ratio = stats.traditional_chinese_chars / total_valid_chars
            english_ratio = stats.english_chars / total_valid_chars
            
            # 6. Determine language
            if trad_chinese_ratio >= 0.95:
                # Pure Traditional Chinese (95%+ Traditional Chinese)
                detected_lang = 'zh-TW'
                confidence = 0.95
                logger.info(f"Detected: Pure Traditional Chinese ({trad_chinese_ratio:.1%})")
            
            elif english_ratio >= 0.95:
                # Pure English (95%+ English)
                detected_lang = 'en'
                confidence = 0.95
                logger.info(f"Detected: Pure English ({english_ratio:.1%})")
            
            elif trad_chinese_ratio > 0 and english_ratio > 0:
                # Mixed Traditional Chinese + English
                if trad_chinese_ratio >= self.TRADITIONAL_CHINESE_THRESHOLD:
                    # Traditional Chinese >= 20%, use Traditional Chinese prompt
                    detected_lang = 'zh-TW'
                    confidence = 0.9
                    logger.info(
                        f"Detected: Mixed content with {trad_chinese_ratio:.1%} Traditional Chinese "
                        f"(>= 20%), using zh-TW"
                    )
                else:
                    # Traditional Chinese < 20%, use English prompt
                    detected_lang = 'en'
                    confidence = 0.9
                    logger.info(
                        f"Detected: Mixed content with {trad_chinese_ratio:.1%} Traditional Chinese "
                        f"(< 20%), using en"
                    )
            else:
                # Shouldn't reach here, but handle edge case
                detected_lang = 'en' if english_ratio > trad_chinese_ratio else 'zh-TW'
                confidence = 0.8
            
            detection_time_ms = int((time.time() - start_time) * 1000)
            
            return LanguageDetectionResult(
                language=detected_lang,
                confidence=confidence,
                is_supported=True,
                detection_time_ms=detection_time_ms
            )
            
        except (LanguageDetectionError, UnsupportedLanguageError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            logger.error(f"Unexpected error in language detection: {str(e)}")
            raise LanguageDetectionError(
                text_length=len(text) if text else 0,
                reason=f"Unexpected detection error: {str(e)}"
            )