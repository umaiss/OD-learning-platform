"""
Embedding generation utility using Ollama
"""
import os
import asyncio
import aiohttp
from typing import List
from core.config import settings


async def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding vector for text using Ollama
    
    Args:
        text: Input text to embed
        
    Returns:
        List[float]: Embedding vector (list of floats)
    """
    # Use Ollama's embedding model (default: nomic-embed-text)
    # You can change this via OLLAMA_EMBEDDING_MODEL env var
    embedding_model = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{ollama_url}/api/embeddings",
                json={
                    "model": embedding_model,
                    "prompt": text
                },
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    embedding = data.get("embedding", [])
                    
                    # Ensure the embedding matches the expected dimension
                    if len(embedding) != settings.vector_dimension:
                        # If dimension mismatch, pad or truncate
                        if len(embedding) < settings.vector_dimension:
                            embedding.extend([0.0] * (settings.vector_dimension - len(embedding)))
                        else:
                            embedding = embedding[:settings.vector_dimension]
                    
                    return embedding
                else:
                    error_text = await response.text()
                    raise Exception(f"Ollama API error: {response.status} - {error_text}")
    except aiohttp.ClientError as e:
        raise Exception(f"Failed to connect to Ollama: {str(e)}")
    except Exception as e:
        raise Exception(f"Error generating embedding: {str(e)}")


async def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for multiple texts (batch processing)
    
    Args:
        texts: List of input texts to embed
        
    Returns:
        List[List[float]]: List of embedding vectors
    """
    tasks = [generate_embedding(text) for text in texts]
    return await asyncio.gather(*tasks)

