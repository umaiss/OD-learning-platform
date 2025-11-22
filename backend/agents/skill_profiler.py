from typing import Dict, List, Optional
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from core.llm import llm_provider
from core.llm_ollama import generate_structured


class EndorsedSkill(BaseModel):
    """LinkedIn endorsed skill"""
    skill: str
    endorsements: int


class LinkedInProfile(BaseModel):
    """LinkedIn profile data"""
    id: Optional[int] = None
    learnerId: Optional[int] = None
    username: Optional[str] = None
    fullName: Optional[str] = None
    headline: Optional[str] = None
    location: Optional[str] = None
    endorsedSkills: Optional[List[EndorsedSkill]] = None
    connections: Optional[int] = None
    followers: Optional[int] = None


class SkillProfileOutput(BaseModel):
    """Pydantic schema for skill profile output"""
    ai_analysis: str  # AI analysis and remarks
    strengths: List[str]
    growth_areas: List[str]  # Renamed from gaps for clarity
    skill_map: Dict[str, str]  # skill -> level (beginner/intermediate/advanced)


class SkillProfiler:
    """Agent for profiling user skills and determining skill levels"""
    
    def __init__(self):
        self.llm = llm_provider.get_default_llm()
        self.parser = JsonOutputParser()
    
    async def generate_skill_profile(
        self,
        current_role: str,
        primary_stack: List[str],
        learning_goals: str,
        skill_rate: Optional[Dict[str, str]] = None,  # skill -> rate (e.g., {"JavaScript": "8/10"})
        linkedin_profile: Optional[LinkedInProfile] = None
    ) -> SkillProfileOutput:
        """
        Generate a comprehensive skill profile based on role, stack, goals, and LinkedIn data
        
        Args:
            current_role: User's current role (e.g., "software engineer", "data scientist")
            primary_stack: Array of primary technologies (e.g., ["JavaScript", "Python", "React"])
            learning_goals: User's learning goals and objectives
            skill_rate: Dictionary mapping skills to self-rated levels (optional)
            linkedin_profile: LinkedIn profile data (optional)
        
        Returns:
            SkillProfileOutput: Validated skill profile with AI analysis, strengths, growth areas, and skill map
        """
        system_prompt = (
            "You are an expert technical skill evaluator and career advisor. "
            "Analyze the provided information comprehensively and provide detailed insights including: "
            "1. AI Analysis and Remarks: A comprehensive analysis of the user's profile, combining all provided data "
            "   to give insights about their technical background, career trajectory, and potential. "
            "2. Strengths: List of technical skills and competencies they excel at. "
            "3. Growth Areas: List of skills and areas that need development or improvement. "
            "4. Skill Map: A comprehensive dictionary mapping all relevant skills to levels (beginner/intermediate/advanced)."
        )
        
        # Build user prompt with all available data
        user_prompt_parts = [
            f"Current Role: {current_role}",
            f"Primary Stack: {', '.join(primary_stack)}",
            f"Learning Goals: {learning_goals}"
        ]
        
        if skill_rate:
            skill_rate_str = ", ".join([f"{skill}: {rate}" for skill, rate in skill_rate.items()])
            user_prompt_parts.append(f"Skill Self-Ratings: {skill_rate_str}")
        
        if linkedin_profile:
            linkedin_info = []
            if linkedin_profile.fullName:
                linkedin_info.append(f"Name: {linkedin_profile.fullName}")
            if linkedin_profile.headline:
                linkedin_info.append(f"Headline: {linkedin_profile.headline}")
            if linkedin_profile.location:
                linkedin_info.append(f"Location: {linkedin_profile.location}")
            if linkedin_profile.endorsedSkills:
                endorsed_skills_str = ", ".join([
                    f"{skill.skill} ({skill.endorsements} endorsements)"
                    for skill in linkedin_profile.endorsedSkills
                ])
                linkedin_info.append(f"Endorsed Skills: {endorsed_skills_str}")
            if linkedin_profile.connections:
                linkedin_info.append(f"Connections: {linkedin_profile.connections}")
            if linkedin_profile.followers:
                linkedin_info.append(f"Followers: {linkedin_profile.followers}")
            
            if linkedin_info:
                user_prompt_parts.append(f"\nLinkedIn Profile Data:\n" + "\n".join(linkedin_info))
        
        user_prompt = "\n".join(user_prompt_parts)
        
        user_prompt += """

Please provide a comprehensive analysis:
1. AI Analysis and Remarks: A detailed analysis (2-3 paragraphs) that synthesizes all the provided information,
   highlighting the user's technical background, strengths, career positioning, and potential growth trajectory.
   Consider their primary stack, learning goals, LinkedIn endorsements, and any self-ratings.

2. Strengths: A list of specific technical skills, competencies, and areas where the user demonstrates proficiency.
   Consider their primary stack, LinkedIn endorsements, and any patterns in their profile.

3. Growth Areas: A list of skills, technologies, or competencies that would benefit from development based on:
   - Their learning goals
   - Gaps in their primary stack
   - Emerging technologies in their field
   - Career advancement opportunities

4. Skill Map: A comprehensive dictionary mapping ALL relevant skills (from primary stack, LinkedIn, and related technologies)
   to skill levels: "beginner", "intermediate", or "advanced". Include:
   - All skills from the primary stack
   - Skills from LinkedIn endorsements
   - Related technologies that are relevant to their role and goals
   - Skills mentioned in their learning goals

Be thorough and provide actionable insights."""
        
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

