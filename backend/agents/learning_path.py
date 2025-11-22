from typing import Dict, List, Optional
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from core.llm import llm_provider
from core.llm_ollama import generate_structured


class ModuleInfo(BaseModel):
    """Module information schema"""
    name: str
    description: str


class WeeklyGoal(BaseModel):
    """Weekly goal with modules, XP, and milestones"""
    week: int
    goals: List[str]  # List of goals for this week
    modules: List[ModuleInfo]  # Modules for this week
    xp: int  # XP points for completing this week
    milestones: List[str]  # Milestones for this week


class LearningPathOutput(BaseModel):
    """Pydantic schema for learning path output"""
    duration_weeks: int
    weekly_goals: List[WeeklyGoal]  # Structured weekly goals with modules, XP, and milestones


class LearningPathGenerator:
    """Agent for generating personalized learning paths"""
    
    def __init__(self):
        self.llm = llm_provider.get_default_llm()
        self.parser = JsonOutputParser()
    
    async def generate_learning_path_plan(
        self,
        skill_map: Dict[str, str],
        experience: int,
        role: str
    ) -> LearningPathOutput:
        """
        Generate a personalized learning path plan based on skill map, experience, and role
        
        Args:
            skill_map: Dictionary mapping skill names to levels (beginner/intermediate/advanced)
            experience: Years of experience
            role: User's role (e.g., "software engineer", "data scientist")
        
        Returns:
            LearningPathOutput: Validated learning path with duration, goals, milestones, and modules
        """
        system_prompt = (
            "You are an expert tech mentor. Create a personalized 4–6 week learning plan "
            "based on the skill map with gamification elements."
        )
        
        user_prompt = f"""Role: {role}
Experience: {experience} years
Skill Map: {skill_map}

Create a comprehensive learning plan that:
1. Has a duration of 4-6 weeks
2. For EACH week, provide:
   - week: Week number (1, 2, 3, etc.)
   - goals: Array of 2-4 specific learning goals for that week (e.g., ["Learn React hooks", "Build a todo app"])
   - modules: Array of 2-4 modules for that week, each with "name" and "description"
   - xp: XP points for completing that week (100-500 points, increasing with difficulty)
   - milestones: Array of 1-3 key milestones/achievements for that week (e.g., ["Complete first React component", "Deploy app to Vercel"])

IMPORTANT STRUCTURE:
- weekly_goals must be an array of objects, where each object has:
  - week: integer (1, 2, 3, etc.)
  - goals: array of strings (e.g., ["Goal 1", "Goal 2"])
  - modules: array of objects with "name" (string) and "description" (string)
  - xp: integer (gamification points, 100-500)
  - milestones: array of strings (e.g., ["Milestone 1", "Milestone 2"])

Example structure:
{{
  "duration_weeks": 4,
  "weekly_goals": [
    {{
      "week": 1,
      "goals": ["Learn React basics", "Set up development environment"],
      "modules": [
        {{"name": "React Fundamentals", "description": "Introduction to React components and JSX"}},
        {{"name": "Development Setup", "description": "Setting up React development environment"}}
      ],
      "xp": 100,
      "milestones": ["Complete first React component", "Set up project"]
    }},
    {{
      "week": 2,
      "goals": ["Build interactive components", "Learn state management"],
      "modules": [
        {{"name": "State Management", "description": "Understanding React state and props"}},
        {{"name": "Event Handling", "description": "Handling user interactions"}}
      ],
      "xp": 150,
      "milestones": ["Build a todo app", "Implement state management"]
    }}
  ]
}}

Focus on addressing skill gaps and building on existing strengths from the skill map.
Make the plan practical and achievable for someone with {experience} years of experience.
Distribute XP points based on difficulty - easier weeks get less XP, harder weeks get more."""
        
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        # Use Ollama client with structured output
        result = await generate_structured(
            prompt=full_prompt,
            schema=LearningPathOutput
        )
        
        return result
    
    async def generate_learning_path(
        self,
        skill_goal: str,
        current_skills: Dict,
        difficulty: str = "intermediate",
        duration_hours: Optional[int] = None
    ) -> Dict:
        """
        Generate a personalized learning path
        
        Args:
            skill_goal: Target skill or goal
            current_skills: Dictionary of current skill levels
            difficulty: Desired difficulty level
            duration_hours: Estimated hours available
        
        Returns:
            Dictionary with learning path structure
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert learning path designer. Create a structured 
            learning path with modules, lessons, and milestones. Return a JSON object with:
            title, description, modules (array with title, description, order, estimated_time), 
            milestones, and estimated_total_duration."""),
            ("user", """Goal: {goal}
            Current Skills: {skills}
            Difficulty: {difficulty}
            Available Time: {duration} hours""")
        ])
        
        chain = prompt | self.llm | self.parser
        
        result = await chain.ainvoke({
            "goal": skill_goal,
            "skills": str(current_skills),
            "difficulty": difficulty,
            "duration": duration_hours or "flexible"
        })
        
        return result
    
    async def adapt_learning_path(
        self,
        existing_path: Dict,
        progress_data: Dict,
        feedback: Optional[str] = None
    ) -> Dict:
        """
        Adapt an existing learning path based on progress and feedback
        
        Args:
            existing_path: Current learning path structure
            progress_data: User progress information
            feedback: Optional user feedback
        
        Returns:
            Updated learning path
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Adapt the learning path based on user progress and feedback. 
            Adjust difficulty, add/remove modules, or modify content as needed. 
            Return the updated learning path as JSON."""),
            ("user", """Current Path: {path}
            Progress: {progress}
            Feedback: {feedback}""")
        ])
        
        chain = prompt | self.llm | self.parser
        
        result = await chain.ainvoke({
            "path": str(existing_path),
            "progress": str(progress_data),
            "feedback": feedback or "None"
        })
        
        return result
    
    async def suggest_next_steps(
        self,
        current_module: str,
        completion_status: Dict
    ) -> List[Dict]:
        """
        Suggest next steps in the learning path
        
        Args:
            current_module: Current module identifier
            completion_status: Completion status of current and previous modules
        
        Returns:
            List of suggested next steps
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Based on the current learning progress, suggest the next steps. 
            Return a JSON array of suggestions with: step, reason, priority, and estimated_time."""),
            ("user", """Current Module: {module}
            Completion Status: {status}""")
        ])
        
        chain = prompt | self.llm | self.parser
        
        result = await chain.ainvoke({
            "module": current_module,
            "status": str(completion_status)
        })
        
        return result if isinstance(result, list) else [result]

