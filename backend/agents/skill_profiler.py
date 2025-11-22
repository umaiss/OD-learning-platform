from typing import Dict, List, Optional
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from core.llm import llm_provider
from core.llm_ollama import generate_structured


class SkillProfileOutput(BaseModel):
    """Pydantic schema for skill profile output"""
    strengths: List[str]
    gaps: List[str]
    skill_map: Dict[str, str]  # skill -> level (beginner/intermediate/advanced)


class SkillProfiler:
    """Agent for profiling user skills and determining skill levels"""
    
    def __init__(self):
        self.llm = llm_provider.get_default_llm()
        self.parser = JsonOutputParser()
    
    async def generate_skill_profile(
        self,
        self_assessment: str,
        role: str,
        experience: int
    ) -> SkillProfileOutput:
        """
        Generate a skill profile based on self-assessment, role, and experience
        
        Args:
            self_assessment: User's self-assessment text describing their skills
            role: User's role (e.g., "software engineer", "data scientist")
            experience: Years of experience
        
        Returns:
            SkillProfileOutput: Validated skill profile with strengths, gaps, and skill map
        """
        system_prompt = (
            "You are an expert technical skill evaluator. Based on self assessment, "
            "generate strengths, improvement areas, and a structured skill map for a software engineer."
        )
        
        user_prompt = f"""Role: {role}
Experience: {experience} years
Self Assessment: {self_assessment}

Please analyze this information and provide:
1. A list of strengths (technical skills they excel at)
2. A list of gaps/improvement areas (skills that need development)
3. A skill map (dictionary mapping skill names to levels: beginner, intermediate, or advanced)

Focus on technical skills relevant to the role."""
        
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        # Use Ollama client with structured output
        result = await generate_structured(
            prompt=full_prompt,
            schema=SkillProfileOutput
        )
        
        return result
    
    async def profile_skills(
        self,
        user_input: str,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Profile user skills based on input text
        
        Args:
            user_input: User's description of their skills/experience
            context: Optional additional context about the user
        
        Returns:
            Dictionary with skill profiles
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a skill profiling expert. Analyze the user's input and 
            determine their skill levels across different domains. Return a JSON object with 
            skills and their levels (beginner, intermediate, advanced)."""),
            ("user", "User input: {user_input}\nContext: {context}")
        ])
        
        chain = prompt | self.llm | self.parser
        
        result = await chain.ainvoke({
            "user_input": user_input,
            "context": context or {}
        })
        
        return result
    
    async def assess_skill_level(
        self,
        skill_name: str,
        user_responses: List[str]
    ) -> Dict:
        """
        Assess skill level based on user responses to questions
        
        Args:
            skill_name: Name of the skill being assessed
            user_responses: List of user responses to assessment questions
        
        Returns:
            Dictionary with skill assessment results
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""You are assessing the user's level in {skill_name}. 
            Based on their responses, determine if they are beginner, intermediate, or advanced.
            Return a JSON object with the skill level and detailed assessment."""),
            ("user", "User responses: {responses}")
        ])
        
        chain = prompt | self.llm | self.parser
        
        result = await chain.ainvoke({
            "responses": "\n".join(user_responses)
        })
        
        return result
    
    async def generate_skill_questions(
        self,
        skill_name: str,
        difficulty: str = "intermediate"
    ) -> List[Dict]:
        """
        Generate assessment questions for a skill
        
        Args:
            skill_name: Name of the skill
            difficulty: Target difficulty level
        
        Returns:
            List of question dictionaries
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Generate assessment questions for skill evaluation. 
            Return a JSON array of questions with fields: question, type (multiple_choice/open_ended), 
            options (if multiple_choice), and difficulty."""),
            ("user", "Skill: {skill_name}\nDifficulty: {difficulty}")
        ])
        
        chain = prompt | self.llm | self.parser
        
        result = await chain.ainvoke({
            "skill_name": skill_name,
            "difficulty": difficulty
        })
        
        return result if isinstance(result, list) else [result]

