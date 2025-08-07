"""
LM Studio API Client with Comprehensive Logging
"""

import requests
import json
from typing import List, Dict, Any, Optional
import time
from datetime import datetime

from .logger import get_logger

class LMStudioClient:
    """Wrapper class for LM Studio API interactions with full logging"""
    
    def __init__(self):
        """Initialize with environment variables"""
        from config.settings import LM_STUDIO_URL, MODEL_NAME, REQUEST_TIMEOUT
        
        self.base_url = LM_STUDIO_URL.rstrip('/')
        self.model_name = MODEL_NAME
        self.timeout = REQUEST_TIMEOUT
        self.api_endpoint = f"{self.base_url}/v1/chat/completions"
        
        from utils.logger import get_logger
        self.logger = get_logger()
        
        self.logger.log_processing_step(
            "API Client Initialization",
            f"URL: {self.base_url}, Model: {self.model_name}, Timeout: {self.timeout}s"
        )
        
        self._test_connection()
    
    def _test_connection(self):
        """Test connection to LM Studio with detailed logging"""
        try:
            self.logger.log_processing_step("Testing LM Studio Connection")
            
            start_time = datetime.now()
            response = requests.get(f"{self.base_url}/v1/models", timeout=5)
            duration = (datetime.now() - start_time).total_seconds()
            
            if response.status_code == 200:
                models_data = response.json()
                self.logger.log_api_call("/v1/models", {}, len(response.text))
                self.logger.log_performance("Connection Test", duration, 
                                          {"status": "success", "models_count": len(models_data.get('data', []))})
                self.logger.app_logger.info(f"✅ Connected to LM Studio at {self.base_url}")
            else:
                self.logger.log_api_error("/v1/models", f"Status {response.status_code}", 0)
                self.logger.app_logger.warning(f"⚠️ LM Studio responded with status {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            self.logger.log_api_error("/v1/models", str(e), 0)
            self.logger.log_error(e, "LM Studio Connection Test")
            self.logger.app_logger.error(f"❌ Could not connect to LM Studio: {str(e)}")
    
    def chat_completion(self, messages: List[Dict[str, str]], 
                       temperature: float = 0.5,
                       max_tokens: Optional[int] = None,
                       stream: bool = False) -> str:
        """Chat completion with comprehensive logging"""
        
        # Log request details
        request_id = datetime.now().strftime("%H%M%S%f")
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "stream": stream
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        # Log the request
        payload_size = len(json.dumps(payload))
        self.logger.log_api_call("chat/completions", payload, 0)
        self.logger.api_logger.info(f"Request ID: {request_id} | Payload size: {payload_size} chars")
        
        # Log message details
        for i, msg in enumerate(messages):
            msg_size = len(msg.get('content', ''))
            self.logger.api_logger.debug(f"Request {request_id} | Message {i}: {msg['role']} ({msg_size} chars)")
        
        start_time = datetime.now()
        
        try:
            self.logger.log_processing_step("Sending API Request", f"ID: {request_id}")
            
            response = requests.post(
                self.api_endpoint,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=300
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            if response.status_code == 200:
                result = response.json()
                response_content = result["choices"][0]["message"]["content"]
                response_size = len(response_content)
                
                # Log successful response
                self.logger.log_api_call("chat/completions", payload, response_size)
                self.logger.log_performance(f"API Call {request_id}", duration, {
                    "status": "success",
                    "response_size": response_size,
                    "tokens_estimated": response_size // 4
                })
                
                self.logger.api_logger.info(f"Request {request_id} completed successfully | Response: {response_size} chars")
                
                return response_content
                
            else:
                error_msg = f"Status {response.status_code}: {response.text}"
                self.logger.log_api_error("chat/completions", error_msg, payload_size)
                self.logger.log_performance(f"API Call {request_id}", duration, {"status": "error"})
                
                raise Exception(f"API request failed: {error_msg}")
                
        except requests.exceptions.Timeout:
            duration = (datetime.now() - start_time).total_seconds()
            self.logger.log_api_error("chat/completions", "Request timeout", payload_size)
            self.logger.log_performance(f"API Call {request_id}", duration, {"status": "timeout"})
            raise
            
        except requests.exceptions.RequestException as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.logger.log_api_error("chat/completions", str(e), payload_size)
            self.logger.log_performance(f"API Call {request_id}", duration, {"status": "network_error"})
            self.logger.log_error(e, f"API Request {request_id}")
            raise
    
    def chat_completion_stream(self, messages: List[Dict[str, str]], 
                              temperature: float = 0.5) -> str:
        """Stream chat completion with detailed logging"""
        
        request_id = datetime.now().strftime("%H%M%S%f")
        self.logger.log_processing_step("Starting Streaming Request", f"ID: {request_id}")
        
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "stream": True
        }
        
        start_time = datetime.now()
        
        try:
            response = requests.post(
                self.api_endpoint,
                json=payload,
                headers={"Content-Type": "application/json"},
                stream=True,
                timeout=300
            )
            
            if response.status_code == 200:
                full_response = ""
                chunk_count = 0
                
                for line in response.iter_lines():
                    if line:
                        chunk_count += 1
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            data = line[6:]
                            if data.strip() == '[DONE]':
                                break
                            try:
                                chunk = json.loads(data)
                                if 'choices' in chunk and len(chunk['choices']) > 0:
                                    delta = chunk['choices'][0].get('delta', {})
                                    if 'content' in delta:
                                        content = delta['content']
                                        full_response += content
                                        print(content, end='', flush=True)
                            except json.JSONDecodeError:
                                continue
                
                duration = (datetime.now() - start_time).total_seconds()
                
                # Log streaming completion
                self.logger.log_performance(f"Streaming {request_id}", duration, {
                    "chunks_received": chunk_count,
                    "final_response_size": len(full_response)
                })
                
                print()  # New line after streaming
                return full_response
            else:
                error_msg = f"Streaming failed with status {response.status_code}"
                self.logger.log_api_error("chat/completions (stream)", error_msg, len(json.dumps(payload)))
                raise Exception(error_msg)
                
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.logger.log_error(e, f"Streaming Request {request_id}")
            self.logger.log_performance(f"Streaming {request_id}", duration, {"status": "error"})
            raise
