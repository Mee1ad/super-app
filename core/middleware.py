# Global middleware (CORS, gzip, logging, etc.)
from typing import Any, Dict, List
from esmerald import Request, Response
from esmerald.middleware import Middleware
from esmerald.middleware.cors import CORSMiddleware


class CustomCORSMiddleware(CORSMiddleware):
    """Custom CORS middleware with specific configuration"""
    
    def __init__(self):
        super().__init__(
            allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
            allow_headers=[
                "Accept",
                "Accept-Language",
                "Content-Language",
                "Content-Type",
                "Authorization",
                "X-Requested-With",
                "Origin",
                "Access-Control-Request-Method",
                "Access-Control-Request-Headers",
            ],
        ) 