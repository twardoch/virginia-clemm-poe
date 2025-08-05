# Chapter 8: Configuration and Advanced Usage

## Overview

Virginia Clemm Poe provides extensive configuration options for customizing behavior, performance tuning, and integration with different environments. This chapter covers advanced configuration, custom integrations, and power-user features.

## Configuration System

### Configuration Hierarchy

Configuration is loaded in order of precedence:

1. **Command-line arguments** (highest priority)
2. **Environment variables**
3. **Configuration files**
4. **Default values** (lowest priority)

### Configuration File Locations

**Linux/macOS:**
```bash
# Primary config file
~/.config/virginia-clemm-poe/config.json

# Alternative locations
~/.virginia-clemm-poe/config.json
./virginia-clemm-poe.json
```

**Windows:**
```cmd
# Primary config file
%APPDATA%\virginia-clemm-poe\config.json

# Alternative locations
%USERPROFILE%\.virginia-clemm-poe\config.json
.\virginia-clemm-poe.json
```

### Configuration Schema

```json
{
  "api": {
    "key": "your_poe_api_key",
    "base_url": "https://api.poe.com/v2",
    "timeout": 30,
    "retry_count": 3,
    "rate_limit": {
      "requests_per_minute": 60,
      "burst_limit": 10
    }
  },
  "browser": {
    "headless": true,
    "debug_port_start": 9222,
    "max_browsers": 3,
    "timeout": 30000,
    "user_agent": "virginia-clemm-poe/1.0",
    "viewport": {
      "width": 1920,
      "height": 1080
    },
    "chrome_args": [
      "--no-sandbox",
      "--disable-dev-shm-usage"
    ]
  },
  "scraping": {
    "concurrent_limit": 5,
    "pause_between_requests": 1.0,
    "retry_delay": 2.0,
    "max_retries": 3,
    "selectors": {
      "pricing_table": [
        "table[data-testid='pricing']",
        ".pricing-table"
      ],
      "bot_creator": [
        "[data-testid='bot-creator']",
        ".bot-creator"
      ]
    }
  },
  "cache": {
    "enabled": true,
    "api_cache": {
      "ttl": 600,
      "max_size": 1000
    },
    "scraping_cache": {
      "ttl": 3600,
      "max_size": 5000
    },
    "global_cache": {
      "ttl": 1800,
      "max_size": 2000
    }
  },
  "storage": {
    "data_file": "~/.local/share/virginia-clemm-poe/poe_models.json",
    "backup_count": 5,
    "auto_backup": true,
    "compression": false
  },
  "logging": {
    "level": "INFO",
    "file": "~/.local/share/virginia-clemm-poe/logs/app.log",
    "max_size": "10MB",
    "backup_count": 5,
    "format": "{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {name}:{function}:{line} | {message}",
    "structured": true
  },
  "performance": {
    "memory_limit": "512MB",
    "gc_threshold": 0.8,
    "enable_profiling": false,
    "metrics_enabled": true
  }
}
```

## Environment Variables

### Core Configuration

```bash
# API Configuration
export POE_API_KEY="your_poe_api_key_here"
export VCP_API_BASE_URL="https://api.poe.com/v2"
export VCP_API_TIMEOUT="30"

# Browser Configuration
export VCP_HEADLESS="true"
export VCP_DEBUG_PORT="9222"
export VCP_BROWSER_TIMEOUT="30000"
export VCP_USER_AGENT="virginia-clemm-poe/1.0"

# Scraping Configuration
export VCP_CONCURRENT_LIMIT="5"
export VCP_PAUSE_SECONDS="1.0"
export VCP_MAX_RETRIES="3"

# Cache Configuration
export VCP_CACHE_ENABLED="true"
export VCP_CACHE_TTL="3600"
export VCP_CACHE_MAX_SIZE="5000"

# Logging Configuration
export VCP_LOG_LEVEL="INFO"
export VCP_LOG_FILE="~/.local/share/virginia-clemm-poe/logs/app.log"
export VCP_STRUCTURED_LOGGING="true"

# Storage Configuration
export VCP_DATA_FILE="~/.local/share/virginia-clemm-poe/poe_models.json"
export VCP_BACKUP_COUNT="5"
export VCP_AUTO_BACKUP="true"

# Performance Configuration
export VCP_MEMORY_LIMIT="512MB"
export VCP_GC_THRESHOLD="0.8"
export VCP_ENABLE_PROFILING="false"
```

### Advanced Environment Variables

```bash
# Network Configuration
export HTTP_PROXY="http://proxy.example.com:8080"
export HTTPS_PROXY="http://proxy.example.com:8080"
export NO_PROXY="localhost,127.0.0.1"

# Browser Engine Selection
export CHROME_PATH="/path/to/custom/chrome"
export VCP_USER_DATA_DIR="/path/to/user/data"
export VCP_DISABLE_EXTENSIONS="true"

# Development Configuration
export VCP_DEBUG="true"
export VCP_PROFILE_MEMORY="true"
export VCP_SAVE_SCREENSHOTS="true"
export VCP_SAVE_PAGE_CONTENT="true"

# CI/CD Configuration
export VCP_CI_MODE="true"
export VCP_NON_INTERACTIVE="true"
export VCP_FAIL_FAST="true"
```

## Advanced Configuration Examples

### High-Performance Configuration

For servers with ample resources:

```json
{
  "browser": {
    "max_browsers": 10,
    "debug_port_start": 9222,
    "timeout": 60000
  },
  "scraping": {
    "concurrent_limit": 20,
    "pause_between_requests": 0.5,
    "max_retries": 5
  },
  "cache": {
    "api_cache": {
      "ttl": 300,
      "max_size": 5000
    },
    "scraping_cache": {
      "ttl": 1800,
      "max_size": 20000
    }
  },
  "performance": {
    "memory_limit": "2GB",
    "gc_threshold": 0.7,
    "enable_profiling": true
  }
}
```

### Low-Resource Configuration

For resource-constrained environments:

```json
{
  "browser": {
    "max_browsers": 1,
    "timeout": 15000,
    "chrome_args": [
      "--no-sandbox",
      "--disable-dev-shm-usage",
      "--memory-pressure-off",
      "--max_old_space_size=256"
    ]
  },
  "scraping": {
    "concurrent_limit": 1,
    "pause_between_requests": 2.0,
    "max_retries": 2
  },
  "cache": {
    "api_cache": {
      "max_size": 100
    },
    "scraping_cache": {
      "max_size": 500
    }
  },
  "performance": {
    "memory_limit": "128MB",
    "gc_threshold": 0.6
  }
}
```

### Development Configuration

For development and debugging:

```json
{
  "browser": {
    "headless": false,
    "debug_port_start": 9222,
    "chrome_args": [
      "--disable-blink-features=AutomationControlled",
      "--disable-extensions-except=/path/to/dev/extension",
      "--load-extension=/path/to/dev/extension"
    ]
  },
  "scraping": {
    "pause_between_requests": 3.0,
    "save_screenshots": true,
    "save_page_content": true
  },
  "logging": {
    "level": "DEBUG",
    "structured": true,
    "enable_console": true
  },
  "performance": {
    "enable_profiling": true,
    "metrics_enabled": true
  }
}
```

## Advanced API Usage

### Custom Configuration Loading

```python
from virginia_clemm_poe.config import load_config, Config

# Load configuration with custom file
config = load_config("/path/to/custom/config.json")

# Override specific settings
config.browser.headless = False
config.scraping.concurrent_limit = 1

# Use configuration in API calls
from virginia_clemm_poe import api
api.configure(config)
```

### Configuration Validation

```python
from virginia_clemm_poe.config import validate_config, ConfigValidationError

try:
    config = load_config()
    validate_config(config)
    print("Configuration is valid")
except ConfigValidationError as e:
    print(f"Configuration error: {e}")
    # Handle invalid configuration
```

### Dynamic Configuration Updates

```python
from virginia_clemm_poe.config import get_runtime_config, update_runtime_config

# Get current runtime configuration
runtime_config = get_runtime_config()

# Update configuration at runtime
update_runtime_config({
    "scraping.concurrent_limit": 3,
    "cache.api_cache.ttl": 1200
})

# Changes take effect immediately for new operations
```

## Performance Tuning

### Memory Optimization

```python
from virginia_clemm_poe.utils.memory import configure_memory_management

# Configure memory management
configure_memory_management(
    limit="512MB",
    gc_threshold=0.8,
    enable_monitoring=True
)

# Monitor memory usage during operations
from virginia_clemm_poe.utils.memory import get_memory_stats

stats = get_memory_stats()
print(f"Memory usage: {stats['used_mb']:.1f}MB / {stats['limit_mb']:.1f}MB")
print(f"GC collections: {stats['gc_collections']}")
```

### Cache Optimization

```python
from virginia_clemm_poe.utils.cache import configure_caches, get_cache_stats

# Configure cache settings
configure_caches({
    "api_cache": {"ttl": 300, "max_size": 1000},
    "scraping_cache": {"ttl": 1800, "max_size": 5000},
    "global_cache": {"ttl": 900, "max_size": 2000}
})

# Monitor cache performance
stats = get_cache_stats()
for cache_name, cache_stats in stats.items():
    hit_rate = cache_stats['hit_rate_percent']
    print(f"{cache_name}: {hit_rate:.1f}% hit rate")
```

### Concurrent Processing

```python
from virginia_clemm_poe.updater import ModelUpdater
import asyncio

async def optimized_update():
    updater = ModelUpdater(
        api_key="your_key",
        concurrent_limit=10,  # Increase concurrency
        batch_size=20,        # Larger batches
        retry_delay=1.0       # Faster retries
    )
    
    # Update with optimized settings
    await updater.update_all(
        force=False,           # Only update what's needed
        update_pricing=True,   # Focus on pricing data
        update_info=False      # Skip bot info for speed
    )

# Run optimized update
asyncio.run(optimized_update())
```

## Integration Patterns

### Web Framework Integration

#### FastAPI Integration

```python
from fastapi import FastAPI, BackgroundTasks
from virginia_clemm_poe import api
from virginia_clemm_poe.config import load_config

app = FastAPI()

# Load configuration on startup
@app.on_event("startup")
async def startup_event():
    config = load_config()
    api.configure(config)

@app.get("/models/search/{query}")
async def search_models(query: str):
    models = api.search_models(query)
    return {"query": query, "models": models}

@app.post("/admin/update")
async def trigger_update(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_update_task)
    return {"message": "Update started"}

async def run_update_task():
    from virginia_clemm_poe.updater import ModelUpdater
    updater = ModelUpdater(api_key=os.environ["POE_API_KEY"])
    await updater.update_all()
```

#### Django Integration

```python
# settings.py
VIRGINIA_CLEMM_POE = {
    'API_KEY': os.environ.get('POE_API_KEY'),
    'CACHE_ENABLED': True,
    'CONCURRENT_LIMIT': 5,
    'DATA_FILE': os.path.join(BASE_DIR, 'data', 'poe_models.json')
}

# management/commands/update_models.py
from django.core.management.base import BaseCommand
from virginia_clemm_poe.updater import ModelUpdater
import asyncio

class Command(BaseCommand):
    help = 'Update Poe model data'
    
    def handle(self, *args, **options):
        from django.conf import settings
        
        updater = ModelUpdater(
            api_key=settings.VIRGINIA_CLEMM_POE['API_KEY']
        )
        asyncio.run(updater.update_all())
        
        self.stdout.write(
            self.style.SUCCESS('Successfully updated model data')
        )
```

### Database Integration

#### SQLAlchemy Integration

```python
from sqlalchemy import create_engine, Column, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json

Base = declarative_base()

class PoeModelRecord(Base):
    __tablename__ = 'poe_models'
    
    id = Column(String, primary_key=True)
    model_name = Column(String)
    owned_by = Column(String)
    created = Column(DateTime)
    pricing_data = Column(Text)  # JSON
    bot_info_data = Column(Text)  # JSON
    last_updated = Column(DateTime)

def sync_to_database():
    """Sync Virginia Clemm Poe data to database."""
    from virginia_clemm_poe import api
    
    engine = create_engine('sqlite:///poe_models.db')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    models = api.get_all_models()
    
    for model in models:
        record = session.query(PoeModelRecord).filter_by(id=model.id).first()
        if not record:
            record = PoeModelRecord(id=model.id)
            session.add(record)
        
        record.model_name = model.model_name
        record.owned_by = model.owned_by
        record.created = datetime.fromtimestamp(model.created)
        record.pricing_data = json.dumps(model.pricing.model_dump() if model.pricing else None)
        record.bot_info_data = json.dumps(model.bot_info.model_dump() if model.bot_info else None)
        record.last_updated = datetime.utcnow()
    
    session.commit()
    session.close()
```

### Monitoring Integration

#### Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, Gauge, start_http_server
from virginia_clemm_poe.utils.metrics import register_metrics

# Register custom metrics
SCRAPING_REQUESTS = Counter('vcp_scraping_requests_total', 'Total scraping requests', ['model_id', 'status'])
SCRAPING_DURATION = Histogram('vcp_scraping_duration_seconds', 'Scraping request duration', ['model_id'])
CACHE_HIT_RATE = Gauge('vcp_cache_hit_rate', 'Cache hit rate', ['cache_name'])

def monitor_scraping():
    """Monitor scraping operations with Prometheus metrics."""
    
    @SCRAPING_DURATION.time()
    def scrape_with_metrics(model_id):
        try:
            result = scrape_model(model_id)
            SCRAPING_REQUESTS.labels(model_id=model_id, status='success').inc()
            return result
        except Exception as e:
            SCRAPING_REQUESTS.labels(model_id=model_id, status='error').inc()
            raise
    
    # Start metrics server
    start_http_server(8000)
    
    return scrape_with_metrics
```

#### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "Virginia Clemm Poe Monitoring",
    "panels": [
      {
        "title": "Scraping Success Rate",
        "type": "stat",
        "targets": [
          {
            "expr": "rate(vcp_scraping_requests_total{status=\"success\"}[5m]) / rate(vcp_scraping_requests_total[5m]) * 100"
          }
        ]
      },
      {
        "title": "Cache Hit Rates",
        "type": "graph",
        "targets": [
          {
            "expr": "vcp_cache_hit_rate",
            "legendFormat": "{{cache_name}}"
          }
        ]
      },
      {
        "title": "Scraping Duration",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(vcp_scraping_duration_seconds_bucket[5m]))"
          }
        ]
      }
    ]
  }
}
```

## Security Configuration

### API Key Management

```python
# Using environment variables (recommended)
import os
api_key = os.environ.get('POE_API_KEY')

# Using keyring for secure storage
import keyring
keyring.set_password('virginia-clemm-poe', 'api_key', 'your_key')
api_key = keyring.get_password('virginia-clemm-poe', 'api_key')

# Using AWS Secrets Manager
import boto3
client = boto3.client('secretsmanager')
response = client.get_secret_value(SecretId='virginia-clemm-poe/api-key')
api_key = response['SecretString']
```

### Network Security

```python
# Configure proxy settings
import httpx

proxy_config = {
    'http://': 'http://proxy.example.com:8080',
    'https://': 'http://proxy.example.com:8080'
}

# SSL/TLS configuration
ssl_config = {
    'verify': True,  # Verify SSL certificates
    'cert': '/path/to/client/cert.pem',  # Client certificate
    'trust_env': True  # Trust environment proxy settings
}

# Configure HTTP client with security settings
client = httpx.AsyncClient(
    proxies=proxy_config,
    **ssl_config,
    timeout=30.0
)
```

### Data Security

```python
# Encrypt sensitive data at rest
from cryptography.fernet import Fernet

def encrypt_data_file(data_file_path: str, key: bytes):
    """Encrypt model data file."""
    fernet = Fernet(key)
    
    with open(data_file_path, 'rb') as f:
        data = f.read()
    
    encrypted_data = fernet.encrypt(data)
    
    with open(f"{data_file_path}.encrypted", 'wb') as f:
        f.write(encrypted_data)

def decrypt_data_file(encrypted_file_path: str, key: bytes) -> dict:
    """Decrypt and load model data."""
    fernet = Fernet(key)
    
    with open(encrypted_file_path, 'rb') as f:
        encrypted_data = f.read()
    
    decrypted_data = fernet.decrypt(encrypted_data)
    return json.loads(decrypted_data)
```

## Deployment Configurations

### Docker Configuration

```dockerfile
# Dockerfile
FROM python:3.12-slim

# Install system dependencies for Chrome
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Virginia Clemm Poe
COPY requirements.txt .
RUN pip install -r requirements.txt

# Create app user
RUN useradd -m -u 1000 vcp
USER vcp

# Setup application
WORKDIR /app
COPY --chown=vcp:vcp . .

# Setup browser
RUN virginia-clemm-poe setup

# Configuration
ENV VCP_HEADLESS=true
ENV VCP_LOG_LEVEL=INFO
ENV VCP_CACHE_ENABLED=true

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s \
    CMD virginia-clemm-poe status || exit 1

CMD ["virginia-clemm-poe", "update", "--all"]
```

### Kubernetes Configuration

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: virginia-clemm-poe
spec:
  replicas: 1
  selector:
    matchLabels:
      app: virginia-clemm-poe
  template:
    metadata:
      labels:
        app: virginia-clemm-poe
    spec:
      containers:
      - name: virginia-clemm-poe
        image: virginia-clemm-poe:latest
        env:
        - name: POE_API_KEY
          valueFrom:
            secretKeyRef:
              name: poe-api-key
              key: api-key
        - name: VCP_HEADLESS
          value: "true"
        - name: VCP_LOG_LEVEL
          value: "INFO"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        volumeMounts:
        - name: data-volume
          mountPath: /data
        - name: config-volume
          mountPath: /config
      volumes:
      - name: data-volume
        persistentVolumeClaim:
          claimName: vcp-data
      - name: config-volume
        configMap:
          name: vcp-config
```

This comprehensive configuration guide provides everything needed to customize and optimize Virginia Clemm Poe for any environment or use case.