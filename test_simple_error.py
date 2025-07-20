#!/usr/bin/env python3
"""
Simple test to verify exception handling is working
"""

from esmerald import get
import logging

logger = logging.getLogger(__name__)

@get("/test-simple-error")
def test_simple_error():
    """Simple test endpoint that raises an error"""
    logger.info("Simple error test endpoint called")
    print("🔍 DEBUG: Simple error test endpoint called")
    print("🔍 DEBUG: About to raise ValueError")
    
    # Raise a simple error
    raise ValueError("This is a simple test error")
    
    return {"message": "This should never be reached"} 