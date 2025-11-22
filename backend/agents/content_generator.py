from typing import Dict, List, Optional
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from core.llm import llm_provider
from core.llm_ollama import generate_structured


class QuizQuestion(BaseModel):
    """Quiz question schema"""
    question: str
    options: List[str]
    answer: str


class LessonContentOutput(BaseModel):
    """Pydantic schema for lesson content output"""
    lesson_text: str
    quiz: List[QuizQuestion]


class ContentGenerator:
    """Agent for generating learning content"""
    
    def __init__(self):
        self.llm = llm_provider.get_default_llm()
        self.parser = StrOutputParser()
    
    async def generate_content(
        self,
        module_name: str
    ) -> LessonContentOutput:
        """
        Generate lesson content and quiz for a module
        
        Args:
            module_name: Name of the module to generate content for
        
        Returns:
            LessonContentOutput: Validated lesson content with text and quiz
        """
        system_prompt = (
            "You create concise technical lessons and short quizzes. "
            "Keep it simple and beginner-friendly."
        )
        
        user_prompt = f"""Module: {module_name}

Create:
1. A concise, beginner-friendly lesson text that explains the key concepts of {module_name}
2. A short quiz with 3-5 multiple choice questions related to the lesson

The lesson should be:
- Clear and easy to understand
- Suitable for beginners
- Focused on practical concepts
- Approximately 300-500 words

The quiz should:
- Have 3-5 questions
- Each question should have 4 options
- Include the correct answer
- Test understanding of the lesson content

CRITICAL JSON FORMAT REQUIREMENTS:
- lesson_text must be a valid JSON string (escape newlines as \\n, quotes as \\")
- quiz must be an array of objects, where each object has:
  * "question": string (the question text, properly escaped)
  * "options": array of exactly 4 strings (the answer choices)
  * "answer": string (must match one of the options exactly)

Example format:
{{
  "lesson_text": "Lesson content here. Use \\n for newlines.",
  "quiz": [
    {{
      "question": "What is X?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": "Option A"
    }}
  ]
}}

IMPORTANT: All strings must be properly escaped for JSON. Use \\n for newlines, \\" for quotes."""
        
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        # Use Ollama client with structured output
        result = await generate_structured(
            prompt=full_prompt,
            schema=LessonContentOutput
        )
        
        return result
    
    async def generate_generic_content(
        self,
        topic: str,
        content_type: str = "article",
        difficulty: str = "intermediate",
        length: str = "medium",
        context: Optional[Dict] = None
    ) -> str:
        """
        Generate generic learning content (legacy method)
        
        Args:
            topic: Topic for the content
            content_type: Type of content (article, exercise, quiz, video_script)
            difficulty: Difficulty level
            length: Content length (short, medium, long)
            context: Optional context about the user or learning path
        
        Returns:
            Generated content as string
        """
        content_instructions = {
            "article": "Write a comprehensive educational article",
            "exercise": "Create a practical exercise with examples",
            "quiz": "Generate a quiz with questions and answers",
            "video_script": "Write a video script with clear sections"
        }
        
        instruction = content_instructions.get(content_type, "Create educational content")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""You are an expert educational content creator. {instruction} 
            that is engaging, clear, and appropriate for the specified difficulty level."""),
            ("user", """Topic: {topic}
            Content Type: {content_type}
            Difficulty: {difficulty}
            Length: {length}
            Context: {context}""")
        ])
        
        chain = prompt | self.llm | self.parser
        
        result = await chain.ainvoke({
            "topic": topic,
            "content_type": content_type,
            "difficulty": difficulty,
            "length": length,
            "context": str(context or {})
        })
        
        return result
    
    async def generate_exercise(
        self,
        skill: str,
        difficulty: str = "intermediate"
    ) -> Dict:
        """
        Generate a practice exercise
        
        Args:
            skill: Skill to practice
            difficulty: Difficulty level
        
        Returns:
            Dictionary with exercise content
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Generate a practical exercise. Return a JSON object with:
            title, description, instructions, example_input, expected_output, 
            hints (array), and solution."""),
            ("user", "Skill: {skill}\nDifficulty: {difficulty}")
        ])
        
        from langchain_core.output_parsers import JsonOutputParser
        json_parser = JsonOutputParser()
        
        chain = prompt | self.llm | json_parser
        
        result = await chain.ainvoke({
            "skill": skill,
            "difficulty": difficulty
        })
        
        return result
    
    async def generate_quiz(
        self,
        topic: str,
        num_questions: int = 5,
        difficulty: str = "intermediate"
    ) -> Dict:
        """
        Generate a quiz
        
        Args:
            topic: Quiz topic
            num_questions: Number of questions
            difficulty: Difficulty level
        
        Returns:
            Dictionary with quiz content
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Generate a quiz with multiple choice questions. Return a JSON object with:
            title, description, questions (array with question, options, correct_answer, explanation)."""),
            ("user", """Topic: {topic}
            Number of Questions: {num_questions}
            Difficulty: {difficulty}""")
        ])
        
        from langchain_core.output_parsers import JsonOutputParser
        json_parser = JsonOutputParser()
        
        chain = prompt | self.llm | json_parser
        
        result = await chain.ainvoke({
            "topic": topic,
            "num_questions": num_questions,
            "difficulty": difficulty
        })
        
        return result

