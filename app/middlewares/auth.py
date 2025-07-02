"""
JWT Authentication Middleware for FastAPI

This middleware validates incoming JWT tokens for all protected routes. It uses RS256
public key cryptography to verify token integrity and authorizes requests based on user roles.

Environment Variables:
    - public-key: RSA public key used to verify JWT tokens.
    - public-endpoints: Comma-separated list of routes that bypass authentication.
    - ENVIRONMENT: Environment name (e.g., 'local' to bypass token validation during development).
    - roles: Comma-separated list of allowed roles for access.

Usage:
    Add `TokenMiddleware` to your FastAPI app's middleware stack to enforce token-based access control.
"""

import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from jose import JWTError
from starlette.middleware.base import BaseHTTPMiddleware
from jose.jwt import decode
from app.settings.config import get_config

config = get_config()

# Middleware class to handle JWT validation for all incoming requests
class TokenMiddleware(BaseHTTPMiddleware): 
    """
    Middleware to enforce JWT-based authentication and role-based authorization.

    This class intercepts all incoming requests, checks for a valid Bearer token in the
    Authorization header, and verifies it using the public key. It sets user-specific
    attributes (e.g., role, user_id) on the request state for downstream access.
    """
    
    async def dispatch(self, request: Request, call_next):
        
        public_endpoints = config.public_endpoints  # Add your public endpoint(s) here
        public_endpoints = string_to_list(public_endpoints)

        # Check if the request path is one of the public endpoints
        if request.url.path in public_endpoints:
            # Skip token validation for this route
            response = await call_next(request)
            return response

        # Allow local development to bypass token validation
        if config.ENVIRONMENT.lower() == "local":
            # Set a default role for local development
            request.state.role = "local-user"
            response = await call_next(request)
            return response

        # Get the token from the Authorization header (Bearer token)
        authorization = request.headers.get("Authorization")
        
        if not authorization:
            return JSONResponse(status_code=401, content={"error": "Token is missing"})
        
        if not authorization.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"error": "Invalid token format"})

        token = authorization[len("Bearer "):]

        # Decode and validate the token directly inside the middleware
        try:
            # Load the public key from environment variables
            public_key = config.public_key

            # Decode the JWT token using the public key (RS256 algorithm)
            payload = decode(token, public_key, algorithms=["RS256"])

            role = payload.get("extension_Roles")

            user_id = payload.get("user_id")

            roles = config.roles
            
            roles = string_to_list(roles)

            if role not in roles:
                return JSONResponse(status_code=401, content={"error": "You are not allowed to use this API"})
            
            logging.info(f"successfully verified token")
            
            if role:
                request.state.role = role
                
            if user_id:
                request.state.user_id = user_id

        except JWTError as e:
            logging.error(str(e))
            return JSONResponse(status_code=401, content={"error": f"Token decode error: {str(e)}"})

        response = await call_next(request)
        return response
    
def string_to_list(string):
    if isinstance(string, str):
        return string.split(",")
    return string