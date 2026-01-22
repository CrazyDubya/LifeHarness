# Monitoring and Error Tracking

This document describes the monitoring and error tracking features implemented in LifeHarness.

## Performance Monitoring

### Overview

The application includes a custom performance monitoring middleware that tracks request metrics in real-time.

### Features

- **Request timing**: Measures and logs the duration of each request
- **Slow request detection**: Automatically logs warnings for requests exceeding the threshold (default: 1 second)
- **Performance headers**: Adds `X-Process-Time` and `X-Request-Count` headers to all responses
- **Metrics aggregation**: Tracks total requests, average response time, and slow request percentage

### Endpoints

#### GET /api/monitoring/metrics/performance

Returns current performance metrics (no authentication required).

**Response**:
```json
{
  "total_requests": 1543,
  "total_time": 245.67,
  "average_time": 0.159,
  "slow_requests": 12,
  "slow_request_percentage": 0.78
}
```

#### GET /api/monitoring/health/detailed

Detailed health check with authentication required.

**Headers**: `Authorization: ******

**Response**:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "performance": {
    "total_requests": 1543,
    "average_time": 0.159,
    ...
  },
  "database": "connected",
  "authenticated": true,
  "user_id": "user-uuid"
}
```

### Configuration

The slow request threshold can be configured in `app/main.py`:

```python
app.add_middleware(PerformanceMonitoringMiddleware, slow_request_threshold=1.0)
```

### Logging

Performance logs are written to:
- Console output (DEBUG level for normal requests, WARNING for slow requests)
- `logs/app.log` (all requests)

Example log entries:
```
2026-01-22 10:30:45 - DEBUG - Request completed: GET /api/threads in 0.143s
2026-01-22 10:31:12 - WARNING - Slow request detected: POST /api/threads/step took 1.52s (threshold: 1.0s)
```

---

## Error Tracking with Sentry

### Overview

Sentry integration provides centralized error tracking, performance monitoring, and real-time alerts for production issues.

### Setup

1. **Create a Sentry account** at [https://sentry.io/](https://sentry.io/)

2. **Create a new project** for Python/FastAPI

3. **Copy your DSN** from the project settings

4. **Configure the DSN** in your `.env` file:
   ```
   SENTRY_DSN=https://your-key@sentry.io/your-project-id
   ```

5. **Restart the application** - Sentry will initialize automatically

### Features

- **Automatic error capture**: All unhandled exceptions are sent to Sentry
- **Performance tracking**: Transaction traces for API endpoints
- **Breadcrumbs**: Captures logs leading up to errors
- **Release tracking**: Errors are tagged with environment (development/production)
- **User context**: Errors include authenticated user information
- **SQL tracking**: Database queries are monitored via SQLAlchemy integration

### Configuration

Sentry settings in `app/core/config.py`:

```python
class Settings(BaseSettings):
    # Sentry (optional - for error tracking)
    SENTRY_DSN: Optional[str] = None
```

### Sentry Configuration Details

The Sentry integration is configured in `app/core/sentry_config.py`:

- **Environment-based sampling**:
  - Development: 100% of transactions tracked
  - Production: 10% of transactions tracked (to reduce costs)

- **Integrations**:
  - FastAPI: Automatic endpoint tracking
  - SQLAlchemy: Database query monitoring
  - Logging: Captures logs as breadcrumbs

- **Privacy**:
  - `send_default_pii=False`: Personal data is not sent by default
  - Customize what data is sent via Sentry's data scrubbing rules

### Manual Error Capture

You can manually capture errors with additional context:

```python
from app.core.sentry_config import capture_exception, capture_message

try:
    # Your code
    risky_operation()
except Exception as e:
    capture_exception(e, extra_context={
        "user_action": "generate_autobiography",
        "thread_id": str(thread_id)
    })
```

Capture informational messages:

```python
capture_message("User completed onboarding", level="info")
```

### Viewing Errors

1. Log in to [https://sentry.io/](https://sentry.io/)
2. Navigate to your project
3. View the Issues dashboard for:
   - Error frequency and trends
   - Stack traces with source code
   - User impact metrics
   - Performance bottlenecks

### Disabling Sentry

If you don't configure a SENTRY_DSN, Sentry will be disabled and the application will log:
```
INFO - Sentry DSN not configured. Error tracking disabled.
```

---

## Best Practices

### Performance Monitoring

1. **Monitor slow requests** regularly and investigate spikes
2. **Set appropriate thresholds** based on your SLAs (default: 1s)
3. **Review metrics** before and after deployments
4. **Alert on degradation** - set up notifications for slow request percentage increases

### Error Tracking

1. **Test Sentry integration** in development before going to production
2. **Set up alerts** for error rate increases
3. **Review errors weekly** and prioritize fixes
4. **Use releases** to track which version introduced issues
5. **Add custom context** to errors for better debugging:
   ```python
   with sentry_sdk.push_scope() as scope:
       scope.set_tag("feature", "autobiography")
       scope.set_extra("word_count", word_count)
       # Your code that might fail
   ```

### Production Deployment

For production environments:

1. **Set ENVIRONMENT=production** in `.env`
2. **Configure SENTRY_DSN** with your production project
3. **Lower the slow request threshold** (e.g., 0.5s for better performance)
4. **Set up Sentry alerts** for:
   - Error rate exceeds threshold
   - New issues detected
   - Performance regression detected

---

## Testing

Run monitoring tests:

```bash
cd backend
pytest tests/test_monitoring.py -v
```

Test coverage for monitoring:
- Performance metrics endpoint
- Performance headers in responses
- Detailed health check with authentication
- Metrics structure validation

---

## Troubleshooting

### Sentry Not Initializing

**Issue**: Logs show "Sentry DSN not configured"

**Solution**: 
1. Check `.env` file contains `SENTRY_DSN=https://...`
2. Verify the DSN is correct (copy from Sentry project settings)
3. Restart the application

### Slow Requests Not Logged

**Issue**: Requests are slow but no warnings appear

**Solution**:
1. Check the `slow_request_threshold` setting in `main.py`
2. Verify logging level is set to WARNING or lower
3. Check `logs/app.log` for entries

### Performance Headers Missing

**Issue**: `X-Process-Time` header not in responses

**Solution**:
1. Verify middleware is added in `main.py`
2. Check middleware is not bypassed by exceptions
3. Test with a simple endpoint like `/health`

---

## Future Enhancements

Potential improvements for monitoring:

1. **Database connection pool monitoring**
2. **Memory usage tracking**
3. **LLM API call metrics** (latency, token usage, costs)
4. **Custom business metrics** (threads created, questions answered, etc.)
5. **Grafana/Prometheus integration** for advanced visualization
6. **Automated alerting** via email/Slack for critical issues
