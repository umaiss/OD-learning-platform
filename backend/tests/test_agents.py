"""
Test suite for agent methods
Tests all agent functions with fake inputs and verifies expected outputs
"""
import pytest
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from agents.skill_profiler import SkillProfiler, SkillProfileOutput
from agents.learning_path import LearningPathGenerator, LearningPathOutput
from agents.content_generator import ContentGenerator, LessonContentOutput
from agents.missions import MissionGenerator, DailyMissionsOutput
from agents.chatbot import ChatbotAgent


@pytest.fixture
def skill_profiler():
    """Fixture for SkillProfiler instance"""
    return SkillProfiler()


@pytest.fixture
def learning_path_generator():
    """Fixture for LearningPathGenerator instance"""
    return LearningPathGenerator()


@pytest.fixture
def content_generator():
    """Fixture for ContentGenerator instance"""
    return ContentGenerator()


@pytest.fixture
def mission_generator():
    """Fixture for MissionGenerator instance"""
    return MissionGenerator()


@pytest.fixture
def chatbot_agent():
    """Fixture for ChatbotAgent instance"""
    return ChatbotAgent()


@pytest.mark.asyncio
async def test_skill_profiler_generate_skill_profile(skill_profiler):
    """Test skill profiler returns strengths and gaps"""
    # Fake input
    self_assessment = "I'm good at Python programming and React development. I need to learn Docker and Kubernetes."
    role = "software engineer"
    experience = 3
    
    # Call the agent
    result = await skill_profiler.generate_skill_profile(
        self_assessment=self_assessment,
        role=role,
        experience=experience
    )
    
    # Verify it's a SkillProfileOutput instance
    assert isinstance(result, SkillProfileOutput)
    
    # Verify strengths exist and is a list
    assert hasattr(result, 'strengths')
    assert isinstance(result.strengths, list)
    assert len(result.strengths) > 0, "Strengths list should not be empty"
    
    # Verify gaps exist and is a list
    assert hasattr(result, 'gaps')
    assert isinstance(result.gaps, list)
    assert len(result.gaps) > 0, "Gaps list should not be empty"
    
    # Verify skill_map exists and is a dict
    assert hasattr(result, 'skill_map')
    assert isinstance(result.skill_map, dict)
    assert len(result.skill_map) > 0, "Skill map should not be empty"
    
    # Verify skill_map values are valid levels
    valid_levels = ['beginner', 'intermediate', 'advanced']
    for skill, level in result.skill_map.items():
        assert level.lower() in valid_levels, f"Skill level '{level}' should be one of {valid_levels}"


@pytest.mark.asyncio
async def test_learning_path_generator_generate_learning_path_plan(learning_path_generator):
    """Test learning path generator returns weekly_goals"""
    # Fake input
    skill_map = {
        "Python": "intermediate",
        "Docker": "beginner",
        "React": "advanced",
        "Kubernetes": "beginner"
    }
    experience = 3
    role = "software engineer"
    
    # Call the agent
    result = await learning_path_generator.generate_learning_path_plan(
        skill_map=skill_map,
        experience=experience,
        role=role
    )
    
    # Verify it's a LearningPathOutput instance
    assert isinstance(result, LearningPathOutput)
    
    # Verify duration_weeks exists and is between 4-6
    assert hasattr(result, 'duration_weeks')
    assert isinstance(result.duration_weeks, int)
    assert 4 <= result.duration_weeks <= 6, "Duration should be 4-6 weeks"
    
    # Verify weekly_goals exists and is a list
    assert hasattr(result, 'weekly_goals')
    assert isinstance(result.weekly_goals, list)
    assert len(result.weekly_goals) > 0, "Weekly goals should not be empty"
    assert len(result.weekly_goals) == result.duration_weeks, "Weekly goals should match duration"
    
    # Verify milestones exist
    assert hasattr(result, 'milestones')
    assert isinstance(result.milestones, list)
    assert len(result.milestones) > 0, "Milestones should not be empty"
    
    # Verify modules exist
    assert hasattr(result, 'modules')
    assert isinstance(result.modules, list)
    assert len(result.modules) > 0, "Modules should not be empty"
    
    # Verify each module has name and description
    for module in result.modules:
        assert hasattr(module, 'name')
        assert hasattr(module, 'description')
        assert module.name, "Module name should not be empty"
        assert module.description, "Module description should not be empty"


@pytest.mark.asyncio
async def test_content_generator_generate_content(content_generator):
    """Test content generator returns lesson and quiz"""
    # Fake input
    module_name = "Docker Basics"
    
    # Call the agent
    result = await content_generator.generate_content(
        module_name=module_name
    )
    
    # Verify it's a LessonContentOutput instance
    assert isinstance(result, LessonContentOutput)
    
    # Verify lesson_text exists and is not empty
    assert hasattr(result, 'lesson_text')
    assert isinstance(result.lesson_text, str)
    assert len(result.lesson_text) > 0, "Lesson text should not be empty"
    assert len(result.lesson_text) > 100, "Lesson text should be substantial (at least 100 chars)"
    
    # Verify quiz exists and is a list
    assert hasattr(result, 'quiz')
    assert isinstance(result.quiz, list)
    assert len(result.quiz) > 0, "Quiz should not be empty"
    assert 3 <= len(result.quiz) <= 5, "Quiz should have 3-5 questions"
    
    # Verify each quiz question has required fields
    for question in result.quiz:
        assert hasattr(question, 'question')
        assert hasattr(question, 'options')
        assert hasattr(question, 'answer')
        assert question.question, "Question text should not be empty"
        assert isinstance(question.options, list)
        assert len(question.options) == 4, "Each question should have 4 options"
        assert question.answer, "Answer should not be empty"
        assert question.answer in question.options, "Answer should be one of the options"


@pytest.mark.asyncio
async def test_mission_generator_generate_daily_missions(mission_generator):
    """Test mission generator returns missions list"""
    # Fake input
    skill_map = {
        "Python": "intermediate",
        "Docker": "beginner",
        "React": "advanced"
    }
    
    # Call the agent
    result = await mission_generator.generate_daily_missions(
        skill_map=skill_map
    )
    
    # Verify it's a DailyMissionsOutput instance
    assert isinstance(result, DailyMissionsOutput)
    
    # Verify missions exist and is a list
    assert hasattr(result, 'missions')
    assert isinstance(result.missions, list)
    assert len(result.missions) > 0, "Missions list should not be empty"
    assert 3 <= len(result.missions) <= 5, "Should have 3-5 missions"
    
    # Verify each mission is a string
    for mission in result.missions:
        assert isinstance(mission, str)
        assert len(mission) > 0, "Mission should not be empty"
        assert len(mission) < 200, "Mission should be concise (under 200 chars)"
    
    # Verify xp exists and is positive
    assert hasattr(result, 'xp')
    assert isinstance(result.xp, int)
    assert result.xp >= 0, "XP should be non-negative"
    assert result.xp <= 100, "XP should be reasonable (under 100)"
    
    # Verify streak_increment exists
    assert hasattr(result, 'streak_increment')
    assert isinstance(result.streak_increment, int)
    assert result.streak_increment >= 0, "Streak increment should be non-negative"


@pytest.mark.asyncio
async def test_chatbot_agent_chat_with_context(chatbot_agent):
    """Test chatbot returns a technical response"""
    # Fake input
    message = "How do I get started with Docker?"
    skill_map = {
        "Python": "intermediate",
        "Docker": "beginner"
    }
    learning_plan = {
        "duration_weeks": 4,
        "weekly_goals": ["Learn Docker basics", "Practice containerization"],
        "modules": [{"name": "Docker Basics", "description": "Introduction to Docker"}]
    }
    
    # Call the agent (without db for testing)
    result = await chatbot_agent.chat_with_context(
        message=message,
        skill_map=skill_map,
        learning_plan=learning_plan,
        conversation_history=None,
        db=None  # Skip database for unit test
    )
    
    # Verify response is a string
    assert isinstance(result, str)
    assert len(result) > 0, "Response should not be empty"
    assert len(result) > 50, "Response should be substantial (at least 50 chars)"
    
    # Verify response contains technical content (basic check)
    # The response should mention Docker or containerization
    response_lower = result.lower()
    technical_keywords = ['docker', 'container', 'image', 'command', 'run', 'build']
    has_technical_content = any(keyword in response_lower for keyword in technical_keywords)
    assert has_technical_content, "Response should contain technical content related to the question"


@pytest.mark.asyncio
async def test_skill_profiler_output_structure(skill_profiler):
    """Test skill profiler output structure is correct"""
    result = await skill_profiler.generate_skill_profile(
        self_assessment="I know JavaScript and React well, but I'm new to TypeScript.",
        role="frontend developer",
        experience=2
    )
    
    # Check all required fields are present
    required_fields = ['strengths', 'gaps', 'skill_map']
    for field in required_fields:
        assert hasattr(result, field), f"Result should have '{field}' field"
    
    # Check strengths are strings
    for strength in result.strengths:
        assert isinstance(strength, str), "Each strength should be a string"
    
    # Check gaps are strings
    for gap in result.gaps:
        assert isinstance(gap, str), "Each gap should be a string"


@pytest.mark.asyncio
async def test_learning_path_output_structure(learning_path_generator):
    """Test learning path output structure is correct"""
    result = await learning_path_generator.generate_learning_path_plan(
        skill_map={"Python": "beginner"},
        experience=1,
        role="developer"
    )
    
    # Check all required fields
    required_fields = ['duration_weeks', 'weekly_goals', 'milestones', 'modules']
    for field in required_fields:
        assert hasattr(result, field), f"Result should have '{field}' field"
    
    # Check weekly_goals match duration
    assert len(result.weekly_goals) == result.duration_weeks, \
        "Number of weekly goals should match duration in weeks"


@pytest.mark.asyncio
async def test_content_output_structure(content_generator):
    """Test content generator output structure is correct"""
    result = await content_generator.generate_content(
        module_name="Python Functions"
    )
    
    # Check all required fields
    assert hasattr(result, 'lesson_text'), "Result should have 'lesson_text' field"
    assert hasattr(result, 'quiz'), "Result should have 'quiz' field"
    
    # Check quiz questions structure
    for i, question in enumerate(result.quiz):
        assert hasattr(question, 'question'), f"Question {i} should have 'question' field"
        assert hasattr(question, 'options'), f"Question {i} should have 'options' field"
        assert hasattr(question, 'answer'), f"Question {i} should have 'answer' field"


@pytest.mark.asyncio
async def test_mission_output_structure(mission_generator):
    """Test mission generator output structure is correct"""
    result = await mission_generator.generate_daily_missions(
        skill_map={"JavaScript": "intermediate"}
    )
    
    # Check all required fields
    required_fields = ['missions', 'xp', 'streak_increment']
    for field in required_fields:
        assert hasattr(result, field), f"Result should have '{field}' field"
    
    # Check missions are non-empty strings
    for mission in result.missions:
        assert isinstance(mission, str), "Each mission should be a string"
        assert len(mission.strip()) > 0, "Mission should not be empty or whitespace"

