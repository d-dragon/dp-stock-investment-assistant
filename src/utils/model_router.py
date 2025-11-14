"""
Multi-Model Router for AI-Assisted Development

This module provides intelligent routing of programming tasks to specialized AI models
based on task type, complexity, and model strengths.

Usage:
    from src.utils.model_router import ModelRouter
    
    router = ModelRouter()
    result = await router.route_task(
        task_type='code_generation',
        description='Create a FastAPI endpoint',
        context={'file_path': 'src/api/routes.py'}
    )
"""

import os
import yaml
import logging
from typing import Dict, List, Optional, Any, Literal
from dataclasses import dataclass
from pathlib import Path
import re
from enum import Enum

logger = logging.getLogger(__name__)


class TaskType(Enum):
    """Enumeration of supported task types"""
    ARCHITECTURE = "architecture"
    CODE_GENERATION = "code_generation"
    DEBUGGING = "debugging"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    REFACTORING = "refactoring"
    UNKNOWN = "unknown"


class ComplexityLevel(Enum):
    """Enumeration of task complexity levels"""
    SIMPLE = "simple"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class ModelConfig:
    """Configuration for an AI model"""
    name: str
    provider: str
    api_endpoint: str
    context_window: int
    cost_per_1m_input_tokens: float
    cost_per_1m_output_tokens: float
    strengths: List[str]


@dataclass
class RoutingResult:
    """Result of model routing"""
    model_name: str
    provider: str
    strategy: str
    fallback_models: List[str]
    estimated_cost: float
    reasoning: str


class ModelRouter:
    """
    Intelligently routes programming tasks to appropriate AI models
    based on configuration and task characteristics.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the ModelRouter with configuration.
        
        Args:
            config_path: Path to the YAML configuration file.
                        Defaults to .github/copilot-model-config.yaml
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / ".github" / "copilot-model-config.yaml"
        
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.models = self._initialize_models()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Loaded model configuration from {self.config_path}")
            return config
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {self.config_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML configuration: {e}")
            raise
    
    def _initialize_models(self) -> Dict[str, ModelConfig]:
        """Initialize model configurations from config"""
        models = {}
        
        # Add primary model
        primary = self.config.get('primary_model', {})
        if primary:
            models[primary['name']] = ModelConfig(**primary)
        
        # Add fallback models
        for fallback in self.config.get('fallback_models', []):
            models[fallback['name']] = ModelConfig(**fallback)
        
        # Add specialized models
        for task_type, spec in self.config.get('specialized_models', {}).items():
            if 'name' in spec:
                model_name = spec['name']
                if model_name not in models and 'provider' in spec:
                    # Create ModelConfig from specialized model data
                    models[model_name] = ModelConfig(
                        name=model_name,
                        provider=spec['provider'],
                        api_endpoint=spec.get('api_endpoint', ''),
                        context_window=spec.get('context_window', 100000),
                        cost_per_1m_input_tokens=spec.get('cost_per_1m_input_tokens', 0.0),
                        cost_per_1m_output_tokens=spec.get('cost_per_1m_output_tokens', 0.0),
                        strengths=spec.get('use_cases', [])
                    )
        
        logger.info(f"Initialized {len(models)} models: {list(models.keys())}")
        return models
    
    def detect_task_type(self, description: str, context: Optional[Dict[str, Any]] = None) -> TaskType:
        """
        Detect task type from description and context.
        
        Args:
            description: Natural language description of the task
            context: Additional context (file paths, etc.)
            
        Returns:
            Detected TaskType
        """
        description_lower = description.lower()
        
        # Get detection patterns from config
        detection = self.config.get('task_detection', {})
        
        # Check keywords for each task type
        for task_type, patterns in detection.items():
            keywords = patterns.get('keywords', [])
            
            # Check if any keyword matches
            for keyword in keywords:
                if keyword.lower() in description_lower:
                    try:
                        return TaskType(task_type)
                    except ValueError:
                        continue
            
            # Check file patterns if context provided
            if context and 'file_path' in context:
                file_path = context['file_path']
                file_patterns = patterns.get('file_patterns', [])
                
                for pattern in file_patterns:
                    # Convert glob pattern to regex
                    regex_pattern = pattern.replace('**', '.*').replace('*', '[^/]*')
                    if re.match(regex_pattern, file_path):
                        try:
                            return TaskType(task_type)
                        except ValueError:
                            continue
        
        return TaskType.UNKNOWN
    
    def estimate_complexity(
        self,
        description: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ComplexityLevel:
        """
        Estimate task complexity based on description and context.
        
        Args:
            description: Natural language description of the task
            context: Additional context
            
        Returns:
            Estimated ComplexityLevel
        """
        # Simple heuristics for complexity estimation
        word_count = len(description.split())
        
        # Check for complexity indicators
        high_complexity_indicators = [
            'architecture', 'refactor', 'redesign', 'migrate', 'optimize',
            'distributed', 'scalable', 'concurrent', 'async', 'parallel'
        ]
        
        medium_complexity_indicators = [
            'implement', 'integrate', 'connect', 'api', 'database',
            'authentication', 'validation', 'error handling'
        ]
        
        description_lower = description.lower()
        
        # Check for high complexity
        if any(indicator in description_lower for indicator in high_complexity_indicators):
            return ComplexityLevel.HIGH
        
        # Check for medium complexity
        if any(indicator in description_lower for indicator in medium_complexity_indicators):
            return ComplexityLevel.MEDIUM
        
        # Check context
        if context:
            lines = context.get('lines_of_code', 0)
            if lines > 200:
                return ComplexityLevel.HIGH
            elif lines > 50:
                return ComplexityLevel.MEDIUM
        
        # Default to simple for short descriptions
        if word_count < 20:
            return ComplexityLevel.SIMPLE
        
        return ComplexityLevel.MEDIUM
    
    def select_model(
        self,
        task_type: TaskType,
        complexity: ComplexityLevel,
        context: Optional[Dict[str, Any]] = None
    ) -> RoutingResult:
        """
        Select the most appropriate model for the task.
        
        Args:
            task_type: Type of task
            complexity: Task complexity level
            context: Additional context
            
        Returns:
            RoutingResult with selected model and reasoning
        """
        # Get specialized model for task type
        specialized_models = self.config.get('specialized_models', {})
        
        if task_type != TaskType.UNKNOWN and task_type.value in specialized_models:
            model_config = specialized_models[task_type.value]
            model_name = model_config['name']
            
            # Check complexity requirements
            min_complexity = model_config.get('min_complexity', 'simple')
            
            # Get fallback models
            fallback_models = [
                fb['name'] for fb in self.config.get('fallback_models', [])
            ]
            
            # Determine strategy based on complexity
            if complexity == ComplexityLevel.SIMPLE:
                strategy = 'use_specialized'
            elif complexity == ComplexityLevel.MEDIUM:
                strategy = 'specialized_with_validation'
            else:
                strategy = 'multi_model_consultation'
            
            reasoning = (
                f"Selected {model_name} for {task_type.value} task "
                f"with {complexity.value} complexity. "
                f"Strategy: {strategy}"
            )
            
            return RoutingResult(
                model_name=model_name,
                provider=model_config['provider'],
                strategy=strategy,
                fallback_models=fallback_models,
                estimated_cost=0.0,  # TODO: Calculate based on expected tokens
                reasoning=reasoning
            )
        
        # Fallback to primary model
        primary_model = self.config.get('primary_model', {})
        model_name = primary_model.get('name', 'claude-sonnet-4.5')
        
        fallback_models = [
            fb['name'] for fb in self.config.get('fallback_models', [])
        ]
        
        reasoning = (
            f"Using primary model {model_name} for {task_type.value} task "
            f"(no specialized model configured)"
        )
        
        return RoutingResult(
            model_name=model_name,
            provider=primary_model.get('provider', 'anthropic'),
            strategy='use_primary',
            fallback_models=fallback_models,
            estimated_cost=0.0,
            reasoning=reasoning
        )
    
    def route_task(
        self,
        description: str,
        task_type: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> RoutingResult:
        """
        Route a task to the appropriate model.
        
        Args:
            description: Natural language description of the task
            task_type: Optional explicit task type (overrides detection)
            context: Additional context
            
        Returns:
            RoutingResult with selected model and routing information
        """
        # Detect or use provided task type
        if task_type:
            try:
                detected_type = TaskType(task_type)
            except ValueError:
                logger.warning(f"Invalid task type '{task_type}', detecting from description")
                detected_type = self.detect_task_type(description, context)
        else:
            detected_type = self.detect_task_type(description, context)
        
        logger.info(f"Detected task type: {detected_type.value}")
        
        # Estimate complexity
        complexity = self.estimate_complexity(description, context)
        logger.info(f"Estimated complexity: {complexity.value}")
        
        # Select model
        result = self.select_model(detected_type, complexity, context)
        
        logger.info(f"Routing result: {result.reasoning}")
        
        return result
    
    def get_fallback_chain(self) -> List[str]:
        """
        Get the configured fallback chain.
        
        Returns:
            List of model names in fallback order
        """
        strategy = self.config.get('fallback_strategy', {})
        return strategy.get('cascade_order', [])
    
    def get_model_info(self, model_name: str) -> Optional[ModelConfig]:
        """
        Get information about a specific model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            ModelConfig if found, None otherwise
        """
        return self.models.get(model_name)


# Example usage
if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize router
    router = ModelRouter()
    
    # Example 1: Code generation task
    result = router.route_task(
        description="Create a new FastAPI endpoint for fetching stock data",
        context={'file_path': 'src/api/routes.py'}
    )
    print(f"\nExample 1: {result.reasoning}")
    print(f"Model: {result.model_name}, Strategy: {result.strategy}")
    
    # Example 2: Debugging task
    result = router.route_task(
        description="Fix the MongoDB authentication error in the repository",
        task_type="debugging"
    )
    print(f"\nExample 2: {result.reasoning}")
    print(f"Model: {result.model_name}, Strategy: {result.strategy}")
    
    # Example 3: Testing task
    result = router.route_task(
        description="Generate comprehensive unit tests for the data manager",
        context={'file_path': 'tests/test_data_manager.py', 'lines_of_code': 150}
    )
    print(f"\nExample 3: {result.reasoning}")
    print(f"Model: {result.model_name}, Strategy: {result.strategy}")
    
    # Get fallback chain
    chain = router.get_fallback_chain()
    print(f"\nFallback chain: {' -> '.join(chain)}")
