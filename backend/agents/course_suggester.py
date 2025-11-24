"""
Course suggester agent - Hybrid approach using local database + LLM
"""
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from db.models import Course
from db.vector import VectorEmbedding
from core.embeddings import generate_embedding
from core.llm_ollama import generate_structured
from pydantic import BaseModel


class LearningMaterial(BaseModel):
    """Learning material structure matching the API"""
    title: str
    url: str
    platform: str
    type: Optional[str] = "course"
    estimated_hours: Optional[int] = None
    description: Optional[str] = None


class CourseSuggestionOutput(BaseModel):
    """Pydantic schema for course suggestions"""
    suggested_courses: List[Dict]  # List of course suggestions with title, url, platform, etc.


class CourseSuggester:
    """Agent for suggesting courses using hybrid approach (local DB + LLM)"""
    
    def __init__(self):
        pass
    
    async def suggest_courses_for_module(
        self,
        db: Session,
        module_name: str,
        module_description: str,
        skill_level: str = "intermediate",
        limit: int = 5
    ) -> List[LearningMaterial]:
        """
        Suggest courses for a module using hybrid approach:
        1. Search local database using vector similarity
        2. Use LLM to suggest additional courses if needed
        3. Combine and rank results
        
        Args:
            db: Database session
            module_name: Name of the module
            module_description: Description of the module
            skill_level: Skill level (beginner, intermediate, advanced)
            limit: Maximum number of suggestions to return
            
        Returns:
            List of LearningMaterial objects
        """
        suggestions = []
        
        # Step 1: Search local database using vector similarity
        db_suggestions = await self._search_local_database(
            db=db,
            query=f"{module_name} {module_description}",
            skill_level=skill_level,
            limit=limit
        )
        
        suggestions.extend(db_suggestions)
        
        # Step 2: If we don't have enough suggestions, use LLM to suggest more
        if len(suggestions) < limit:
            llm_suggestions = await self._llm_suggest_courses(
                module_name=module_name,
                module_description=module_description,
                skill_level=skill_level,
                limit=limit - len(suggestions)
            )
            suggestions.extend(llm_suggestions)
        
        # Step 3: Remove duplicates and limit results
        seen_urls = set()
        unique_suggestions = []
        for suggestion in suggestions:
            if suggestion.url not in seen_urls:
                seen_urls.add(suggestion.url)
                unique_suggestions.append(suggestion)
                if len(unique_suggestions) >= limit:
                    break
        
        return unique_suggestions[:limit]
    
    async def _search_local_database(
        self,
        db: Session,
        query: str,
        skill_level: str,
        limit: int
    ) -> List[LearningMaterial]:
        """
        Search local course database using vector similarity
        """
        try:
            # Generate embedding for the query
            query_embedding = await generate_embedding(query)
            embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"
            
            # Search for courses using vector similarity
            # Use CAST to properly handle vector type in parameterized query
            results = db.execute(
                text("""
                    SELECT c.id, c.title, c.url, c.platform, c.description, 
                           c.duration_hours, c.rating, c.difficulty,
                           1 - (ve.embedding <=> CAST(:query_embedding AS vector)) as similarity
                    FROM courses c
                    JOIN vector_embeddings ve ON ve.course_id = c.id
                    WHERE ve.content_type = 'course'
                      AND ve.embedding IS NOT NULL
                      AND (c.difficulty = :skill_level OR c.difficulty IS NULL)
                    ORDER BY ve.embedding <=> CAST(:query_embedding AS vector)
                    LIMIT :limit
                """),
                {
                    "query_embedding": embedding_str,
                    "skill_level": skill_level,
                    "limit": limit
                }
            )
            
            suggestions = []
            for row in results:
                if row.similarity and row.similarity > 0.3:  # Similarity threshold
                    suggestions.append(LearningMaterial(
                        title=row.title,
                        url=row.url,
                        platform=row.platform,
                        type="course",
                        estimated_hours=row.duration_hours,
                        description=row.description[:200] if row.description else None
                    ))
            
            return suggestions
        except Exception as e:
            print(f"Error searching local database: {str(e)}")
            # Rollback the transaction to clear the error state
            try:
                db.rollback()
            except Exception:
                pass
            # Fallback to text-based search
            return await self._text_search_database(db, query, skill_level, limit)
    
    async def _text_search_database(
        self,
        db: Session,
        query: str,
        skill_level: str,
        limit: int
    ) -> List[LearningMaterial]:
        """
        Fallback text-based search if vector search fails
        """
        try:
            query_lower = query.lower()
            query_terms = query_lower.split()
            
            # Search in title, description, and topics
            courses = db.query(Course).filter(
                Course.difficulty == skill_level
            ).all()
            
            # Simple relevance scoring
            scored_courses = []
            for course in courses:
                score = 0
                title_lower = course.title.lower()
                desc_lower = (course.description or "").lower()
                topics_lower = " ".join(course.topics or []).lower()
                
                for term in query_terms:
                    if term in title_lower:
                        score += 3
                    if term in desc_lower:
                        score += 2
                    if term in topics_lower:
                        score += 1
                
                if score > 0:
                    scored_courses.append((score, course))
            
            # Sort by score and return top results
            scored_courses.sort(key=lambda x: x[0], reverse=True)
            
            suggestions = []
            for score, course in scored_courses[:limit]:
                suggestions.append(LearningMaterial(
                    title=course.title,
                    url=course.url,
                    platform=course.platform,
                    type="course",
                    estimated_hours=course.duration_hours,
                    description=course.description[:200] if course.description else None
                ))
            
            return suggestions
        except Exception as e:
            print(f"Error in text search: {str(e)}")
            # Rollback the transaction to clear the error state
            try:
                db.rollback()
            except Exception:
                pass
            return []
    
    async def _llm_suggest_courses(
        self,
        module_name: str,
        module_description: str,
        skill_level: str,
        limit: int
    ) -> List[LearningMaterial]:
        """
        Use LLM to suggest courses based on module content
        Note: These are suggestions that may need validation
        """
        system_prompt = (
            "You are an expert course recommender. Suggest relevant online courses "
            "(Udemy, Coursera, YouTube, freeCodeCamp, etc.) based on the module content. "
            "Return course suggestions with title, URL, platform, and description."
        )
        
        user_prompt = f"""Module: {module_name}
Description: {module_description}
Skill Level: {skill_level}

Suggest {limit} relevant online courses that would help someone learn this module.
For each course, provide:
- title: Course title
- url: Course URL (use realistic URLs like https://www.udemy.com/course/example or https://www.coursera.org/learn/example)
- platform: Platform name (udemy, coursera, youtube, freecodecamp, etc.)
- description: Brief description
- estimated_hours: Estimated duration in hours

Return as JSON array of course objects."""
        
        try:
            # Use structured output to get course suggestions
            # Since we can't guarantee URLs exist, we'll use a flexible schema
            from typing import Any
            
            # Create a flexible schema for LLM suggestions
            class CourseSuggestion(BaseModel):
                title: str
                url: str
                platform: str
                description: str
                estimated_hours: Optional[int] = None
            
            class CourseSuggestionsList(BaseModel):
                courses: List[CourseSuggestion]
            
            result = await generate_structured(
                prompt=f"{system_prompt}\n\n{user_prompt}",
                schema=CourseSuggestionsList
            )
            
            suggestions = []
            for course in result.courses:
                suggestions.append(LearningMaterial(
                    title=course.title,
                    url=course.url,
                    platform=course.platform,
                    type="course",
                    estimated_hours=course.estimated_hours,
                    description=course.description
                ))
            
            return suggestions
        except Exception as e:
            print(f"Error getting LLM suggestions: {str(e)}")
            return []

