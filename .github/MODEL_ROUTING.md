# Multi-Model Routing Configuration

This directory contains configuration and implementation for intelligent routing of programming tasks to specialized AI models.

## Overview

The multi-model routing system enables intelligent selection of AI models based on:
- **Task Type**: Architecture, code generation, debugging, testing, documentation
- **Complexity**: Simple, medium, or high complexity tasks
- **Context**: File paths, code patterns, and other contextual information

## Files

- **`copilot-model-config.yaml`**: Configuration file defining models, routing rules, and task detection patterns
- **`../src/utils/model_router.py`**: Python implementation for programmatic model routing
- **`chatmodes/Multi-model-sw-enginerring-assitant-1.md`**: GitHub Copilot chat mode instructions

## Configuration Structure

### Model Definitions

```yaml
primary_model:
  name: 'claude-sonnet-4.5'
  provider: 'anthropic'
  # ... other properties

fallback_models:
  - name: 'gpt-5-codex'
    provider: 'openai'
    priority: 1

specialized_models:
  architecture:
    name: 'claude-sonnet-4.5'
    use_cases:
      - 'system design'
      - 'technical planning'
```

### Routing Rules

```yaml
routing_rules:
  - name: 'simple_tasks'
    conditions:
      max_lines: 50
      complexity: 'simple'
    strategy: 'use_primary'
    
  - name: 'complex_problems'
    conditions:
      min_lines: 200
      complexity: 'high'
    strategy: 'multi_model_consultation'
```

### Task Detection

```yaml
task_detection:
  architecture:
    keywords:
      - 'design'
      - 'architecture'
    file_patterns:
      - 'architecture/**'
```

## Usage

### Python API

```python
from src.utils.model_router import ModelRouter

# Initialize router
router = ModelRouter()

# Route a task
result = router.route_task(
    description="Create a new FastAPI endpoint for stock data",
    context={'file_path': 'src/api/routes.py'}
)

print(f"Selected model: {result.model_name}")
print(f"Strategy: {result.strategy}")
print(f"Reasoning: {result.reasoning}")
```

### With LangChain

```python
from langchain.chat_models import ChatAnthropic, ChatOpenAI
from src.utils.model_router import ModelRouter
import os

# Initialize router
router = ModelRouter()

# Initialize models
models = {
    'claude-sonnet-4.5': ChatAnthropic(
        model='claude-sonnet-4-20250514',
        api_key=os.getenv('ANTHROPIC_API_KEY')
    ),
    'gpt-5-codex': ChatOpenAI(
        model='gpt-4-turbo',
        api_key=os.getenv('OPENAI_API_KEY')
    ),
}

# Route and execute
result = router.route_task(
    description="Design a microservice architecture",
    task_type="architecture"
)

model = models[result.model_name]
response = model.invoke("Design a microservice architecture for stock analysis")
print(response.content)
```

### With Custom Extension

```python
import vscode
from src.utils.model_router import ModelRouter

class MultiModelExtension:
    def __init__(self):
        self.router = ModelRouter()
    
    async def handle_request(self, request):
        # Get active file context
        editor = vscode.window.activeTextEditor
        context = {
            'file_path': editor.document.fileName,
            'lines_of_code': editor.document.lineCount
        }
        
        # Route task
        result = self.router.route_task(
            description=request.prompt,
            context=context
        )
        
        # Call appropriate model API
        response = await self.call_model(result.model_name, request.prompt)
        return response
```

## Environment Variables

Set the following environment variables for API access:

```bash
# Anthropic (Claude)
export ANTHROPIC_API_KEY="your-anthropic-api-key"

# OpenAI (GPT)
export OPENAI_API_KEY="your-openai-api-key"

# Google (Gemini)
export GOOGLE_API_KEY="your-google-api-key"

# xAI (Grok)
export XAI_API_KEY="your-xai-api-key"
```

Or create a `.env` file:

```env
ANTHROPIC_API_KEY=your-anthropic-api-key
OPENAI_API_KEY=your-openai-api-key
GOOGLE_API_KEY=your-google-api-key
XAI_API_KEY=your-xai-api-key
```

## Model Selection Logic

### Task Type → Model Mapping

| Task Type | Primary Model | Reason |
|-----------|--------------|---------|
| Architecture | Claude Sonnet 4.5 | Superior reasoning and design capabilities |
| Code Generation | GPT-5 Codex | Advanced code synthesis and optimization |
| Debugging | Claude Sonnet 4.5 | Deep problem analysis and root cause identification |
| Testing | Gemini 2.5 Pro | Comprehensive test coverage and edge case detection |
| Documentation | Claude Haiku 4.5 | Fast, clear technical writing |

### Complexity-Based Routing

- **Simple** (<50 lines): Use specialized model directly
- **Medium** (50-200 lines): Use specialized model with validation from fallback
- **High** (>200 lines): Multi-model consultation with synthesis

## Customization

### Adding a New Model

1. Add to `copilot-model-config.yaml`:

```yaml
specialized_models:
  your_task_type:
    name: 'your-model-name'
    provider: 'your-provider'
    api_endpoint: 'https://api.provider.com/v1'
    context_window: 100000
    use_cases:
      - 'specific use case 1'
      - 'specific use case 2'
```

2. Update task detection patterns:

```yaml
task_detection:
  your_task_type:
    keywords:
      - 'keyword1'
      - 'keyword2'
    file_patterns:
      - 'your/path/**'
```

3. Test the configuration:

```python
router = ModelRouter()
result = router.route_task(
    description="Task with keyword1",
    task_type="your_task_type"
)
```

### Modifying Routing Rules

Edit `routing_rules` in `copilot-model-config.yaml`:

```yaml
routing_rules:
  - name: 'custom_rule'
    description: 'Your custom routing rule'
    conditions:
      max_lines: 100
      complexity: 'medium'
      custom_field: 'custom_value'
    strategy: 'your_strategy'
    model: 'your-model-name'
```

## Testing

Run the model router tests:

```bash
# Basic functionality test
python src/utils/model_router.py

# Unit tests (if created)
pytest tests/test_model_router.py
```

## Limitations

### Current GitHub Copilot Limitations

- ✅ **Supported**: Custom instructions in chat mode files
- ✅ **Supported**: Tool specifications
- ❌ **Not Yet Supported**: Custom model selection
- ❌ **Not Yet Supported**: Multi-model routing
- ❌ **Not Yet Supported**: Dynamic model switching

The configuration in this directory is designed to work with:
- Custom VS Code extensions
- LangChain-based implementations
- Direct API integrations
- Future GitHub Copilot features (when available)

### Workarounds

Until GitHub Copilot supports custom model routing:

1. **Use the Python API**: Implement routing in your own tools
2. **Build a VS Code Extension**: Create a custom extension using this configuration
3. **Use LangChain**: Orchestrate multiple models with LangChain
4. **External Service**: Create a routing service that wraps the model APIs

## Monitoring and Optimization

The configuration includes monitoring settings:

```yaml
monitoring:
  enabled: true
  track_metrics:
    - 'response_time'
    - 'token_usage'
    - 'cost_per_request'
    - 'success_rate'
```

Track model performance and optimize routing rules based on actual usage patterns.

## Security

API keys should never be committed to the repository:

- Use environment variables
- Add `.env` to `.gitignore`
- Use secure key management in production
- Enable data redaction for sensitive information

## Contributing

To contribute improvements:

1. Test your changes with the Python API
2. Update the configuration file
3. Update this README
4. Add examples demonstrating the new functionality

## References

- [Anthropic Claude API](https://docs.anthropic.com/claude/reference/getting-started-with-the-api)
- [OpenAI API](https://platform.openai.com/docs/api-reference)
- [Google Gemini API](https://ai.google.dev/docs)
- [xAI Grok API](https://docs.x.ai)
- [LangChain Documentation](https://python.langchain.com/docs/)
- [VS Code Extension API](https://code.visualstudio.com/api)

## Support

For issues or questions:
- Check the model router logs
- Verify API keys are set correctly
- Ensure configuration YAML is valid
- Review the examples in `model_router.py`
