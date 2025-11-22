"""
Ollama LLM client for text generation and structured output
"""
import json
import os
from typing import Optional, Type, TypeVar
from pydantic import BaseModel, ValidationError
from langchain_community.llms import Ollama
from langchain_core.language_models.llms import LLM

T = TypeVar('T', bound=BaseModel)


def get_llm() -> LLM:
    """
    Get an Ollama LLM instance
    
    Returns:
        LLM: Configured Ollama instance
    """
    model_name = os.getenv("OLLAMA_MODEL", "llama3.1")
    
    return Ollama(
        model=model_name,
        temperature=0.2,
        streaming=False
    )


async def generate_text(prompt: str) -> str:
    """
    Simple text completion using Ollama
    
    Args:
        prompt: The input prompt for text generation
        
    Returns:
        str: Generated text response
    """
    llm = get_llm()
    
    # Ollama's invoke is synchronous, but we wrap it in async for consistency
    # In practice, you might want to run this in a thread pool for true async
    response = await _run_async(llm.invoke, prompt)
    
    return response.strip() if isinstance(response, str) else str(response)


async def generate_structured(
    prompt: str, 
    schema: Type[T],
    retry_on_failure: bool = True
) -> T:
    """
    Generate structured JSON output validated against a Pydantic schema
    
    Args:
        prompt: The input prompt for generation
        schema: Pydantic BaseModel class to validate against
        retry_on_failure: Whether to retry once if validation fails
        
    Returns:
        T: Validated instance of the schema type
        
    Raises:
        ValueError: If validation fails after retries
    """
    llm = get_llm()
    
    # Create a prompt that asks for JSON only
    json_prompt = f"""You are a helpful assistant that returns ONLY valid JSON.
Do not include any markdown formatting, code blocks, or explanatory text.
Return ONLY the JSON object.

{prompt}

Return your response as a valid JSON object matching this structure:
{_get_schema_description(schema)}"""
    
    # First attempt
    response = await _run_async(llm.invoke, json_prompt)
    parsed_data = _extract_json(response)
    
    try:
        return schema(**parsed_data)
    except ValidationError as e:
        if not retry_on_failure:
            raise ValueError(f"Validation failed: {e}") from e
        
        # Retry with clarification
        clarification_prompt = f"""The previous response failed validation. 
Please return ONLY valid JSON that matches this exact schema:
{_get_schema_description(schema)}

Previous response (which was invalid):
{response}

Errors: {str(e)}

Please return ONLY the JSON object, no markdown, no code blocks, no explanation."""
        
        retry_response = await _run_async(llm.invoke, clarification_prompt)
        retry_parsed = _extract_json(retry_response)
        
        try:
            return schema(**retry_parsed)
        except ValidationError as retry_error:
            raise ValueError(
                f"Validation failed after retry. Original error: {e}. Retry error: {retry_error}"
            ) from retry_error


def _extract_json(text: str) -> dict:
    """
    Extract JSON from text, handling markdown code blocks
    
    Args:
        text: Text that may contain JSON
        
    Returns:
        dict: Parsed JSON object
        
    Raises:
        ValueError: If no valid JSON can be extracted
    """
    text = text.strip()
    
    # Remove markdown code blocks if present
    if text.startswith("```"):
        # Find the first newline after ```
        first_newline = text.find("\n")
        if first_newline != -1:
            text = text[first_newline + 1:]
        # Remove trailing ```
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
    
    # Try to find JSON object boundaries
    start_idx = text.find("{")
    end_idx = text.rfind("}")
    
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        json_str = text[start_idx:end_idx + 1]
    else:
        json_str = text
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON from response: {text[:200]}...") from e


def _get_schema_description(schema: Type[BaseModel]) -> str:
    """
    Get a human-readable description of a Pydantic schema
    
    Args:
        schema: Pydantic BaseModel class
        
    Returns:
        str: Schema description
    """
    try:
        # Get JSON schema
        json_schema = schema.model_json_schema()
        
        # Extract properties
        properties = json_schema.get("properties", {})
        required = json_schema.get("required", [])
        
        desc = "{\n"
        for field_name, field_info in properties.items():
            field_type = field_info.get("type", "unknown")
            is_required = field_name in required
            required_marker = " (required)" if is_required else " (optional)"
            desc += f'  "{field_name}": {field_type}{required_marker},\n'
        desc = desc.rstrip(",\n") + "\n}"
        
        return desc
    except Exception:
        # Fallback to model fields
        return str(schema.model_fields)


async def _run_async(func, *args, **kwargs):
    """
    Run a synchronous function asynchronously
    
    Args:
        func: Synchronous function to run
        *args: Positional arguments
        **kwargs: Keyword arguments
        
    Returns:
        Result of the function call
    """
    import asyncio
    
    # Use to_thread for Python 3.9+, fallback to run_in_executor
    try:
        # Python 3.9+ has asyncio.to_thread
        return await asyncio.to_thread(func, *args, **kwargs)
    except AttributeError:
        # Fallback for older Python versions
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))

