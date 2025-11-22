from typing import Dict, List, Optional
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from core.llm import llm_provider
from core.llm_ollama import generate_structured


class DailyMissionsOutput(BaseModel):
    """Pydantic schema for daily missions output"""
    missions: List[str]
    xp: int
    streak_increment: int


class MissionGenerator:
    """Agent for generating gamified learning missions"""
    
    def __init__(self):
        self.llm = llm_provider.get_default_llm()
        self.parser = JsonOutputParser()
    
    async def generate_daily_missions(
        self,
        skill_map: Dict[str, str]
    ) -> DailyMissionsOutput:
        """
        Generate daily micro missions based on skill map
        
        Args:
            skill_map: Dictionary mapping skill names to levels (beginner/intermediate/advanced)
        
        Returns:
            DailyMissionsOutput: Validated daily missions with XP and streak increment
        """
        system_prompt = (
            "Generate 3-5 micro missions based on the learner's skill map. "
            "missions should be short, 5-minute tasks."
        )
        
        user_prompt = f"""Skill Map: {skill_map}

Create 3-5 micro missions that:
- Are short, focused tasks (approximately 5 minutes each)
- Target skills from the skill map
- Are appropriate for the skill levels indicated
- Are actionable and achievable
- Help build on strengths and address gaps

IMPORTANT:
- missions must be an array of strings, NOT objects. Example: ["Mission 1", "Mission 2", "Mission 3"]
- Each mission should be a simple string description
- Do NOT use objects like {{"mission": "..."}} or {{"task": "..."}}

For each mission:
- Make it specific and clear
- Focus on practical, hands-on learning
- Keep it engaging and motivating

Also provide:
- Total XP points for completing all missions (typically 10-50 points, as an integer)
- Streak increment (usually 1, but can be higher for completing all missions, as an integer)"""
        
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        # Use Ollama client with structured output
        result = await generate_structured(
            prompt=full_prompt,
            schema=DailyMissionsOutput
        )
        
        return result
    
    async def generate_mission(
        self,
        skill: str,
        mission_type: str = "practice",
        difficulty: str = "intermediate",
        user_level: Optional[str] = None
    ) -> Dict:
        """
        Generate a learning mission
        
        Args:
            skill: Target skill for the mission
            mission_type: Type of mission (practice, challenge, project)
            difficulty: Difficulty level
            user_level: User's current skill level
        
        Returns:
            Dictionary with mission details
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a gamification expert. Create engaging learning missions. 
            Return a JSON object with: title, description, objectives (array), tasks (array), 
            points, difficulty, estimated_time, and success_criteria."""),
            ("user", """Skill: {skill}
            Mission Type: {mission_type}
            Difficulty: {difficulty}
            User Level: {user_level}""")
        ])
        
        chain = prompt | self.llm | self.parser
        
        result = await chain.ainvoke({
            "skill": skill,
            "mission_type": mission_type,
            "difficulty": difficulty,
            "user_level": user_level or "intermediate"
        })
        
        return result
    
    async def generate_mission_series(
        self,
        skill_path: List[str],
        difficulty_progression: str = "gradual"
    ) -> List[Dict]:
        """
        Generate a series of related missions
        
        Args:
            skill_path: List of skills to cover
            difficulty_progression: How difficulty should progress
        
        Returns:
            List of mission dictionaries
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Generate a series of connected learning missions that build upon each other. 
            Return a JSON array of missions, each with: title, description, skill, order, 
            difficulty, points, and prerequisites."""),
            ("user", """Skills: {skills}
            Difficulty Progression: {progression}""")
        ])
        
        chain = prompt | self.llm | self.parser
        
        result = await chain.ainvoke({
            "skills": ", ".join(skill_path),
            "progression": difficulty_progression
        })
        
        return result if isinstance(result, list) else [result]
    
    async def evaluate_mission_completion(
        self,
        mission: Dict,
        user_submission: str
    ) -> Dict:
        """
        Evaluate if a mission has been completed successfully
        
        Args:
            mission: Mission details
            user_submission: User's submission/response
        
        Returns:
            Evaluation results
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Evaluate the user's mission submission. Return a JSON object with:
            completed (boolean), score (0-100), feedback, strengths, areas_for_improvement, 
            and points_earned."""),
            ("user", """Mission: {mission}
            User Submission: {submission}""")
        ])
        
        chain = prompt | self.llm | self.parser
        
        result = await chain.ainvoke({
            "mission": str(mission),
            "submission": user_submission
        })
        
        return result

