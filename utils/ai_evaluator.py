import openai
from config.settings import settings
from typing import Dict, Tuple, Optional
import re


class AIEvaluator:
    def __init__(self):
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
        else:
            print("Warning: OPENAI_API_KEY not set. AI evaluation will use mock responses.")
    
    def evaluate_response(self, question: str, answer: str, solution: Optional[str] = None) -> Dict[str, any]:
        """
        Evaluate the candidate's response to a technical question using AI
        Returns scores for technical accuracy, problem-solving logic, and communication clarity
        """
        if not settings.OPENAI_API_KEY:
            return self._mock_evaluation(question, answer)
        
        try:
            # Construct prompt for AI evaluation
            prompt = self._construct_evaluation_prompt(question, answer, solution)
            
            response = openai.ChatCompletion.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an experienced technical interviewer evaluating candidates' responses. Provide objective, fair assessments."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            evaluation_text = response.choices[0].message['content']
            return self._parse_ai_response(evaluation_text)
        
        except Exception as e:
            print(f"Error in AI evaluation: {str(e)}")
            # Return mock evaluation in case of error
            return self._mock_evaluation(question, answer)
    
    def _construct_evaluation_prompt(self, question: str, answer: str, solution: Optional[str]) -> str:
        """Construct the prompt for AI evaluation"""
        prompt = f"""
Evaluate the following response to a technical interview question. Score each category from 0 to 10.

QUESTION: {question}

CANDIDATE RESPONSE: {answer}

"""
        if solution:
            prompt += f"REFERENCE SOLUTION: {solution}\n\n"
        
        prompt += """
Provide your evaluation in the following format:

TECHNICAL_ACCURACY_SCORE: [0-10]
TECHNICAL_ACCURACY_FEEDBACK: [Brief explanation]

PROBLEM_SOLVING_LOGIC_SCORE: [0-10]
PROBLEM_SOLVING_LOGIC_FEEDBACK: [Brief explanation]

COMMUNICATION_CLARITY_SCORE: [0-10]
COMMUNICATION_CLARITY_FEEDBACK: [Brief explanation]

OVERALL_FEEDBACK: [Overall feedback and suggestions for improvement]

FINAL_SCORE: [Combined weighted score out of 10]
"""
        return prompt
    
    def _parse_ai_response(self, ai_response: str) -> Dict[str, any]:
        """Parse the AI response to extract scores and feedback"""
        # Extract scores using regex
        technical_accuracy_match = re.search(r'TECHNICAL_ACCURACY_SCORE:\s*(\d+\.?\d*)', ai_response)
        problem_solving_match = re.search(r'PROBLEM_SOLVING_LOGIC_SCORE:\s*(\d+\.?\d*)', ai_response)
        communication_clarity_match = re.search(r'COMMUNICATION_CLARITY_SCORE:\s*(\d+\.?\d*)', ai_response)
        final_score_match = re.search(r'FINAL_SCORE:\s*(\d+\.?\d*)', ai_response)
        
        # Extract feedback sections
        tech_feedback_match = re.search(r'TECHNICAL_ACCURACY_FEEDBACK:\s*(.*?)(?=PROBLEM_SOLVING_LOGIC_SCORE:|$)', ai_response, re.DOTALL)
        problem_feedback_match = re.search(r'PROBLEM_SOLVING_LOGIC_FEEDBACK:\s*(.*?)(?=COMMUNICATION_CLARITY_SCORE:|$)', ai_response, re.DOTALL)
        comm_feedback_match = re.search(r'COMMUNICATION_CLARITY_FEEDBACK:\s*(.*?)(?=OVERALL_FEEDBACK:|$)', ai_response, re.DOTALL)
        overall_feedback_match = re.search(r'OVERALL_FEEDBACK:\s*(.*?)(?=FINAL_SCORE:|$|END)', ai_response, re.DOTALL)
        
        # Parse scores (default to 0 if not found)
        technical_accuracy = float(technical_accuracy_match.group(1)) if technical_accuracy_match else 0.0
        problem_solving = float(problem_solving_match.group(1)) if problem_solving_match else 0.0
        communication_clarity = float(communication_clarity_match.group(1)) if communication_clarity_match else 0.0
        final_score = float(final_score_match.group(1)) if final_score_match else 0.0
        
        # Clean up feedback text
        technical_feedback = tech_feedback_match.group(1).strip() if tech_feedback_match else "No feedback provided"
        problem_feedback = problem_feedback_match.group(1).strip() if problem_feedback_match else "No feedback provided"
        communication_feedback = comm_feedback_match.group(1).strip() if comm_feedback_match else "No feedback provided"
        overall_feedback = overall_feedback_match.group(1).strip() if overall_feedback_match else "No overall feedback provided"
        
        # Create combined feedback
        combined_feedback = f"Technical Accuracy: {technical_feedback}\nProblem Solving: {problem_feedback}\nCommunication: {communication_feedback}\n\nOverall: {overall_feedback}"
        
        return {
            "technical_accuracy": min(technical_accuracy, 10.0),
            "problem_solving_logic": min(problem_solving, 10.0),
            "communication_clarity": min(communication_clarity, 10.0),
            "final_score": min(final_score, 10.0),
            "feedback": combined_feedback,
            "ai_evaluation": ai_response
        }
    
    def _mock_evaluation(self, question: str, answer: str) -> Dict[str, any]:
        """Mock evaluation when OpenAI API is not available"""
        # This is a simplified mock that analyzes the response content
        answer_length = len(answer.split())
        has_approach = any(word in answer.lower() for word in ['approach', 'algorithm', 'solution', 'think', 'idea'])
        has_complexity = any(word in answer.lower() for word in ['time', 'space', 'complexity', 'efficient', 'runtime'])
        
        # Calculate mock scores based on content analysis
        technical_accuracy = min(10.0, max(1.0, answer_length / 10))
        problem_solving = 5.0  # Default middle score
        if has_approach:
            problem_solving += 2.0
        if has_complexity:
            problem_solving += 1.5
        
        communication_clarity = min(10.0, max(1.0, answer_length / 15))
        
        # Calculate final score as average
        final_score = (technical_accuracy + problem_solving + communication_clarity) / 3
        
        feedback = f"The response demonstrates {'good' if has_approach else 'some'} understanding of the approach. " \
                  f"Consider explaining time/space complexity for stronger answers. " \
                  f"Length of response: {answer_length} words."
        
        return {
            "technical_accuracy": technical_accuracy,
            "problem_solving_logic": min(problem_solving, 10.0),
            "communication_clarity": communication_clarity,
            "final_score": final_score,
            "feedback": feedback,
            "ai_evaluation": "Mock evaluation - OpenAI API key not configured"
        }


# Global instance
ai_evaluator = AIEvaluator()