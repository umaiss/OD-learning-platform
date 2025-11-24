from typing import Dict, List, Optional
from pydantic import BaseModel
from core.llm_ollama import generate_structured
from sqlalchemy.orm import Session
from db.models import Learner


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
    """Agent for generating personalized learning paths using Ollama"""
    
    def __init__(self):
        pass
    
    async def _load_skill_map_from_learner(
        self,
        learner_id: int,
        db: Session
    ) -> Optional[Dict[str, str]]:
        """Load skill_map from learner profile if learner_id is provided"""
        try:
            learner = db.query(Learner).filter(Learner.id == learner_id).first()
            if learner and learner.skill_map:
                return learner.skill_map
            return None
        except Exception as e:
            print(f"Warning: Failed to load skill_map from learner {learner_id}: {str(e)}")
            return None
    
    async def generate_learning_path_plan(
        self,
        skill_map: Optional[Dict[str, str]] = None,
        experience: int = 0,
        role: str = "developer",
        learning_goals: str = "",
        learner_id: Optional[int] = None,
        db: Optional[Session] = None
    ) -> LearningPathOutput:
        """
        Generate a personalized learning path plan based on skill map, experience, role, and learning goals
        
        Args:
            skill_map: Dictionary mapping skill names to levels (beginner/intermediate/advanced). 
                      If None and learner_id is provided, will load from database.
            experience: Years of experience
            role: User's role (e.g., "software engineer", "data scientist", "developer")
            learning_goals: User's learning goals and career objectives
            learner_id: Optional learner ID to load skill_map from database
            db: Optional database session for loading skill_map
        
        Returns:
            LearningPathOutput: Validated learning path with duration, goals, milestones, and modules
        """
        # Load skill_map from learner if not provided but learner_id is available
        if skill_map is None and learner_id is not None and db is not None:
            skill_map = await self._load_skill_map_from_learner(learner_id, db)
        
        if skill_map is None:
            skill_map = {}
        
        # Build comprehensive system prompt
        system_prompt = """You are an expert tech mentor and learning path designer with deep knowledge of software development, 
programming languages, frameworks, and career progression. Your task is to create personalized, practical, and achievable 
learning paths that help developers grow their skills systematically.

Key Principles:
1. Create learning paths that are realistic and achievable (4-6 weeks duration)
2. Build progressively - each week should build on previous weeks
3. Balance theory with practical projects
4. Address skill gaps while building on existing strengths
5. Make content relevant to the user's role and career goals
6. Include gamification elements (XP points) that increase with difficulty
7. Set clear, measurable milestones for each week

You MUST return ONLY valid JSON that matches the exact schema provided. Do not include markdown, code blocks, or any explanatory text."""

        # Build user prompt with context
        user_prompt_parts = [
            "## User Profile",
            f"Role: {role}",
            f"Experience: {experience} years",
        ]
        
        if skill_map:
            skill_map_str = ", ".join([f"{skill}: {level}" for skill, level in skill_map.items()])
            user_prompt_parts.append(f"Current Skills: {skill_map_str}")
        else:
            user_prompt_parts.append("Current Skills: Not specified (assume beginner level)")
        
        if learning_goals:
            user_prompt_parts.append(f"\n## Learning Goals & Career Objectives")
            user_prompt_parts.append(learning_goals)
            user_prompt_parts.append("\nCRITICAL: The entire learning path MUST directly support these learning goals.")
        
        user_prompt_parts.append("\n## Task")
        user_prompt_parts.append("""Create a comprehensive, week-by-week learning plan with the following structure:

1. Duration: 4-6 weeks (choose based on complexity and user's experience level)
2. For EACH week, provide:
   - week: Week number (1, 2, 3, etc.)
   - goals: Array of 2-4 specific, actionable learning goals (e.g., ["Learn React hooks", "Build a todo app"])
   - modules: Array of 2-4 learning modules, each with:
     * name: Clear, descriptive module name
     * description: Brief description of what will be learned
   - xp: XP points (100-500, increasing with week number and difficulty)
   - milestones: Array of 1-3 concrete, measurable achievements (e.g., ["Complete first React component", "Deploy app to Vercel"])

## Guidelines:
- Start with fundamentals if user has beginner skills, or advanced topics if they're experienced
- Each week should have 2-4 modules that are cohesive and build on each other
- XP should increase progressively (Week 1: 100-150, Week 2: 150-200, etc.)
- Milestones should be specific and achievable within that week
- If learning goals are provided, ensure every week directly contributes to those goals
- Make the path practical - include hands-on projects and real-world applications

## Example Structure:
{
  "duration_weeks": 6,
  "weekly_goals": [
    {
      "week": 1,
      "goals": ["Learn React basics", "Set up development environment"],
      "modules": [
        {"name": "React Fundamentals", "description": "Introduction to React components and JSX"},
        {"name": "Development Setup", "description": "Setting up React development environment"}
      ],
      "xp": 100,
      "milestones": ["Complete first React component", "Set up project"]
    },
    {
      "week": 2,
      "goals": ["Learn React hooks", "Build a todo app"],
      "modules": [
        {"name": "React Hooks", "description": "Understanding React hooks and their applications"},
        {"name": "Todo App Development", "description": "Building a simple todo app with React"}
      ],
      "xp": 200,
      "milestones": ["Complete first React component", "Deploy app to Vercel"]
    }
  ]
}

Remember: Return ONLY the JSON object. No markdown, no code blocks, no explanations.""")
        
        full_prompt = f"{system_prompt}\n\n{chr(10).join(user_prompt_parts)}"
        
        # Use Ollama with structured output
        result = await generate_structured(
            prompt=full_prompt,
            schema=LearningPathOutput,
            retry_on_failure=True
        )
        
        return result

