# Vector Search Implementation Guide

## Overview

The platform now includes **full vector search functionality** using PGVector and Ollama embeddings. This enables semantic search capabilities that make the chatbot more contextually aware and helpful.

## How It Works

### 1. Embedding Generation
- Uses Ollama's `nomic-embed-text` model to generate 768-dimensional embeddings
- Embeddings are created automatically when content is generated
- Stored in the `vector_embeddings` table with metadata

### 2. Content Indexing
Embeddings are automatically created for:
- **Lesson Content**: When `/api/v1/content/generate` is called
- **Learning Plans**: When `/api/v1/learning-path/generate` is called
- **Skill Profiles**: When `/api/v1/profile/save` is called

### 3. Semantic Search
- When users chat with the AI coach, their queries are embedded
- Vector similarity search finds the most relevant content using cosine distance
- Retrieved content is used as context for more accurate responses

## Architecture

### Files Created/Modified

1. **`core/embeddings.py`**: 
   - `generate_embedding(text)` - Generates embeddings using Ollama API
   - `generate_embeddings_batch(texts)` - Batch embedding generation

2. **`core/vector_utils.py`**:
   - `create_vector_embedding()` - Creates and saves embeddings to database
   - `create_embeddings_for_content()` - Helper for automatic embedding creation

3. **`agents/chatbot.py`** (Updated):
   - `_retrieve_relevant_content()` - Now uses real vector similarity search
   - Falls back to text search if vector search fails

4. **Routers Updated**:
   - `routers/content.py` - Creates embeddings for lessons and quizzes
   - `routers/learning_path.py` - Creates embeddings for learning plans
   - `routers/profile.py` - Creates embeddings for skill profiles

## Configuration

### Environment Variables

Add to your `.env` file:

```bash
# Ollama Configuration
OLLAMA_MODEL=llama3.1                    # LLM model for text generation
OLLAMA_EMBEDDING_MODEL=nomic-embed-text   # Embedding model
OLLAMA_BASE_URL=http://localhost:11434    # Ollama server URL

# Vector Database
VECTOR_DIMENSION=768                      # Embedding dimension (768 for nomic-embed-text)
```

### Setup Steps

1. **Install Ollama**:
   ```bash
   # Download from https://ollama.ai
   # Or use: curl -fsSL https://ollama.ai/install.sh | sh
   ```

2. **Pull Required Models**:
   ```bash
   ollama pull llama3.1
   ollama pull nomic-embed-text
   ```

3. **Start Ollama** (if not running as service):
   ```bash
   ollama serve
   ```

4. **Verify Setup**:
   ```bash
   curl http://localhost:11434/api/tags  # Should list installed models
   ```

## Usage

### Automatic Embedding Creation

No manual steps required! Embeddings are created automatically when:

1. **Generating Content**:
   ```bash
   POST /api/v1/content/generate
   # Automatically creates embeddings for lesson text and quiz questions
   ```

2. **Generating Learning Path**:
   ```bash
   POST /api/v1/learning-path/generate
   # Automatically creates embedding for the learning plan
   ```

3. **Saving Profile**:
   ```bash
   POST /api/v1/profile/save
   # Automatically creates embedding for the skill profile
   ```

### Chatbot with Vector Search

The chatbot automatically uses vector search:

```bash
POST /api/v1/chatbot/chat
{
  "learner_id": 1,
  "message": "What should I learn about React hooks?",
  "conversation_history": []
}
```

**What happens:**
1. Query is embedded: `"What should I learn about React hooks?"` → embedding vector
2. Vector search finds similar content from stored lessons/plans/profiles
3. Retrieved content is added as context to the LLM prompt
4. Response is more accurate and contextually relevant

## Vector Search Query

The chatbot uses this SQL query for semantic search:

```sql
SELECT text, 
       1 - (embedding <=> :query_embedding::vector) as similarity
FROM vector_embeddings
WHERE embedding IS NOT NULL
ORDER BY embedding <=> :query_embedding::vector
LIMIT :limit
```

- `<=>` is the cosine distance operator in pgvector
- `1 - distance` gives cosine similarity (higher = more similar)
- Results are filtered by similarity threshold (0.3 minimum)

## Troubleshooting

### Embeddings Not Created

**Symptom**: Chatbot doesn't find relevant content

**Solutions**:
1. Check Ollama is running: `curl http://localhost:11434/api/tags`
2. Verify model is installed: `ollama list`
3. Check logs for embedding errors (they're non-blocking)
4. Verify `VECTOR_DIMENSION` matches your embedding model (768 for nomic-embed-text)

### Slow Embedding Generation

**Symptom**: API calls take longer than expected

**Solutions**:
1. Use a faster embedding model (nomic-embed-text is already fast)
2. Consider batch processing for multiple embeddings
3. Cache embeddings for frequently accessed content

### Vector Search Returns No Results

**Symptom**: Chatbot says "I don't have information about that"

**Solutions**:
1. Verify embeddings exist: `SELECT COUNT(*) FROM vector_embeddings;`
2. Check similarity threshold (currently 0.3) - may need adjustment
3. Ensure content was generated after vector search was implemented
4. Check that pgvector extension is enabled in Supabase

## Performance Considerations

1. **Embedding Generation**: ~100-500ms per text (depends on length and model)
2. **Vector Search**: ~10-50ms for similarity search (very fast with pgvector)
3. **Storage**: Each embedding uses ~3KB (768 floats × 4 bytes)

## Future Enhancements

Potential improvements:
- [ ] Batch embedding generation for better performance
- [ ] Embedding caching for frequently accessed content
- [ ] Hybrid search (vector + keyword) for better results
- [ ] Re-ranking of search results using LLM
- [ ] Embedding updates when content is modified

## Dependencies

Added to `requirements.txt`:
- `aiohttp==3.10.11` - For async HTTP requests to Ollama API

## Summary

✅ **Fully Implemented**:
- Embedding generation using Ollama
- Automatic embedding creation for all content types
- Vector similarity search in chatbot
- Fallback to text search if vector search fails
- Error handling and logging

The vector database is now **fully utilized** and helping the chatbot provide more contextually relevant responses!

