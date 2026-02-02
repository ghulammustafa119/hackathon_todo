# AI Provider Migration Guide

## Migration from Hugging Face to Cohere

This project has migrated from Hugging Face to Cohere for AI chatbot functionality. This change was made to support reliable AI service with consistent availability while maintaining the stateless architecture.

### Changes Made

1. **Agent Replacement**: Replaced `HuggingFaceChatbotAgent` with `CohereChatbotAgent`
2. **Dependencies**: Added Cohere Python SDK, removed Hugging Face specific dependencies
3. **Configuration**: Updated environment variables from Hugging Face to Cohere
4. **API Calls**: Adapted tool calling mechanism for Cohere models

### New Configuration

Environment variables for Cohere integration:

```bash
# Cohere Configuration
COHERE_API_KEY=your_cohere_api_key_here
```

### Key Features Maintained

- ✅ Stateless architecture (no conversation memory)
- ✅ JWT per-request authentication
- ✅ MCP tool integration for task operations
- ✅ User isolation and security
- ✅ All existing functionality preserved

### Deployment Notes

- The backend is now suitable for deployment with Cohere API
- Frontend remains compatible with Vercel deployment
- All stateless architecture principles maintained
- No session or memory storage used

### Environment Variables

The following environment variables need to be configured for the Cohere integration:

- `COHERE_API_KEY`: Your Cohere API key

### Migration Steps

1. Install the Cohere Python SDK: `pip install cohere`
2. Create a Cohere service module (`services/cohere_client.py`)
3. Update the AI agent to use Cohere API instead of Hugging Face
4. Update configuration to use COHERE_API_KEY
5. Modify API endpoint to use Cohere service
6. Update error handling for Cohere API responses

### Key Benefits

- Reliable API with consistent uptime
- Well-documented Python SDK
- Good performance for task management conversations
- Clear pricing model
- No model availability issues