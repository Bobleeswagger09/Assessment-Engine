import re
import math
from typing import Dict, List, Tuple
from collections import Counter
from abc import ABC, abstractmethod


class GradingStrategy(ABC):
    """Abstract base class for grading strategies"""
    
    @abstractmethod
    def grade(self, student_answer: str, expected_answer: str, 
              max_marks: float, rubric: Dict = None) -> Tuple[float, str, Dict]:
        pass


class KeywordMatchingGrader(GradingStrategy):
    """Grades based on keyword matching and density"""
    
    def grade(self, student_answer: str, expected_answer: str, 
              max_marks: float, rubric: Dict = None) -> Tuple[float, str, Dict]:
        
        keywords = self._extract_keywords(expected_answer)
        student_lower = student_answer.lower()
        matched_keywords = []
        missed_keywords = []
        
        for keyword in keywords:
            if keyword.lower() in student_lower:
                matched_keywords.append(keyword)
            else:
                missed_keywords.append(keyword)
        
        if len(keywords) > 0:
            match_percentage = len(matched_keywords) / len(keywords)
        else:
            match_percentage = 0.5
        
        min_words = 10
        word_count = len(student_answer.split())
        length_factor = min(1.0, word_count / min_words) if word_count < min_words else 1.0
        
        final_score = max_marks * match_percentage * length_factor
        
        feedback = self._generate_feedback(
            matched_keywords, missed_keywords, word_count, min_words
        )
        
        grading_details = {
            'strategy': 'keyword_matching',
            'matched_keywords': matched_keywords,
            'missed_keywords': missed_keywords,
            'match_percentage': round(match_percentage * 100, 2),
            'word_count': word_count,
            'length_factor': round(length_factor, 2)
        }
        
        return round(final_score, 2), feedback, grading_details
    
    def _extract_keywords(self, text: str) -> List[str]:
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'
        }
        
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        keywords = [w for w in words if w not in stop_words]
        
        return list(set(keywords))
    
    def _generate_feedback(self, matched: List[str], missed: List[str], 
                          word_count: int, min_words: int) -> str:
        feedback_parts = []
        
        if len(matched) > 0:
            feedback_parts.append(f"Good coverage of key concepts: {', '.join(matched[:5])}")
        
        if len(missed) > 0:
            feedback_parts.append(f"Consider including: {', '.join(missed[:3])}")
        
        if word_count < min_words:
            feedback_parts.append(f"Answer could be more detailed")
        
        return ". ".join(feedback_parts) if feedback_parts else "Answer reviewed."


class CosineSimilarityGrader(GradingStrategy):
    """Grades using TF-IDF and cosine similarity"""
    
    def grade(self, student_answer: str, expected_answer: str, 
              max_marks: float, rubric: Dict = None) -> Tuple[float, str, Dict]:
        
        student_tokens = self._tokenize(student_answer)
        expected_tokens = self._tokenize(expected_answer)
        
        student_vector = self._compute_tfidf(student_tokens, [student_tokens, expected_tokens])
        expected_vector = self._compute_tfidf(expected_tokens, [student_tokens, expected_tokens])
        
        similarity = self._cosine_similarity(student_vector, expected_vector)
        
        adjusted_similarity = math.sqrt(similarity)
        score = max_marks * adjusted_similarity
        
        feedback = self._generate_similarity_feedback(similarity)
        
        grading_details = {
            'strategy': 'cosine_similarity',
            'similarity_score': round(similarity, 4),
            'adjusted_similarity': round(adjusted_similarity, 4),
            'student_word_count': len(student_tokens),
            'expected_word_count': len(expected_tokens)
        }
        
        return round(score, 2), feedback, grading_details
    
    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b[a-zA-Z]+\b', text.lower())
    
    def _compute_tfidf(self, tokens: List[str], all_documents: List[List[str]]) -> Dict[str, float]:
        tf = Counter(tokens)
        total_terms = len(tokens)
        
        idf = {}
        for term in set(tokens):
            doc_count = sum(1 for doc in all_documents if term in doc)
            idf[term] = math.log(len(all_documents) / (doc_count + 1))
        
        tfidf = {}
        for term, freq in tf.items():
            tfidf[term] = (freq / total_terms) * idf.get(term, 0)
        
        return tfidf
    
    def _cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        all_terms = set(vec1.keys()) | set(vec2.keys())
        
        if not all_terms:
            return 0.0
        
        dot_product = sum(vec1.get(term, 0) * vec2.get(term, 0) for term in all_terms)
        
        mag1 = math.sqrt(sum(val ** 2 for val in vec1.values()))
        mag2 = math.sqrt(sum(val ** 2 for val in vec2.values()))
        
        if mag1 == 0 or mag2 == 0:
            return 0.0
        
        return dot_product / (mag1 * mag2)
    
    def _generate_similarity_feedback(self, similarity: float) -> str:
        if similarity >= 0.8:
            return "Excellent answer with strong alignment to expected content."
        elif similarity >= 0.6:
            return "Good answer, captures most key points."
        elif similarity >= 0.4:
            return "Adequate answer, but could be more comprehensive."
        else:
            return "Answer needs improvement. Review the question carefully."


class MCQGrader(GradingStrategy):
    """Grades multiple choice questions"""
    
    def grade(self, student_answer: str, expected_answer: str, 
              max_marks: float, rubric: Dict = None) -> Tuple[float, str, Dict]:
        
        student_answer = student_answer.strip().lower()
        expected_answer = expected_answer.strip().lower()
        
        is_correct = student_answer == expected_answer
        score = max_marks if is_correct else 0
        
        feedback = "Correct!" if is_correct else f"Incorrect. Expected: {expected_answer}"
        
        grading_details = {
            'strategy': 'mcq',
            'is_correct': is_correct,
            'student_answer': student_answer,
            'expected_answer': expected_answer
        }
        
        return score, feedback, grading_details


class GradingService:
    """Main service for grading student submissions"""
    
    def __init__(self):
        self.strategies = {
            'mcq': MCQGrader(),
            'true_false': MCQGrader(),
            'short_answer': KeywordMatchingGrader(),
            'essay': CosineSimilarityGrader(),
        }
    
    def grade_answer(self, question_type: str, student_answer: str, 
                     expected_answer: str, max_marks: float, 
                     rubric: Dict = None) -> Tuple[float, str, Dict]:
        strategy = self.strategies.get(question_type, KeywordMatchingGrader())
        return strategy.grade(student_answer, expected_answer, max_marks, rubric)
    
    def grade_submission(self, submission_data: List[Dict]) -> Dict:
        total_score = 0.0
        max_score = 0.0
        detailed_results = []
        
        for item in submission_data:
            score, feedback, details = self.grade_answer(
                question_type=item['question_type'],
                student_answer=item['student_answer'],
                expected_answer=item['expected_answer'],
                max_marks=item['max_marks'],
                rubric=item.get('rubric')
            )
            
            total_score += score
            max_score += item['max_marks']
            
            detailed_results.append({
                'question_id': item.get('question_id'),
                'score': score,
                'max_marks': item['max_marks'],
                'feedback': feedback,
                'grading_details': details
            })
        
        percentage = (total_score / max_score * 100) if max_score > 0 else 0
        
        return {
            'total_score': round(total_score, 2),
            'max_score': round(max_score, 2),
            'percentage': round(percentage, 2),
            'detailed_results': detailed_results
        }