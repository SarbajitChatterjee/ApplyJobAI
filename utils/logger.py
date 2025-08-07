"""
Comprehensive Logging System
Handles all logging requirements for the CV & Motivation Letter Agent
"""

import logging
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
import functools

class AgentLogger:
    """Centralized logging system for the agent"""
    
    def __init__(self, session_id: str = None):
        self.session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.setup_loggers()
    
    def setup_loggers(self):
        """Setup different loggers for different purposes"""
        # Create logs directory
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        
        # Main application logger
        self.app_logger = self._create_logger(
            'app', 
            os.path.join(log_dir, f'app_{self.session_id}.log'),
            level=logging.INFO
        )
        
        # API interaction logger
        self.api_logger = self._create_logger(
            'api', 
            os.path.join(log_dir, f'api_calls_{self.session_id}.log'),
            level=logging.DEBUG
        )
        
        # User interaction logger
        self.interaction_logger = self._create_logger(
            'interaction', 
            os.path.join(log_dir, f'interactions_{self.session_id}.log'),
            level=logging.INFO
        )
        
        # Error logger
        self.error_logger = self._create_logger(
            'error', 
            os.path.join(log_dir, f'errors_{self.session_id}.log'),
            level=logging.ERROR
        )
        
        # Performance logger
        self.perf_logger = self._create_logger(
            'performance', 
            os.path.join(log_dir, f'performance_{self.session_id}.log'),
            level=logging.INFO
        )
    
    def _create_logger(self, name: str, filename: str, level: int) -> logging.Logger:
        """Create a configured logger"""
        logger = logging.getLogger(f"{name}_{self.session_id}")
        logger.setLevel(level)
        
        # Avoid duplicate handlers
        if not logger.handlers:
            # File handler
            file_handler = logging.FileHandler(filename, encoding='utf-8')
            file_handler.setLevel(level)
            
            # Console handler for errors and important info
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.WARNING if name != 'app' else logging.INFO)
            
            # Formatter
            formatter = logging.Formatter(
                '%(asctime)s | %(levelname)s | %(name)s | %(funcName)s:%(lineno)d | %(message)s'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
        
        return logger
    
    # Logging methods for different types
    def log_app_start(self, config: Dict[str, Any]):
        """Log application startup"""
        self.app_logger.info(f"🚀 Agent started with session ID: {self.session_id}")
        self.app_logger.info(f"Configuration: {json.dumps(config, indent=2)}")
    
    def log_api_call(self, endpoint: str, payload: Dict[str, Any], response_size: int = 0):
        """Log API calls"""
        self.api_logger.info(f"API Call to {endpoint}")
        self.api_logger.debug(f"Payload size: {len(str(payload))} chars")
        self.api_logger.debug(f"Response size: {response_size} chars")
    
    def log_api_error(self, endpoint: str, error: str, payload_size: int = 0):
        """Log API errors"""
        self.api_logger.error(f"API Error at {endpoint}: {error}")
        self.error_logger.error(f"API Error: {endpoint} | Payload size: {payload_size} | Error: {error}")
    
    def log_user_interaction(self, action: str, section: str = None, user_input: str = None):
        """Log user interactions"""
        message = f"User Action: {action}"
        if section:
            message += f" | Section: {section}"
        if user_input:
            message += f" | Input: {user_input[:100]}..." if len(user_input) > 100 else f" | Input: {user_input}"
        
        self.interaction_logger.info(message)
    
    def log_file_operation(self, operation: str, filepath: str, success: bool = True, error: str = None):
        """Log file operations"""
        if success:
            self.app_logger.info(f"File {operation}: {filepath}")
        else:
            self.error_logger.error(f"File {operation} failed: {filepath} | Error: {error}")
    
    def log_processing_step(self, step: str, details: str = None):
        """Log processing steps"""
        message = f"Processing: {step}"
        if details:
            message += f" | {details}"
        self.app_logger.info(message)
    
    def log_performance(self, operation: str, duration: float, details: Dict[str, Any] = None):
        """Log performance metrics"""
        message = f"Performance: {operation} took {duration:.2f}s"
        if details:
            message += f" | Details: {json.dumps(details)}"
        self.perf_logger.info(message)
    
    def log_error(self, error: Exception, context: str = None):
        """Log errors with context"""
        message = f"Error: {str(error)}"
        if context:
            message = f"Context: {context} | {message}"
        
        self.error_logger.error(message, exc_info=True)
        self.app_logger.error(message)

# Decorator for automatic function logging
def log_function_call(logger_instance):
    """Decorator to automatically log function calls"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = datetime.now()
            func_name = f"{func.__module__}.{func.__name__}"
            
            try:
                logger_instance.app_logger.debug(f"Starting {func_name}")
                result = func(*args, **kwargs)
                
                duration = (datetime.now() - start_time).total_seconds()
                logger_instance.log_performance(func_name, duration)
                
                logger_instance.app_logger.debug(f"Completed {func_name}")
                return result
                
            except Exception as e:
                logger_instance.log_error(e, f"Function: {func_name}")
                raise
                
        return wrapper
    return decorator

# Global logger instance
_global_logger = None

def get_logger(session_id: str = None) -> AgentLogger:
    """Get or create global logger instance"""
    global _global_logger
    if _global_logger is None or session_id:
        _global_logger = AgentLogger(session_id)
    return _global_logger