"""
STT Text Pre-Processor for LLM Integration
Production-ready controller layer for cleaning Speech-to-Text output before LLM processing.
English-only support with internal default configuration.
"""

import re
import logging
from typing import List
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class ProcessingStep(ABC):
    """Abstract base class for text processing pipeline steps."""
    
    @abstractmethod
    def process(self, text: str) -> str:
        """
        Process text and return transformed result.
        
        Args:
            text: Input text to process
            
        Returns:
            Processed text
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of this processing step."""
        pass


class WhitespaceNormalizationStep(ProcessingStep):
    """Normalizes all whitespace to single spaces and trims edges."""
    
    @property
    def name(self) -> str:
        return "WhitespaceNormalization"
    
    def process(self, text: str) -> str:
        """Normalize whitespace in text."""
        if not text:
            return text
        
        text = re.sub(r'[\t\n\r]+', ' ', text)
        text = re.sub(r' +', ' ', text)
        return text.strip()


class STTArtifactRemovalStep(ProcessingStep):
    """Removes Speech-to-Text artifacts and noise markers."""
    
    def __init__(self):
        self.artifact_patterns = [
            r'\[inaudible\]',
            r'\[silence\]',
            r'\[noise\]',
            r'\[music\]',
            r'\[laughter\]',
            r'\[applause\]',
            r'\[crosstalk\]',
            r'\[background noise\]',
            r'\[background\]',
            r'<unk>',
            r'<UNK>',
            r'\*\*\*+',
            r'___+',
            r'---+',
        ]
        self.compiled_patterns = [re.compile(p, re.IGNORECASE) for p in self.artifact_patterns]
    
    @property
    def name(self) -> str:
        return "STTArtifactRemoval"
    
    def process(self, text: str) -> str:
        """Remove STT artifacts from text."""
        if not text:
            return text
        
        for pattern in self.compiled_patterns:
            text = pattern.sub('', text)
        
        text = re.sub(r' +', ' ', text)
        return text.strip()


class FillerWordRemovalStep(ProcessingStep):
    """Removes English filler words and verbal hesitations."""
    
    def __init__(self):
        self.standalone_fillers = {
            'um', 'umm', 'ummm',
            'uh', 'uhh', 'uhhh',
            'er', 'err', 'errm',
            'ah', 'ahh', 'ahhh',
            'hmm', 'hmmm', 'mmm', 'mmmm',
            'mhm', 'uh-huh', 'mm-hmm', 'uh huh',
            'huh', 'eh', 'ohh', 'ooh',
        }
        
        self.multi_word_fillers = [
            'you know',
            'i mean',
            'sort of',
            'kind of',
            'you see',
            'like you know',
        ]
        
        self.multi_word_fillers.sort(key=lambda x: len(x.split()), reverse=True)
    
    @property
    def name(self) -> str:
        return "FillerWordRemoval"
    
    def process(self, text: str) -> str:
        """Remove filler words from text."""
        if not text:
            return text
        
        words = text.split()
        if not words:
            return text
        
        result = []
        i = 0
        
        while i < len(words):
            matched = False
            
            for phrase in self.multi_word_fillers:
                phrase_words = phrase.split()
                phrase_len = len(phrase_words)
                
                if i + phrase_len <= len(words):
                    candidate = ' '.join(words[i:i + phrase_len])
                    candidate_clean = re.sub(r'[^\w\s]', '', candidate).lower()
                    phrase_clean = re.sub(r'[^\w\s]', '', phrase).lower()
                    
                    if candidate_clean == phrase_clean:
                        i += phrase_len
                        matched = True
                        break
            
            if matched:
                continue
            
            current_word_clean = re.sub(r'[^\w]', '', words[i]).lower()
            
            if current_word_clean in self.standalone_fillers:
                i += 1
                continue
            
            result.append(words[i])
            i += 1
        
        return ' '.join(result)


class RepeatedWordRemovalStep(ProcessingStep):
    """Removes consecutive repeated words caused by STT stuttering."""
    
    @property
    def name(self) -> str:
        return "RepeatedWordRemoval"
    
    def process(self, text: str) -> str:
        """Remove consecutive repeated words."""
        if not text:
            return text
        
        words = text.split()
        if len(words) <= 1:
            return text
        
        result = [words[0]]
        
        for i in range(1, len(words)):
            current_normalized = self._normalize_word(words[i])
            previous_normalized = self._normalize_word(words[i - 1])
            
            if not current_normalized:
                result.append(words[i])
                continue
            
            if current_normalized != previous_normalized:
                result.append(words[i])
        
        return ' '.join(result)
    
    def _normalize_word(self, word: str) -> str:
        """Normalize word for comparison."""
        normalized = re.sub(r'[^\w]', '', word).lower()
        return normalized


class ExcessDeterminerRemovalStep(ProcessingStep):
    """Removes unnecessary, hanging, or isolated determiners with intelligent context awareness."""
    
    def __init__(self):
        self.determiners = {'the', 'a', 'an'}
        
        self.non_noun_words = {
            'is', 'are', 'was', 'were', 'am', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'should', 'could', 'can', 'may', 'might', 'must',
            'and', 'or', 'but', 'so', 'because', 'if', 'when', 'where',
            'um', 'uh', 'er', 'ah', 'hmm',
            'not', 'no', 'yes',
        }
        
        self.verbs = {
            'is', 'are', 'was', 'were', 'am', 'be', 'been', 'being',
            'have', 'has', 'had', 'having',
            'do', 'does', 'did', 'doing', 'done',
            'go', 'goes', 'went', 'going', 'gone',
            'get', 'gets', 'got', 'getting', 'gotten',
            'make', 'makes', 'made', 'making',
            'take', 'takes', 'took', 'taking', 'taken',
            'see', 'sees', 'saw', 'seeing', 'seen',
            'come', 'comes', 'came', 'coming',
            'want', 'wants', 'wanted', 'wanting',
            'need', 'needs', 'needed', 'needing',
            'think', 'thinks', 'thought', 'thinking',
            'know', 'knows', 'knew', 'knowing', 'known',
            'find', 'finds', 'found', 'finding',
            'give', 'gives', 'gave', 'giving', 'given',
            'tell', 'tells', 'told', 'telling',
            'work', 'works', 'worked', 'working',
            'call', 'calls', 'called', 'calling',
            'try', 'tries', 'tried', 'trying',
            'ask', 'asks', 'asked', 'asking',
            'feel', 'feels', 'felt', 'feeling',
            'leave', 'leaves', 'left', 'leaving',
            'put', 'puts', 'putting',
        }
    
    @property
    def name(self) -> str:
        return "ExcessDeterminerRemoval"
    
    def process(self, text: str) -> str:
        """Remove excess or hanging determiners with intelligent context analysis."""
        if not text:
            return text
        
        words = text.split()
        if len(words) <= 1:
            if words and words[0].lower().strip('.,!?;:\'"') in self.determiners:
                return ""
            return text
        
        result = []
        
        for i, word in enumerate(words):
            word_lower = word.lower().strip('.,!?;:\'"')
            
            if word_lower in self.determiners:
                should_remove = False
                
                if i == len(words) - 1:
                    should_remove = True
                    logger.debug(f"Removing trailing determiner: '{word}'")
                
                elif i < len(words) - 1:
                    next_word_lower = words[i + 1].lower().strip('.,!?;:\'"')
                    
                    if next_word_lower in self.determiners:
                        should_remove = True
                        logger.debug(f"Removing determiner before another determiner: '{word}' -> '{next_word_lower}'")
                    
                    elif next_word_lower in self.non_noun_words:
                        should_remove = True
                        logger.debug(f"Removing determiner before non-noun word: '{word}' -> '{next_word_lower}'")
                    
                    elif not next_word_lower:
                        should_remove = True
                        logger.debug(f"Removing determiner before empty/punctuation: '{word}'")
                
                if i == 0 and len(words) >= 2:
                    first_word_lower = word_lower
                    second_word_lower = words[1].lower().strip('.,!?;:\'"')
                    
                    if first_word_lower in self.determiners and second_word_lower in self.verbs:
                        should_remove = True
                        logger.debug(f"Removing leading determiner before verb: '{word}' -> '{words[1]}'")
                    
                    elif first_word_lower in self.determiners and second_word_lower in self.determiners:
                        should_remove = True
                        logger.debug(f"Removing first of consecutive determiners at start: '{word}' -> '{words[1]}'")
                
                if not should_remove:
                    result.append(word)
            else:
                result.append(word)
        
        final_result = []
        for i, word in enumerate(result):
            word_lower = word.lower().strip('.,!?;:\'"')
            
            if word_lower in self.determiners:
                if i == 0 and len(result) == 1:
                    logger.debug(f"Removing standalone determiner: '{word}'")
                    continue
                
                if i == len(result) - 1:
                    logger.debug(f"Removing final trailing determiner: '{word}'")
                    continue
            
            final_result.append(word)
        
        return ' '.join(final_result)


class SpellingCorrectionStep(ProcessingStep):
    """Corrects spelling errors using lightweight dictionary-based correction."""
    
    def __init__(self):
        self.spellchecker = None
        self._initialize_spellchecker()
    
    def _initialize_spellchecker(self):
        """Initialize spell checker."""
        try:
            from spellchecker import SpellChecker
            self.spellchecker = SpellChecker(language='en', distance=2)
            logger.debug("Spell checker initialized successfully")
        except ImportError:
            logger.warning("spellchecker library not installed. Spelling correction disabled.")
            self.spellchecker = None
        except Exception as e:
            logger.error(f"Failed to initialize spell checker: {e}")
            self.spellchecker = None
    
    @property
    def name(self) -> str:
        return "SpellingCorrection"
    
    def process(self, text: str) -> str:
        """Correct spelling errors in text."""
        if not text or not self.spellchecker:
            return text
        
        tokens = self._tokenize(text)
        corrected_tokens = []
        
        for token in tokens:
            if self._is_correctable_word(token):
                corrected = self._correct_word(token)
                corrected_tokens.append(corrected)
            else:
                corrected_tokens.append(token)
        
        return self._reconstruct_text(corrected_tokens)
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words and punctuation."""
        pattern = r"\w+(?:'\w+)?|[^\w\s]"
        tokens = re.findall(pattern, text)
        return tokens
    
    def _is_correctable_word(self, token: str) -> bool:
        """Check if token should be spell-checked."""
        if not token or len(token) <= 1:
            return False
        
        if re.match(r'^\d+$', token):
            return False
        
        if re.match(r'^[^\w]+$', token):
            return False
        
        if not re.search(r'[a-zA-Z]', token):
            return False
        
        if token.isupper() and len(token) <= 5:
            return False
        
        if token[0].isupper() and len(token) >= 2 and token[1:].islower():
            return False
        
        return True
    
    def _correct_word(self, word: str) -> str:
        """Correct a single word while preserving case."""
        lower_word = word.lower()
        corrected_lower = self.spellchecker.correction(lower_word)
        
        if not corrected_lower or corrected_lower == lower_word:
            return word
        
        if word.isupper():
            return corrected_lower.upper()
        elif word[0].isupper():
            return corrected_lower.capitalize()
        else:
            return corrected_lower
    
    def _reconstruct_text(self, tokens: List[str]) -> str:
        """Reconstruct text from tokens with proper spacing."""
        if not tokens:
            return ""
        
        result = []
        for i, token in enumerate(tokens):
            if i == 0:
                result.append(token)
            elif re.match(r'^[.,!?;:\)\]}]$', token):
                result.append(token)
            elif re.match(r'^[\(\[{]$', token):
                if i > 0:
                    result.append(' ')
                result.append(token)
            elif token == "'" and i > 0 and i < len(tokens) - 1:
                prev_token = tokens[i - 1]
                if prev_token and prev_token[-1].isalpha():
                    result.append(token)
                else:
                    result.append(' ')
                    result.append(token)
            else:
                result.append(' ')
                result.append(token)
        
        return ''.join(result)


class PunctuationRestorationStep(ProcessingStep):
    """Restores punctuation and capitalization to unpunctuated STT output."""
    
    def __init__(self):
        self.question_starters = {
            'what', 'where', 'when', 'why', 'who', 'whom', 'whose',
            'how', 'which', 'can', 'could', 'would', 'should',
            'will', 'shall', 'may', 'might', 'must',
            'is', 'are', 'was', 'were', 'am',
            'do', 'does', 'did', 'have', 'has', 'had',
        }
        
        self.sentence_connectors = {
            'and', 'but', 'or', 'so', 'because', 'however',
            'therefore', 'moreover', 'furthermore', 'additionally',
            'meanwhile', 'nevertheless', 'although', 'though',
        }
        
        self.min_words_for_sentence = 3
        self.max_words_per_sentence = 25
        self.optimal_words_per_sentence = 15
    
    @property
    def name(self) -> str:
        return "PunctuationRestoration"
    
    def process(self, text: str) -> str:
        """Restore punctuation and capitalization to text."""
        if not text:
            return text
        
        text = text.strip()
        
        if self._has_sentence_punctuation(text):
            return self._capitalize_sentences(text)
        
        sentences = self._segment_into_sentences(text)
        
        if not sentences:
            return text
        
        punctuated_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            words = sentence.split()
            
            if len(words) == 1:
                punctuated_sentences.append(sentence)
                continue
            
            if len(words) < self.min_words_for_sentence:
                punctuated_sentences.append(sentence)
                continue
            
            sentence = self._capitalize_first_letter(sentence)
            sentence = self._add_terminal_punctuation(sentence, words)
            punctuated_sentences.append(sentence)
        
        return ' '.join(punctuated_sentences)
    
    def _has_sentence_punctuation(self, text: str) -> bool:
        """Check if text already has sentence-ending punctuation."""
        return bool(re.search(r'[.!?]', text))
    
    def _capitalize_sentences(self, text: str) -> str:
        """Capitalize first letter of each sentence."""
        sentences = re.split(r'([.!?]+\s+)', text)
        result = []
        
        for i, segment in enumerate(sentences):
            if i % 2 == 0 and segment.strip():
                segment = self._capitalize_first_letter(segment.strip())
                result.append(segment)
            else:
                result.append(segment)
        
        return ''.join(result)
    
    def _capitalize_first_letter(self, text: str) -> str:
        """Capitalize the first alphabetic character in text."""
        for i, char in enumerate(text):
            if char.isalpha():
                return text[:i] + char.upper() + text[i + 1:]
        return text
    
    def _segment_into_sentences(self, text: str) -> List[str]:
        """Segment unpunctuated text into sentences."""
        words = text.split()
        
        if len(words) <= self.optimal_words_per_sentence:
            return [text]
        
        sentences = []
        current_sentence_words = []
        word_count = 0
        
        for i, word in enumerate(words):
            current_sentence_words.append(word)
            word_count += 1
            
            should_break = False
            
            if word_count >= self.max_words_per_sentence:
                should_break = True
            elif word_count >= self.optimal_words_per_sentence:
                word_lower = word.lower().strip('.,!?;:')
                if word_lower in self.sentence_connectors:
                    should_break = True
            
            if should_break:
                sentences.append(' '.join(current_sentence_words))
                current_sentence_words = []
                word_count = 0
        
        if current_sentence_words:
            sentences.append(' '.join(current_sentence_words))
        
        return sentences
    
    def _add_terminal_punctuation(self, sentence: str, words: List[str]) -> str:
        """Add appropriate terminal punctuation to sentence."""
        sentence = sentence.rstrip('.,!?;:')
        
        first_word = words[0].lower().strip('.,!?;:\'"')
        
        if first_word in self.question_starters:
            return sentence + '?'
        else:
            return sentence + '.'


class FinalPolishingStep(ProcessingStep):
    """Final polishing: spacing, duplicate punctuation removal, and trimming."""
    
    @property
    def name(self) -> str:
        return "FinalPolishing"
    
    def process(self, text: str) -> str:
        """Apply final polishing to text."""
        if not text:
            return text
        
        text = re.sub(r'\s+([.,!?;:])', r'\1', text)
        
        text = re.sub(r'([.,!?;:])\1+', r'\1', text)
        
        text = re.sub(r'([.!?])\s*([.!?])', r'\1', text)
        
        text = re.sub(r' +', ' ', text)
        
        text = re.sub(r'([.!?])\s+([.,!?])', r'\1', text)
        
        text = text.strip()
        
        if text and text[-1] not in '.!?' and len(text.split()) >= 3:
            text += '.'
        
        return text


class TextProcessor:
    """
    Pipeline-based text processor for STT post-processing.
    
    Orchestrates multiple processing steps to transform raw Speech-to-Text
    output into clean, properly formatted text suitable for LLM consumption.
    """
    
    def __init__(self):
        """Initialize text processor with default pipeline."""
        self.pipeline: List[ProcessingStep] = self._build_pipeline()
        logger.info(f"TextProcessor initialized with {len(self.pipeline)} steps")
    
    def _build_pipeline(self) -> List[ProcessingStep]:
        """Build the default processing pipeline."""
        pipeline = [
            WhitespaceNormalizationStep(),
            STTArtifactRemovalStep(),
            FillerWordRemovalStep(),
            RepeatedWordRemovalStep(),
            ExcessDeterminerRemovalStep(),
            SpellingCorrectionStep(),
            PunctuationRestorationStep(),
            FinalPolishingStep(),
        ]
        
        step_names = [step.name for step in pipeline]
        logger.debug(f"Pipeline steps: {step_names}")
        
        return pipeline
    
    def process(self, text: str) -> str:
        """
        Process text through the complete pipeline.
        
        Args:
            text: Raw Speech-to-Text output
            
        Returns:
            Cleaned and formatted text ready for LLM
        """
        if not text or not text.strip():
            return ""
        
        processed_text = text
        
        for step in self.pipeline:
            try:
                before = processed_text
                processed_text = step.process(processed_text)
                
                if logger.isEnabledFor(logging.DEBUG):
                    if before != processed_text:
                        logger.debug(f"{step.name}: '{before[:60]}...' -> '{processed_text[:60]}...'")
                    else:
                        logger.debug(f"{step.name}: No changes")
                        
            except Exception as e:
                logger.error(f"Error in {step.name}: {e}", exc_info=True)
                continue
        
        return processed_text


_processor_instance: TextProcessor = None


def _get_processor() -> TextProcessor:
    """Get or create singleton TextProcessor instance."""
    global _processor_instance
    
    if _processor_instance is None:
        _processor_instance = TextProcessor()
    
    return _processor_instance


def preprocess_before_llm(text: str) -> str:
    """
    Preprocess Speech-to-Text output before sending to LLM.
    
    This is the main controller function that cleans and normalizes
    raw STT output through a comprehensive processing pipeline.
    
    Processing pipeline:
    1. Whitespace normalization
    2. STT artifact removal
    3. Filler word removal
    4. Repeated word removal
    5. Excess determiner removal (intelligent context-aware)
    6. Spelling correction
    7. Punctuation restoration
    8. Final polishing
    
    Args:
        text: Raw text output from Speech-to-Text system
        
    Returns:
        Cleaned and properly formatted text ready for LLM processing
        
    Examples:
        >>> preprocess_before_llm("um the the meeting is is scheduled for uh tomorrow")
        'The meeting is scheduled for tomorrow.'
        
        >>> preprocess_before_llm("where is is the the nearest cafe you know")
        'Where is the nearest cafe?'
        
        >>> preprocess_before_llm("the")
        ''
        
        >>> preprocess_before_llm("the is ready")
        'Is ready.'
    """
    processor = _get_processor()
    return processor.process(text)


# if __name__ == "__main__":
#     logging.basicConfig(
#         level=logging.INFO,
#         format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
#     )
    
#     print("=" * 100)
#     print("STT PRE-PROCESSOR FOR LLM - PRODUCTION CONTROLLER LAYER")
#     print("=" * 100)
#     print()
    
#     test_cases = [
#         "um the the meeting is is scheduled for uh tomorrow",
#         "where is the the nearest cafe um i mean coffee shop",
#         "what time is is the meeting uh scheduled for tomorrow",
#         "okay so basically we need to finalize the the report by friday right",
#         "how do i um you know configure the the settings properly",
#         "the project deadline is is next week we we need to finish testing",
#         "can you you help me with this issue im having trouble understanding",
#         "uh basically the system is designed to handle multiple requests simultaneously",
#         "what are are the the main features of of the new new product",
#         "i mean the the performance has improved significantly over the last quarter you know",
#         "um where where can i find the the documentation for this this api",
#         "the team team needs to collaborate more effectively on this this initiative",
#         "is is the the report ready for for submission",
#         "we we should should probably uh discuss this this with the the team you know",
#         "hanging determiner test the the the",
#         "single word test hello",
#         "two words only",
#         "the",
#         "a meeting",
#         "schedule the the",
#         "the is ready",
#         "the was done yesterday",
#         "meeting the the",
#         "the the the",
#         "a a a",
#         "the meeting the",
#         "the are important",
#         "the will happen tomorrow",
#     ]
    
#     for i, raw_stt in enumerate(test_cases, 1):
#         cleaned = preprocess_before_llm(raw_stt)
        
#         print(f"Example {i}:")
#         print(f"  INPUT:  {raw_stt}")
#         print(f"  OUTPUT: {cleaned}")
#         print()
    
#     print("=" * 100)
#     print("STRESS TEST - LONG UTTERANCE WITH MULTIPLE ISSUES")
#     print("=" * 100)
#     print()
    
#     long_utterance = (
#         "um so like basically what what i wanted to to say is that uh the the system "
#         "performance has has been really really good lately you know and and we we "
#         "should probably uh keep monitoring it it closely but but overall i i think "
#         "the the team has done done a a great job you know i mean considering all all "
#         "the the challenges we we faced um yeah the the"
#     )
    
#     cleaned_long = preprocess_before_llm(long_utterance)
    
#     print(f"INPUT:\n{long_utterance}")
#     print()
#     print(f"OUTPUT:\n{cleaned_long}")
#     print()
    
#     print("=" * 100)