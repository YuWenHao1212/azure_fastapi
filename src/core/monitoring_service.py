"""
Azure Application Insights integration for monitoring and telemetry.
"""
import logging
import os
from typing import Optional, Dict, Any
from datetime import datetime, timezone

from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.ext.azure import metrics_exporter
from opencensus.trace import tracer as tracer_module
from opencensus.trace.samplers import ProbabilitySampler
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.stats import aggregation as aggregation_module
from opencensus.stats import measure as measure_module
from opencensus.stats import stats as stats_module
from opencensus.stats import view as view_module
from opencensus.tags import tag_map as tag_map_module
from opencensus.tags import tag_key as tag_key_module

logger = logging.getLogger(__name__)


class MonitoringService:
    """Service for Application Insights monitoring and custom metrics."""
    
    def __init__(self):
        self.instrumentation_key = os.getenv(
            "APPINSIGHTS_INSTRUMENTATIONKEY",
            "a2fa7c8c-1440-4754-a1d8-ca58a0a82af0"  # From monitoring_setup.md
        )
        self.is_enabled = os.getenv("MONITORING_ENABLED", "true").lower() == "true"
        
        if self.is_enabled:
            self._setup_monitoring()
        else:
            logger.info("Monitoring is disabled")
    
    def _setup_monitoring(self):
        """Initialize Application Insights components."""
        try:
            self._setup_logging()
            self._setup_tracing()
            self._setup_metrics()
            logger.info(f"Monitoring service initialized (Key: {self.instrumentation_key[:8]}...)")
        except Exception as e:
            logger.error(f"Failed to initialize monitoring: {e}")
            self.is_enabled = False
    
    def track_request(self, endpoint: str, method: str, duration_ms: float, 
                     success: bool, status_code: int, custom_properties: Optional[Dict[str, Any]] = None):
        """Track API request metrics."""
        if not self.is_enabled:
            return
        
        properties = {
            "endpoint": endpoint,
            "method": method,
            "duration_ms": duration_ms,
            "success": success,
            "status_code": status_code,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        if custom_properties:
            properties.update(custom_properties)
        
        # Send custom event to Application Insights
        if hasattr(self, 'logger'):
            self.logger.info(
                "RequestTracked",
                extra={
                    "custom_dimensions": properties
                }
            )
    
    def track_keyword_extraction(self, language: str, prompt_version: str,
                               keyword_count: int, duration_ms: float,
                               success: bool, confidence_score: float):
        """Track keyword extraction business metrics."""
        if not self.is_enabled:
            return
        
        metrics = {
            "language": language,
            "prompt_version": prompt_version,
            "keyword_count": keyword_count,
            "duration_ms": duration_ms,
            "success": success,
            "confidence_score": confidence_score,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Send custom metrics
        if hasattr(self, 'metrics_recorder'):
            self._record_custom_metric(
                "keyword_extraction",
                metrics
            )
    
    def track_error(self, error_type: str, error_message: str, 
                   endpoint: Optional[str] = None, custom_properties: Optional[Dict[str, Any]] = None):
        """Track errors and exceptions."""
        if not self.is_enabled:
            return
        
        properties = {
            "error_type": error_type,
            "error_message": error_message,
            "endpoint": endpoint or "unknown",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        if custom_properties:
            properties.update(custom_properties)
        
        # Send error to Application Insights
        if hasattr(self, 'logger'):
            self.logger.error(
                f"Error: {error_type}",
                extra={
                    "custom_dimensions": properties
                },
                exc_info=True
            )
    
    def track_dependency(self, dependency_type: str, dependency_name: str,
                        duration_ms: float, success: bool, data: Optional[str] = None):
        """Track external dependency calls (e.g., OpenAI API)."""
        if not self.is_enabled:
            return
        
        dependency_data = {
            "type": dependency_type,
            "name": dependency_name,
            "duration_ms": duration_ms,
            "success": success,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Track dependency
        if hasattr(self, 'tracer'):
            with self.tracer.span(name=f"{dependency_type}.{dependency_name}") as span:
                span.add_attribute("dependency.type", dependency_type)
                span.add_attribute("dependency.name", dependency_name)
                span.add_attribute("dependency.duration_ms", duration_ms)
                span.add_attribute("dependency.success", success)
                if data:
                    span.add_attribute("dependency.data", data)


    def _setup_logging(self):
        """Setup Azure logging handler."""
        handler = AzureLogHandler(
            connection_string=f"InstrumentationKey={self.instrumentation_key}"
        )
        handler.setLevel(logging.INFO)
        
        # Create a dedicated logger for Application Insights
        self.logger = logging.getLogger("azure.monitoring")
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def _setup_tracing(self):
        """Setup distributed tracing."""
        self.tracer = tracer_module.Tracer(
            exporter=AzureExporter(
                connection_string=f"InstrumentationKey={self.instrumentation_key}"
            ),
            sampler=ProbabilitySampler(1.0)
        )
    
    def _setup_metrics(self):
        """Setup custom metrics exporter."""
        self.stats = stats_module.stats
        self.view_manager = self.stats.view_manager
        self.stats_recorder = self.stats.stats_recorder
        
        # Register the exporter
        exporter = metrics_exporter.new_metrics_exporter(
            connection_string=f"InstrumentationKey={self.instrumentation_key}"
        )
        self.view_manager.register_exporter(exporter)
        
        # Define measures
        self.request_duration_measure = measure_module.MeasureFloat(
            "request_duration",
            "The duration of requests in milliseconds",
            "ms"
        )
        
        self.keyword_count_measure = measure_module.MeasureInt(
            "keyword_count",
            "Number of keywords extracted",
            "keywords"
        )
        
        # Define tags
        self.endpoint_key = tag_key_module.TagKey("endpoint")
        self.method_key = tag_key_module.TagKey("method")
        self.status_key = tag_key_module.TagKey("status")
        self.language_key = tag_key_module.TagKey("language")
        
        # Create views
        self._create_views()
    
    def _create_views(self):
        """Create and register metric views."""
        # Request duration view
        duration_view = view_module.View(
            "request_duration_distribution",
            "Distribution of request durations",
            [self.endpoint_key, self.method_key, self.status_key],
            self.request_duration_measure,
            aggregation_module.DistributionAggregation(
                [50, 100, 200, 500, 1000, 2000, 5000, 10000]
            )
        )
        
        # Keyword count view
        keyword_view = view_module.View(
            "keyword_count_distribution",
            "Distribution of keyword counts",
            [self.language_key],
            self.keyword_count_measure,
            aggregation_module.DistributionAggregation(
                [5, 10, 12, 15, 20, 25, 30]
            )
        )
        
        # Register views
        self.view_manager.register_view(duration_view)
        self.view_manager.register_view(keyword_view)
    
    def _record_custom_metric(self, metric_name: str, properties: Dict[str, Any]):
        """Record custom metrics to Application Insights."""
        if hasattr(self, 'logger'):
            self.logger.info(
                f"CustomMetric.{metric_name}",
                extra={
                    "custom_dimensions": properties
                }
            )
    
    def track_metric(self, name: str, value: float, properties: Optional[Dict[str, Any]] = None):
        """Track a custom metric."""
        if not self.is_enabled:
            return
        
        metric_properties = {
            "metric_name": name,
            "metric_value": value,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        if properties:
            metric_properties.update(properties)
        
        self._record_custom_metric(name, metric_properties)
    
    def track_event(self, name: str, properties: Optional[Dict[str, Any]] = None):
        """Track a custom event."""
        if not self.is_enabled:
            return
        
        event_properties = {
            "event_name": name,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        if properties:
            event_properties.update(properties)
        
        if hasattr(self, 'logger'):
            self.logger.info(
                f"CustomEvent.{name}",
                extra={
                    "custom_dimensions": event_properties
                }
            )


# Global monitoring instance
monitoring_service = MonitoringService()