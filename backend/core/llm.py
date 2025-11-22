from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel
from core.config import settings


class LLMProvider:
    """LLM provider factory for managing different LLM instances"""
    
    def __init__(self):
        self._openai_llm: Optional[BaseChatModel] = None
        self._anthropic_llm: Optional[BaseChatModel] = None
    
    def get_openai_llm(
        self,
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> BaseChatModel:
        """Get or create OpenAI LLM instance"""
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        
        if self._openai_llm is None:
            self._openai_llm = ChatOpenAI(
                api_key=settings.openai_api_key,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )
        return self._openai_llm
    
    def get_anthropic_llm(
        self,
        model: str = "claude-3-sonnet-20240229",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> BaseChatModel:
        """Get or create Anthropic LLM instance"""
        if not settings.anthropic_api_key:
            raise ValueError("Anthropic API key not configured")
        
        if self._anthropic_llm is None:
            self._anthropic_llm = ChatAnthropic(
                api_key=settings.anthropic_api_key,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )
        return self._anthropic_llm
    
    def get_default_llm(self) -> BaseChatModel:
        """Get default LLM (prefers OpenAI, falls back to Anthropic)"""
        if settings.openai_api_key:
            return self.get_openai_llm()
        elif settings.anthropic_api_key:
            return self.get_anthropic_llm()
        else:
            raise ValueError("No LLM API keys configured")


# Global LLM provider instance
llm_provider = LLMProvider()

