---
description: Comprehensive testing strategy across all levels - unit, integration, E2E, performance, security, and language-specific testing conventions
applyTo: "tests/**"
---

# Testing Strategy and Conventions

## Testing Philosophy

### Core Principles
- **Test behavior, not implementation**: Focus on user-facing functionality and API contracts
- **Fast feedback loops**: Unit tests should complete in seconds; integration tests in minutes
- **Isolation**: Tests should not depend on external services, network, or shared state
- **Repeatability**: Tests produce consistent results regardless of execution order or environment
- **Meaningful coverage**: Test happy paths, edge cases, and error conditions; avoid vanity metrics
- **Test pyramid**: Many unit tests, fewer integration tests, minimal E2E tests

### Test Levels Overview
```
       /\
      /E2E\         ← Few (5-10% of tests)
     /------\       User workflows, UI → API → DB
    /  INT   \      ← Some (20-30% of tests)
   /----------\     API routes, service integration, DB repositories
  /   UNIT     \    ← Many (60-75% of tests)
 /--------------\   Pure functions, business logic, model clients
```

### Coverage Targets
- **Overall**: 80%+ line coverage, 90%+ for critical business logic
- **Critical paths**: User authentication, financial data accuracy, model fallback logic
- **Edge cases**: Error handling, boundary conditions, null/empty inputs
- **NOT covered**: Trivial getters/setters, framework boilerplate, auto-generated code

## Test Organization

### Directory Structure
```
tests/
├── conftest.py               # Shared pytest fixtures and configuration
├── test_*.py                 # Unit tests for core modules
├── api/                      # API integration tests
│   └── test_api_routes.py
├── integration/              # Cross-service integration tests
│   ├── test_db_operations.py
│   └── test_cache_layer.py
├── e2e/                      # End-to-end tests (future)
│   └── test_user_workflows.py
├── performance/              # Load and performance tests
│   └── test_load.py
└── security/                 # Security and vulnerability tests
    └── test_auth.py

frontend/src/
├── components/
│   └── ChatMessage.test.tsx  # Component unit tests
├── services/
│   └── api.test.ts           # Service layer tests
└── utils/
    └── validation.test.ts    # Utility function tests
```

### Naming Conventions
- **Backend (Python)**: `test_<module_name>.py` (e.g., `test_agent.py`, `test_data_manager.py`)
- **Frontend (TypeScript)**: `<ComponentName>.test.tsx` or `<module>.test.ts`
- **Test functions**: `test_<behavior_description>` (e.g., `test_agent_returns_fallback_when_primary_fails`)
- **Test classes**: `Test<FeatureName>` (e.g., `TestModelFactory`, `TestChatMessage`)

## Backend Testing (Python + pytest)

### pytest Configuration
- **Framework**: pytest 7.0+ with plugins (pytest-cov, pytest-mock)
- **Configuration**: `pytest.ini` or `pyproject.toml` for settings
- **Fixtures**: Centralized in `tests/conftest.py` for reusability

### Fixture Patterns
```python
# tests/conftest.py
import pytest
from core.agent import StockAgent
from utils.config_loader import ConfigLoader

@pytest.fixture
def mock_config():
    """Minimal configuration for testing."""
    return {
        'model_provider': 'openai',
        'openai': {'api_key': 'test-key-fake', 'model': 'gpt-4'},
        'mongodb': {'uri': 'mongodb://localhost:27017/test_db'},
        'redis': {'host': 'localhost', 'port': 6379, 'db': 1}  # Separate test DB
    }

@pytest.fixture
def mock_agent(mock_config, mocker):
    """Agent with mocked external dependencies."""
    mocker.patch('core.model_factory.ModelFactory.create_client')
    mocker.patch('core.data_manager.DataManager.fetch_stock_data', return_value={'price': 150.0})
    return StockAgent(mock_config, data_manager=None)

@pytest.fixture
def flask_test_client(mock_config):
    """Flask app test client with mocked dependencies."""
    from web.app_factory import create_app
    app = create_app(mock_config)
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
```

### Unit Test Patterns

#### Testing Pure Functions
```python
def test_calculate_moving_average_returns_correct_values():
    """Test moving average calculation with known input."""
    from analysis.technical import calculate_moving_average
    
    prices = [100, 102, 104, 106, 108]
    result = calculate_moving_average(prices, window=3)
    
    assert len(result) == 3
    assert result[0] == pytest.approx(102.0)
    assert result[-1] == pytest.approx(106.0)

def test_calculate_moving_average_raises_on_invalid_window():
    """Test error handling for invalid window size."""
    from analysis.technical import calculate_moving_average
    
    with pytest.raises(ValueError, match="Window size must be positive"):
        calculate_moving_average([100, 102], window=0)
```

#### Testing Classes with Dependencies
```python
def test_agent_processes_query_with_primary_model(mock_agent, mocker):
    """Test agent uses primary model for query processing."""
    mock_client = mocker.MagicMock()
    mock_client.generate.return_value = "AAPL is trading at $150"
    mocker.patch.object(mock_agent, '_get_model_client', return_value=mock_client)
    
    result = mock_agent._process_query("Price of AAPL")
    
    assert "150" in result
    mock_client.generate.assert_called_once()

def test_agent_falls_back_when_primary_fails(mock_agent, mocker):
    """Test agent falls back to secondary model on primary failure."""
    primary_client = mocker.MagicMock()
    primary_client.generate.side_effect = Exception("API error")
    
    fallback_client = mocker.MagicMock()
    fallback_client.generate.return_value = "Fallback response"
    
    mocker.patch.object(mock_agent, '_get_model_client', side_effect=[primary_client, fallback_client])
    
    result = mock_agent._process_query("Price of AAPL")
    
    assert "Fallback response" in result
    assert primary_client.generate.call_count == 1
    assert fallback_client.generate.call_count == 1
```

#### Testing Streaming Functions
```python
def test_agent_streaming_yields_chunks(mock_agent, mocker):
    """Test agent streaming returns incremental chunks."""
    mock_client = mocker.MagicMock()
    mock_client.generate_stream.return_value = iter(["chunk1", "chunk2", "chunk3"])
    mocker.patch.object(mock_agent, '_get_model_client', return_value=mock_client)
    
    chunks = list(mock_agent.process_query_streaming("Test query"))
    
    assert len(chunks) == 3
    assert chunks[0] == "chunk1"
    assert chunks[-1] == "chunk3"
```

### Integration Test Patterns

#### Testing Flask API Routes
```python
def test_health_endpoint_returns_healthy_status(flask_test_client):
    """Test /api/health returns 200 with healthy status."""
    response = flask_test_client.get('/api/health')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'

def test_chat_endpoint_processes_message(flask_test_client, mocker):
    """Test /api/chat endpoint with valid payload."""
    mocker.patch('core.agent.StockAgent._process_query', return_value="Response text")
    
    response = flask_test_client.post('/api/chat', json={
        'message': 'Price of AAPL',
        'provider': 'openai'
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'response' in data
    assert data['model'] == 'gpt-4'

def test_chat_endpoint_returns_400_on_missing_message(flask_test_client):
    """Test /api/chat validation for required fields."""
    response = flask_test_client.post('/api/chat', json={})
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
```

#### Testing Database Repositories
```python
@pytest.fixture
def test_db():
    """Isolated test database with cleanup."""
    from pymongo import MongoClient
    client = MongoClient('mongodb://localhost:27017/')
    db = client['test_stock_assistant']
    yield db
    client.drop_database('test_stock_assistant')  # Cleanup after test
    client.close()

def test_repository_inserts_and_retrieves_stock_data(test_db):
    """Test repository can store and fetch stock data."""
    from data.repositories.market_data_repository import MarketDataRepository
    
    repo = MarketDataRepository(test_db)
    
    # Insert test data
    repo.insert_price({'symbol': 'AAPL', 'price': 150.0, 'timestamp': '2024-01-01T00:00:00Z'})
    
    # Retrieve and verify
    result = repo.get_latest_price('AAPL')
    assert result['symbol'] == 'AAPL'
    assert result['price'] == 150.0
```

### Mocking Strategies

#### Mocking External APIs
```python
def test_data_manager_fetches_yahoo_finance_data(mocker):
    """Test DataManager handles Yahoo Finance API responses."""
    mock_response = {
        'chart': {'result': [{'meta': {'regularMarketPrice': 150.0}}]}
    }
    mocker.patch('requests.get', return_value=mocker.Mock(json=lambda: mock_response, status_code=200))
    
    from core.data_manager import DataManager
    manager = DataManager(config={})
    
    price = manager.fetch_current_price('AAPL')
    assert price == 150.0
```

#### Mocking MongoDB
```python
def test_repository_handles_mongodb_errors_gracefully(mocker):
    """Test repository error handling for database failures."""
    from pymongo.errors import ConnectionFailure
    from data.repositories.market_data_repository import MarketDataRepository
    
    mock_db = mocker.MagicMock()
    mock_db.market_data.find_one.side_effect = ConnectionFailure("Network error")
    
    repo = MarketDataRepository(mock_db)
    
    with pytest.raises(ConnectionFailure):
        repo.get_latest_price('AAPL')
```

#### Mocking Redis
```python
def test_cache_layer_uses_redis_for_price_data(mocker):
    """Test caching layer with Redis mock."""
    mock_redis = mocker.MagicMock()
    mock_redis.get.return_value = None  # Cache miss
    mock_redis.setex.return_value = True
    
    mocker.patch('redis.Redis', return_value=mock_redis)
    
    from data.services.cache_service import CacheService
    cache = CacheService(config={'redis': {'host': 'localhost'}})
    
    # First call - cache miss, should fetch and store
    price = cache.get_or_fetch_price('AAPL', fetcher=lambda: 150.0)
    
    assert price == 150.0
    mock_redis.get.assert_called_once_with('price:AAPL')
    mock_redis.setex.assert_called_once()
```

### Running Backend Tests
```powershell
# Run all tests
pytest -v

# Run specific test file
pytest tests/test_agent.py -v

# Run tests matching pattern
pytest -k "test_agent" -v

# Run with coverage report
pytest --cov=src --cov-report=html --cov-report=term

# Run tests in parallel (requires pytest-xdist)
pytest -n auto

# Run only failed tests from last run
pytest --lf

# Stop on first failure (fast feedback)
pytest -x
```

## Frontend Testing (Jest + React Testing Library)

### Jest Configuration
- **Framework**: Jest 29+ (included with Create React App)
- **Testing Library**: React Testing Library for component tests
- **Configuration**: `package.json` jest field or `jest.config.js`

### Component Testing Patterns

#### Testing Presentational Components
```typescript
// ChatMessage.test.tsx
import { render, screen } from '@testing-library/react';
import { ChatMessage } from './ChatMessage';

describe('ChatMessage', () => {
  it('renders user message with correct styling', () => {
    render(<ChatMessage message="Hello" isUser={true} timestamp="10:30 AM" />);
    
    const messageElement = screen.getByText('Hello');
    expect(messageElement).toBeInTheDocument();
    expect(messageElement).toHaveClass('user-message');
  });

  it('renders assistant message with different styling', () => {
    render(<ChatMessage message="Hi there" isUser={false} timestamp="10:31 AM" />);
    
    const messageElement = screen.getByText('Hi there');
    expect(messageElement).toHaveClass('assistant-message');
  });

  it('displays timestamp', () => {
    render(<ChatMessage message="Test" isUser={true} timestamp="10:30 AM" />);
    
    expect(screen.getByText('10:30 AM')).toBeInTheDocument();
  });
});
```

#### Testing Components with State
```typescript
// ChatInput.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ChatInput } from './ChatInput';

describe('ChatInput', () => {
  it('calls onSend with input value when submit button clicked', async () => {
    const mockOnSend = jest.fn();
    render(<ChatInput onSend={mockOnSend} />);
    
    const input = screen.getByPlaceholderText('Type your message...');
    const button = screen.getByRole('button', { name: /send/i });
    
    await userEvent.type(input, 'Price of AAPL');
    fireEvent.click(button);
    
    expect(mockOnSend).toHaveBeenCalledWith('Price of AAPL');
  });

  it('clears input after sending message', async () => {
    render(<ChatInput onSend={jest.fn()} />);
    
    const input = screen.getByPlaceholderText('Type your message...') as HTMLInputElement;
    await userEvent.type(input, 'Test message');
    fireEvent.click(screen.getByRole('button', { name: /send/i }));
    
    expect(input.value).toBe('');
  });

  it('disables send button when input is empty', () => {
    render(<ChatInput onSend={jest.fn()} />);
    
    const button = screen.getByRole('button', { name: /send/i });
    expect(button).toBeDisabled();
  });
});
```

#### Testing Custom Hooks
```typescript
// useChatStream.test.ts
import { renderHook, act } from '@testing-library/react';
import { useChatStream } from './useChatStream';
import { io } from 'socket.io-client';

jest.mock('socket.io-client');

describe('useChatStream', () => {
  it('connects to WebSocket on mount', () => {
    const mockSocket = { on: jest.fn(), emit: jest.fn(), off: jest.fn() };
    (io as jest.Mock).mockReturnValue(mockSocket);
    
    renderHook(() => useChatStream());
    
    expect(io).toHaveBeenCalledWith('http://localhost:5000');
    expect(mockSocket.on).toHaveBeenCalledWith('connect', expect.any(Function));
  });

  it('sends message via WebSocket', () => {
    const mockSocket = { on: jest.fn(), emit: jest.fn(), off: jest.fn() };
    (io as jest.Mock).mockReturnValue(mockSocket);
    
    const { result } = renderHook(() => useChatStream());
    
    act(() => {
      result.current.sendMessage('Test message');
    });
    
    expect(mockSocket.emit).toHaveBeenCalledWith('chat_message', { message: 'Test message' });
  });

  it('cleans up listeners on unmount', () => {
    const mockSocket = { on: jest.fn(), emit: jest.fn(), off: jest.fn(), disconnect: jest.fn() };
    (io as jest.Mock).mockReturnValue(mockSocket);
    
    const { unmount } = renderHook(() => useChatStream());
    
    unmount();
    
    expect(mockSocket.off).toHaveBeenCalled();
    expect(mockSocket.disconnect).toHaveBeenCalled();
  });
});
```

### Service Layer Testing
```typescript
// api.test.ts
import { fetchStockPrice, fetchChatResponse } from './api';

global.fetch = jest.fn();

describe('API Service', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('fetches stock price successfully', async () => {
    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ symbol: 'AAPL', price: 150.0 })
    });
    
    const result = await fetchStockPrice('AAPL');
    
    expect(fetch).toHaveBeenCalledWith('http://localhost:5000/api/stock/AAPL');
    expect(result.price).toBe(150.0);
  });

  it('throws error on failed API call', async () => {
    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 500
    });
    
    await expect(fetchStockPrice('AAPL')).rejects.toThrow('Failed to fetch stock price');
  });
});
```

### Running Frontend Tests
```powershell
cd frontend

# Run all tests in watch mode
npm test

# Run tests once (CI mode)
npm run test:ci

# Run with coverage
npm test -- --coverage

# Run specific test file
npm test -- ChatMessage.test.tsx

# Update snapshots
npm test -- -u
```

## End-to-End Testing (Future)

### E2E Testing Strategy
- **Tool**: Playwright or Cypress for browser automation
- **Scope**: Critical user workflows (chat interaction, data visualization)
- **Frequency**: Run on pre-production environment before release
- **Data**: Use test fixtures or dedicated test database

### Example E2E Test Pattern (Playwright)
```typescript
// e2e/chat-workflow.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Chat Workflow', () => {
  test('user can send message and receive response', async ({ page }) => {
    await page.goto('http://localhost:3000');
    
    // Wait for app to load
    await expect(page.locator('h1')).toContainText('Stock Assistant');
    
    // Send message
    await page.fill('input[placeholder="Type your message..."]', 'Price of AAPL');
    await page.click('button:has-text("Send")');
    
    // Wait for response
    await expect(page.locator('.assistant-message').last()).toContainText('AAPL', { timeout: 10000 });
    
    // Verify message appears in chat history
    const messages = await page.locator('.chat-message').count();
    expect(messages).toBeGreaterThanOrEqual(2); // User + Assistant
  });
});
```

## Performance Testing

### Load Testing Strategy
- **Tool**: Locust (Python), k6 (JavaScript), or Apache JMeter
- **Metrics**: Requests/sec, latency (p50, p95, p99), error rate
- **Scenarios**: Gradual ramp-up, spike testing, sustained load
- **Targets**: 
  - API response time: p95 < 500ms
  - Streaming latency: First chunk < 1s
  - Concurrent users: 100+ without degradation

### Example Load Test (Locust)
```python
# tests/performance/test_load.py
from locust import HttpUser, task, between

class StockAssistantUser(HttpUser):
    wait_time = between(1, 3)  # Simulate user think time
    
    @task(3)  # Weight: 3x more common than other tasks
    def chat_query(self):
        """Test chat endpoint under load."""
        self.client.post("/api/chat", json={
            "message": "Price of AAPL",
            "provider": "openai"
        })
    
    @task(1)
    def health_check(self):
        """Test health endpoint."""
        self.client.get("/api/health")
    
    @task(1)
    def get_models(self):
        """Test models endpoint."""
        self.client.get("/api/models")

# Run: locust -f tests/performance/test_load.py --host=http://localhost:5000
```

### Performance Benchmarking
```python
# Example: Benchmark model inference time
import time
import statistics

def benchmark_agent_response(agent, queries, iterations=10):
    """Benchmark agent response time."""
    results = []
    
    for query in queries:
        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            agent._process_query(query)
            elapsed = time.perf_counter() - start
            times.append(elapsed)
        
        results.append({
            'query': query,
            'mean': statistics.mean(times),
            'median': statistics.median(times),
            'stdev': statistics.stdev(times),
            'min': min(times),
            'max': max(times)
        })
    
    return results

# Run benchmark and assert performance requirements
def test_agent_response_time_under_threshold():
    """Test agent responds within acceptable time."""
    from core.agent import StockAgent
    agent = StockAgent(config, data_manager)
    
    queries = ["Price of AAPL", "Latest news on TSLA", "Market overview"]
    results = benchmark_agent_response(agent, queries, iterations=5)
    
    for result in results:
        assert result['mean'] < 2.0, f"Query '{result['query']}' took {result['mean']:.2f}s (>2s threshold)"
```

## Security Testing

### Security Testing Strategy
- **Static Analysis**: Bandit (Python), ESLint security plugins (JS/TS)
- **Dependency Scanning**: Snyk, Dependabot, npm audit, pip-audit
- **Container Scanning**: Trivy, Clair for Docker images
- **Secrets Detection**: GitGuardian, TruffleHog
- **Penetration Testing**: OWASP ZAP, Burp Suite (manual or automated)

### Static Security Analysis
```powershell
# Python security scan (Bandit)
pip install bandit
bandit -r src/ -ll  # Only high/medium severity

# JavaScript/TypeScript security scan
cd frontend
npm audit --audit-level=high
npm audit fix

# Dependency vulnerability check
pip install pip-audit
pip-audit --desc --fix

# Container image scan
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image dp-stock/api:latest
```

### Security Test Patterns

#### Testing Authentication and Authorization
```python
def test_api_rejects_requests_without_auth_token():
    """Test API enforces authentication (when implemented)."""
    response = client.get('/api/private-endpoint')
    assert response.status_code == 401

def test_api_validates_jwt_token():
    """Test API validates JWT signature."""
    invalid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature"
    response = client.get('/api/private-endpoint', headers={'Authorization': f'Bearer {invalid_token}'})
    assert response.status_code == 401
```

#### Testing Input Validation
```python
def test_api_rejects_sql_injection_attempts():
    """Test API sanitizes inputs to prevent SQL injection."""
    response = client.post('/api/chat', json={
        'message': "'; DROP TABLE users; --"
    })
    # Should not crash; should treat as normal text
    assert response.status_code in [200, 400]  # Valid response or validation error

def test_api_rejects_xss_attempts():
    """Test API escapes HTML to prevent XSS."""
    response = client.post('/api/chat', json={
        'message': "<script>alert('XSS')</script>"
    })
    data = response.get_json()
    # Response should not contain unescaped script tags
    assert '<script>' not in str(data)
```

#### Testing Rate Limiting (Future)
```python
def test_api_enforces_rate_limit():
    """Test API rate limiting prevents abuse."""
    for _ in range(100):  # Exceed rate limit
        response = client.post('/api/chat', json={'message': 'test'})
    
    assert response.status_code == 429  # Too Many Requests
    data = response.get_json()
    assert 'rate limit' in data['error'].lower()
```

### OWASP Top 10 Test Coverage
- **A01 Broken Access Control**: Test unauthorized access to endpoints
- **A02 Cryptographic Failures**: Verify HTTPS enforcement, secure password storage
- **A03 Injection**: Test SQL injection, NoSQL injection, command injection
- **A04 Insecure Design**: Review architecture for security flaws (manual)
- **A05 Security Misconfiguration**: Audit default configs, exposed debug endpoints
- **A06 Vulnerable Components**: Automated dependency scanning (Snyk, Dependabot)
- **A07 Authentication Failures**: Test weak passwords, session management
- **A08 Data Integrity Failures**: Verify input validation, output encoding
- **A09 Logging Failures**: Ensure sensitive data not logged, audit logs tamper-proof
- **A10 SSRF**: Test server-side request forgery with malicious URLs

## Test Data Management

### Fixtures and Seed Data
- **Location**: `tests/fixtures/` for JSON/YAML test data
- **Database seeds**: SQL/MongoDB scripts for integration tests
- **Factories**: Use factories (factory_boy for Python) to generate test objects
  ```python
  # Example: Factory for test data
  import factory
  from data.models import StockPrice
  
  class StockPriceFactory(factory.Factory):
      class Meta:
          model = StockPrice
      
      symbol = factory.Sequence(lambda n: f"SYM{n}")
      price = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True)
      timestamp = factory.Faker('date_time_this_year')
  ```

### Test Isolation Strategies
- **Database**: Use separate test database; reset between tests or use transactions
- **Redis**: Use separate Redis DB (e.g., DB 1 for tests, DB 0 for dev)
- **Filesystem**: Use `tmpdir` or `tmp_path` fixtures (pytest) for temporary files
- **Time**: Mock `datetime.now()` for consistent timestamps
  ```python
  def test_report_generation_uses_current_date(mocker):
      fixed_time = datetime(2024, 1, 1, 12, 0, 0)
      mocker.patch('datetime.datetime').now.return_value = fixed_time
      
      report = generate_report('AAPL')
      assert report['generated_at'] == fixed_time.isoformat()
  ```

## CI/CD Testing Integration

### GitHub Actions Test Workflow
```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests with coverage
        run: pytest --cov=src --cov-report=xml --cov-report=term
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
  
  frontend-tests:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: frontend
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: 'frontend/package-lock.json'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run tests
        run: npm run test:ci
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./frontend/coverage/lcov.info
```

### Test Quality Gates
- **Coverage threshold**: Fail build if coverage drops below 80%
- **Test duration**: Warn if test suite takes >5 minutes
- **Flaky tests**: Quarantine or fix tests that fail intermittently
- **Zero tolerance**: No skipped tests in main branch without justification

## Debugging Failed Tests

### Common Debugging Techniques
- **Verbose output**: `pytest -vv` or `npm test -- --verbose`
- **Print debugging**: Use `print()` or `console.log()`, but remove before commit
- **Debugger**: Use `pytest --pdb` to drop into debugger on failure
- **Isolation**: Run single test with `pytest tests/test_agent.py::test_specific_function`
- **Capture output**: `pytest -s` to see stdout/stderr during test execution

### Troubleshooting Patterns
- **Flaky network tests**: Ensure all external calls are mocked
- **Database state pollution**: Check test isolation; use transaction rollbacks
- **Timing issues**: Avoid `time.sleep()`; use polling with timeout or mock time
- **Fixture conflicts**: Check fixture scope (function, class, module, session)
- **Import errors**: Verify PYTHONPATH includes `src/` directory

## Testing Best Practices Summary

### Do's
- ✅ Write tests before or immediately after implementation (TDD/BDD)
- ✅ Test one behavior per test function
- ✅ Use descriptive test names that explain intent
- ✅ Mock external dependencies (APIs, databases, network)
- ✅ Keep tests fast (<1s per unit test)
- ✅ Use fixtures and factories to reduce boilerplate
- ✅ Run tests locally before pushing
- ✅ Maintain test documentation and update as code evolves

### Don'ts
- ❌ Don't test implementation details (private methods, internal state)
- ❌ Don't rely on test execution order
- ❌ Don't use real API keys or production data
- ❌ Don't leave commented-out or skipped tests without justification
- ❌ Don't ignore flaky tests; fix or remove them
- ❌ Don't hardcode paths or environment-specific values
- ❌ Don't use `sleep()` to wait for async operations; use proper async patterns
- ❌ Don't aim for 100% coverage; focus on meaningful tests

## References
- pytest: https://docs.pytest.org/
- Jest: https://jestjs.io/docs/getting-started
- React Testing Library: https://testing-library.com/docs/react-testing-library/intro/
- Playwright: https://playwright.dev/
- Locust: https://docs.locust.io/
- OWASP Testing Guide: https://owasp.org/www-project-web-security-testing-guide/
