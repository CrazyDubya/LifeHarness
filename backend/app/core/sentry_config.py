"""Sentry error tracking configuration."""
import logging
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from app.core.config import settings

logger = logging.getLogger(__name__)


def init_sentry():
    """
    Initialize Sentry error tracking.
    
    Sentry is only enabled if SENTRY_DSN is configured in environment variables.
    In development, errors are logged locally instead.
    """
    sentry_dsn = getattr(settings, 'SENTRY_DSN', None)
    
    if not sentry_dsn:
        logger.info("Sentry DSN not configured. Error tracking disabled.")
        return
    
    try:
        # Configure Sentry integrations
        sentry_sdk.init(
            dsn=sentry_dsn,
            environment=settings.ENVIRONMENT,
            traces_sample_rate=1.0 if settings.ENVIRONMENT == "development" else 0.1,
            profiles_sample_rate=1.0 if settings.ENVIRONMENT == "development" else 0.1,
            integrations=[
                FastApiIntegration(transaction_style="endpoint"),
                SqlalchemyIntegration(),
                LoggingIntegration(
                    level=logging.INFO,  # Capture info and above as breadcrumbs
                    event_level=logging.ERROR  # Send errors as events
                ),
            ],
            # Set release version for tracking
            release=f"lifeharness@{settings.ENVIRONMENT}",
            
            # Additional options
            send_default_pii=False,  # Don't send personally identifiable information
            attach_stacktrace=True,
            max_breadcrumbs=50,
        )
        
        logger.info(f"Sentry initialized for environment: {settings.ENVIRONMENT}")
        
    except Exception as e:
        logger.error(f"Failed to initialize Sentry: {e}")


def capture_exception(error: Exception, extra_context: dict = None):
    """
    Manually capture an exception to Sentry.
    
    Args:
        error: The exception to capture
        extra_context: Additional context to attach to the error
    """
    if extra_context:
        with sentry_sdk.push_scope() as scope:
            for key, value in extra_context.items():
                scope.set_extra(key, value)
            sentry_sdk.capture_exception(error)
    else:
        sentry_sdk.capture_exception(error)


def capture_message(message: str, level: str = "info"):
    """
    Capture a message to Sentry.
    
    Args:
        message: The message to capture
        level: Log level (debug, info, warning, error, fatal)
    """
    sentry_sdk.capture_message(message, level)
