"""
Logging Configuration for Advanced Animation System

This module provides centralized logging configuration that saves logs
to separate files for each run, making debugging and tracking easier.
"""

import os
import logging
import logging.handlers
from datetime import datetime
from pathlib import Path
from typing import Optional, Any, Dict, List
import json

class LoggingManager:
    """Manages logging configuration for the advanced animation system."""
    
    def __init__(self, output_dir: str = "logs", log_level: int = logging.INFO):
        """
        Initialize the logging manager.
        
        Args:
            output_dir: Directory to store log files
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.output_dir = Path(output_dir)
        self.log_level = log_level
        self.log_file = None
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration with file and console handlers."""
        # Create logs directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create timestamp for this run
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.output_dir / f"animation_run_{timestamp}.log"
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(self.log_level)
        
        # Clear any existing handlers
        root_logger.handlers.clear()
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        console_formatter = logging.Formatter(
            '%(levelname)s - %(name)s - %(message)s'
        )
        
        # File handler (detailed logging)
        file_handler = logging.handlers.RotatingFileHandler(
            self.log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(detailed_formatter)
        
        # Console handler (simplified for terminal)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.log_level)
        console_handler.setFormatter(console_formatter)
        
        # Add handlers to root logger
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        # Log the start of this session
        logger = logging.getLogger(__name__)
        logger.info(f"Logging session started - Log file: {self.log_file}")
        logger.info(f"Log level: {logging.getLevelName(self.log_level)}")
    
    def get_log_file_path(self) -> Optional[Path]:
        """Get the current log file path."""
        return self.log_file
    
    def log_system_info(self):
        """Log system information for debugging."""
        logger = logging.getLogger(__name__)
        
        import sys
        import platform
        
        logger.info("=" * 60)
        logger.info("SYSTEM INFORMATION")
        logger.info("=" * 60)
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Platform: {platform.platform()}")
        logger.info(f"Architecture: {platform.architecture()}")
        logger.info(f"Processor: {platform.processor()}")
        logger.info(f"Working directory: {os.getcwd()}")
        logger.info("=" * 60)
    
    def log_environment_info(self):
        """Log environment information for debugging."""
        logger = logging.getLogger(__name__)
        
        logger.info("=" * 60)
        logger.info("ENVIRONMENT INFORMATION")
        logger.info("=" * 60)
        
        # Check for important environment variables
        env_vars = [
            'OPENAI_API_KEY',
            'ELEVENLABS_API_KEY',
            'E2B_API_KEY',
            'PYTHONPATH',
            'GITHUB_TOKEN',
            'GITLAB_TOKEN',
            'BITBUCKET_TOKEN'
        ]
        
        for var in env_vars:
            value = os.getenv(var)
            if value:
                # Mask sensitive values
                if any(keyword in var for keyword in ['API_KEY', 'TOKEN', 'SECRET', 'PASSWORD']):
                    masked_value = value[:4] + '*' * max(8, len(value) - 8) + value[-4:] if len(value) > 8 else '***'
                    logger.info(f"{var}: {masked_value}")
                else:
                    logger.info(f"{var}: {value}")
            else:
                logger.warning(f"{var}: Not set")
        
        logger.info("=" * 60)

def setup_logging_for_run(output_dir: str = "logs", log_level: int = logging.INFO) -> LoggingManager:
    """
    Setup logging for a new run.
    
    Args:
        output_dir: Directory to store log files
        log_level: Logging level
        
    Returns:
        LoggingManager instance
    """
    manager = LoggingManager(output_dir, log_level)
    manager.log_system_info()
    manager.log_environment_info()
    return manager

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class AnalyticsManager:
    """Manages analytics and feedback collection."""
    
    def __init__(self, analytics_enabled: bool = True):
        """
        Initialize the analytics manager.
        
        Args:
            analytics_enabled: Whether analytics collection is enabled
        """
        self.analytics_enabled = analytics_enabled
        self.feedback_data = []
        self.video_views = {}
        self.user_preferences = {}
        
        logger = logging.getLogger(__name__)
        if analytics_enabled:
            logger.info("Analytics collection enabled")
        else:
            logger.info("Analytics collection disabled")
    
    def track_video_view(self, video_id: str, user_id: Optional[str] = None, metadata: Optional[dict] = None):
        """
        Track a video view event.
        
        Args:
            video_id: ID of the video being viewed
            user_id: Optional user ID
            metadata: Additional metadata about the view
        """
        if not self.analytics_enabled:
            return
        
        view_data = {
            'video_id': video_id,
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'metadata': metadata or {}
        }
        
        # Update video views count
        if video_id not in self.video_views:
            self.video_views[video_id] = []
        self.video_views[video_id].append(view_data)
        
        logger = logging.getLogger(__name__)
        logger.info(f"Tracked video view: {video_id}")
    
    def collect_feedback(self, feedback_type: str, feedback_data: dict):
        """
        Collect user feedback.
        
        Args:
            feedback_type: Type of feedback (e.g., 'video_quality', 'content_relevance')
            feedback_data: Feedback data dictionary
        """
        if not self.analytics_enabled:
            return
        
        feedback_entry = {
            'type': feedback_type,
            'timestamp': datetime.now().isoformat(),
            'data': feedback_data
        }
        
        self.feedback_data.append(feedback_entry)
        
        logger = logging.getLogger(__name__)
        logger.info(f"Collected {feedback_type} feedback")
    
    def record_user_preference(self, preference_key: str, preference_value: Any):
        """
        Record user preference.
        
        Args:
            preference_key: Key for the preference
            preference_value: Value of the preference
        """
        if not self.analytics_enabled:
            return
        
        self.user_preferences[preference_key] = preference_value
        
        logger = logging.getLogger(__name__)
        logger.info(f"Recorded user preference: {preference_key}")
    
    def get_analytics_summary(self) -> dict:
        """
        Get a summary of collected analytics.
        
        Returns:
            Dictionary containing analytics summary
        """
        return {
            'total_video_views': sum(len(views) for views in self.video_views.values()),
            'unique_videos_viewed': len(self.video_views),
            'total_feedback_entries': len(self.feedback_data),
            'total_user_preferences': len(self.user_preferences),
            'most_viewed_video': max(self.video_views.items(), key=lambda x: len(x[1]))[0] if self.video_views else None
        }
    
    def export_analytics(self, output_dir: str = "analytics") -> str:
        """
        Export analytics data to JSON files.
        
        Args:
            output_dir: Directory to export analytics data
            
        Returns:
            Path to the exported analytics file
        """
        if not self.analytics_enabled:
            return ""
        
        try:
            # Create output directory
            Path(output_dir).mkdir(exist_ok=True)
            
            # Export video views
            views_file = Path(output_dir) / f"video_views_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(views_file, 'w') as f:
                json.dump(self.video_views, f, indent=2)
            
            # Export feedback data
            feedback_file = Path(output_dir) / f"feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(feedback_file, 'w') as f:
                json.dump(self.feedback_data, f, indent=2)
            
            # Export user preferences
            prefs_file = Path(output_dir) / f"user_preferences_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(prefs_file, 'w') as f:
                json.dump(self.user_preferences, f, indent=2)
            
            logger = logging.getLogger(__name__)
            logger.info(f"Exported analytics data to {output_dir}")
            
            return str(views_file)
            
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Error exporting analytics: {e}")
            return "" 