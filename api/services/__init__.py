"""
API Services Package
Contains business logic services bridging API and core agent
"""

# Import main service
from .agent_service import AgentService, agent_service

# Export service components
__all__ = [
    "AgentService",
    "agent_service"  # Global service instance
]

# Service registry for dependency injection
SERVICES = {
    "agent": agent_service
}