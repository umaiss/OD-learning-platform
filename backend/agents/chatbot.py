from typing import Dict, List, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from core.llm import llm_provider
from core.llm_ollama import generate_text
from core.embeddings import generate_embedding
from sqlalchemy.orm import Session
from sqlalchemy import text
from db.vector import VectorEmbedding


class ChatbotAgent:
    """Agent for conversational learning assistance"""
    
    def __init__(self):
        self.llm = llm_provider.get_default_llm()
        self.parser = StrOutputParser()
        self.system_prompt = """You are a helpful learning assistant for an online learning platform. 
        You help users with:
        - Answering questions about learning content
        - Providing explanations and clarifications
        - Suggesting learning resources
        - Guiding users through their learning journey
        - Offering encouragement and motivation
        
        Be friendly, clear, and supportive. If you don't know something, admit it and suggest 
        how the user might find the answer."""
        self.skillpilot_prompt = (
            "You are SkillPilot AI Coach. Be friendly, explain clearly, and give actionable guidance."
        )
    
    async def chat_with_context(
        self,
        message: str,
        skill_map: Optional[Dict[str, str]] = None,
        learning_plan: Optional[Dict] = None,
        conversation_history: Optional[List[Dict]] = None,
        db: Optional[Session] = None
    ) -> str:
        """
        Chat with context-aware responses using skill map, learning plan, and vector retrieval
        
        Args:
            message: User's message/question
            skill_map: Dictionary mapping skill names to levels
            learning_plan: Learning plan dictionary with modules, goals, etc.
            conversation_history: Previous conversation messages
            db: Database session for vector retrieval
        
        Returns:
            Assistant's response
        """
        # Retrieve relevant content from vector database if available
        retrieved_content = []
        if db:
            retrieved_content = await self._retrieve_relevant_content(message, db, limit=3)
        
        # Build context string
        context_parts = []
        
        if skill_map:
            context_parts.append(f"Learner's Skill Map: {skill_map}")
        
        if learning_plan:
            plan_summary = self._summarize_learning_plan(learning_plan)
            context_parts.append(f"Current Learning Plan: {plan_summary}")
        
        if retrieved_content:
            context_parts.append("Relevant Content from Knowledge Base:")
            for i, content in enumerate(retrieved_content, 1):
                context_parts.append(f"{i}. {content}")
        
        context_str = "\n".join(context_parts) if context_parts else None
        
        # Build conversation history
        history_text = ""
        if conversation_history:
            history_lines = []
            for msg in conversation_history[-5:]:  # Last 5 messages for context
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "user":
                    history_lines.append(f"User: {content}")
                elif role == "assistant":
                    history_lines.append(f"Assistant: {content}")
            history_text = "\n".join(history_lines)
        
        # Build the full prompt
        prompt_parts = [self.skillpilot_prompt]
        
        if context_str:
            prompt_parts.append(f"\nContext:\n{context_str}")
        
        if history_text:
            prompt_parts.append(f"\nConversation History:\n{history_text}")
        
        prompt_parts.append(f"\nUser Question: {message}")
        prompt_parts.append("\nProvide a helpful, clear, and actionable response. If you reference content from the knowledge base, cite it naturally.")
        
        full_prompt = "\n".join(prompt_parts)
        
        # Generate response using Ollama
        response = await generate_text(full_prompt)
        
        return response
    
    async def _retrieve_relevant_content(
        self,
        query: str,
        db: Session,
        limit: int = 3
    ) -> List[str]:
        """
        Retrieve relevant content from vector database using semantic search
        
        Args:
            query: User's query/question
            db: Database session
            limit: Maximum number of results to return
        
        Returns:
            List of relevant content text snippets
        """
        try:
            # Generate embedding for the query
            query_embedding = await generate_embedding(query)
            
            # Use vector similarity search with cosine distance (<=> operator)
            # 1 - (embedding <=> query_embedding) gives cosine similarity
            # Higher similarity = more relevant
            # Convert list to string format for SQL query
            embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"
            
            results = db.execute(
                text("""
                    SELECT text, 
                           1 - (embedding <=> CAST(:query_embedding AS vector)) as similarity
                    FROM vector_embeddings
                    WHERE embedding IS NOT NULL
                    ORDER BY embedding <=> CAST(:query_embedding AS vector)
                    LIMIT :limit
                """),
                {
                    "query_embedding": embedding_str,
                    "limit": limit
                }
            )
            
            # Extract results
            retrieved = []
            for row in results:
                similarity = row.similarity
                text_content = row.text
                # Only include results with reasonable similarity (threshold: 0.3)
                if similarity and similarity > 0.3:
                    retrieved.append(text_content[:500])  # Limit text length
            
            # If vector search didn't return enough results, fallback to text search
            if len(retrieved) < limit:
                text_results = db.query(VectorEmbedding).filter(
                    VectorEmbedding.text.ilike(f"%{query[:30]}%")
                ).limit(limit - len(retrieved)).all()
                
                for result in text_results:
                    if result.text not in retrieved:  # Avoid duplicates
                        retrieved.append(result.text[:500])
            
            # Final fallback: get recent content if still not enough
            if len(retrieved) < limit:
                recent_results = db.query(VectorEmbedding).order_by(
                    VectorEmbedding.created_at.desc()
                ).limit(limit - len(retrieved)).all()
                
                for result in recent_results:
                    if result.text not in retrieved:  # Avoid duplicates
                        retrieved.append(result.text[:500])
            
            return retrieved
        except Exception as e:
            # If vector search fails, fallback to text-based search
            print(f"Vector retrieval error: {e}, falling back to text search")
            try:
                results = db.query(VectorEmbedding).filter(
                    VectorEmbedding.text.ilike(f"%{query[:30]}%")
                ).limit(limit).all()
                
                if not results:
                    results = db.query(VectorEmbedding).order_by(
                        VectorEmbedding.created_at.desc()
                    ).limit(limit).all()
                
                return [result.text[:500] for result in results]
            except Exception as fallback_error:
                print(f"Fallback search also failed: {fallback_error}")
                return []
    
    def _summarize_learning_plan(self, learning_plan: Dict) -> str:
        """
        Summarize learning plan for context
        
        Args:
            learning_plan: Learning plan dictionary
        
        Returns:
            String summary of the learning plan
        """
        summary_parts = []
        
        if "duration_weeks" in learning_plan:
            summary_parts.append(f"Duration: {learning_plan['duration_weeks']} weeks")
        
        if "weekly_goals" in learning_plan:
            summary_parts.append(f"Weekly Goals: {', '.join(learning_plan['weekly_goals'][:3])}")
        
        if "modules" in learning_plan:
            module_names = [m.get("name", "Unknown") for m in learning_plan["modules"][:5]]
            summary_parts.append(f"Modules: {', '.join(module_names)}")
        
        return "; ".join(summary_parts) if summary_parts else str(learning_plan)
    
    async def chat(
        self,
        message: str,
        conversation_history: Optional[List[Dict]] = None,
        context: Optional[Dict] = None
    ) -> str:
        """
        Generate a chat response
        
        Args:
            message: User's message
            conversation_history: Previous conversation messages
            context: Additional context (user progress, current module, etc.)
        
        Returns:
            Assistant's response
        """
        messages = [SystemMessage(content=self.system_prompt)]
        
        # Add context if provided
        if context:
            context_str = f"Context: {str(context)}"
            messages.append(SystemMessage(content=context_str))
        
        # Add conversation history
        if conversation_history:
            for msg in conversation_history:
                if msg.get("role") == "user":
                    messages.append(HumanMessage(content=msg.get("content", "")))
                elif msg.get("role") == "assistant":
                    messages.append(AIMessage(content=msg.get("content", "")))
        
        # Add current message
        messages.append(HumanMessage(content=message))
        
        # Generate response
        response = await self.llm.ainvoke(messages)
        
        return response.content if hasattr(response, 'content') else str(response)
    
    async def answer_question(
        self,
        question: str,
        topic: Optional[str] = None,
        difficulty: Optional[str] = None
    ) -> Dict:
        """
        Answer a specific question with detailed explanation
        
        Args:
            question: User's question
            topic: Related topic
            difficulty: Difficulty level for explanation
        
        Returns:
            Dictionary with answer and explanation
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert tutor. Provide clear, detailed answers to questions. 
            Return a JSON object with: answer, explanation, examples (array), related_topics (array), 
            and further_reading (array)."""),
            ("user", """Question: {question}
            Topic: {topic}
            Difficulty Level: {difficulty}""")
        ])
        
        from langchain_core.output_parsers import JsonOutputParser
        json_parser = JsonOutputParser()
        
        chain = prompt | self.llm | json_parser
        
        result = await chain.ainvoke({
            "question": question,
            "topic": topic or "general",
            "difficulty": difficulty or "intermediate"
        })
        
        return result
    
    async def provide_hint(
        self,
        problem: str,
        user_attempt: Optional[str] = None,
        hints_given: int = 0
    ) -> Dict:
        """
        Provide a hint for a problem without giving away the solution
        
        Args:
            problem: The problem or question
            user_attempt: User's current attempt (if any)
            hints_given: Number of hints already given
        
        Returns:
            Dictionary with hint and guidance
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Provide a helpful hint that guides the user toward the solution 
            without giving it away. Return a JSON object with: hint, guidance, and next_step_suggestion."""),
            ("user", """Problem: {problem}
            User Attempt: {attempt}
            Hints Given: {hints}""")
        ])
        
        from langchain_core.output_parsers import JsonOutputParser
        json_parser = JsonOutputParser()
        
        chain = prompt | self.llm | json_parser
        
        result = await chain.ainvoke({
            "problem": problem,
            "attempt": user_attempt or "No attempt yet",
            "hints": hints_given
        })
        
        return result

