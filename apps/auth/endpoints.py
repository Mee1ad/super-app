from esmerald import post, get, HTTPException, status, Body, Request
from esmerald import Response
import json
from apps.auth.schemas import GoogleAuthRequest, RefreshTokenRequest, LoginResponse, TokenResponse
from apps.auth.services import authenticate_with_google, refresh_access_token
from core.config import settings
import traceback
import urllib.parse

@post(
    path="/google",
    tags=["Authentication"],
    summary="Login with Google OAuth",
    description="Authenticate user using Google OAuth authorization code"
)
async def google_login(request: Request) -> LoginResponse:
    """Login with Google OAuth"""
    try:
        body = await request.json()
        google_auth_request = GoogleAuthRequest(**body)
        return await authenticate_with_google(google_auth_request.code)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )

@get(
    path="/google/callback",
    tags=["Authentication"],
    summary="Google OAuth Callback",
    description="Handle Google OAuth callback at /api/v1/auth/google/callback"
)
async def google_callback(code: str) -> Response:
    try:
        result = await authenticate_with_google(code)
        # Prepare user data and tokens for frontend
        user_data = result.user.model_dump()
        tokens = result.tokens.model_dump()
        # You can use query params or fragment. Here, we'll use fragment for security (not sent to server on redirect)
        # Example: /#user=...&tokens=...
        # But for simplicity, let's use query params (frontend should handle parsing and storing securely)
        payload = json.dumps({"user": user_data, "tokens": tokens})
        redirect_url = f"{settings.client_url}/?auth={urllib.parse.quote(payload)}"
        return Response("", status_code=302, headers={"Location": redirect_url})
    except Exception as e:
        print(traceback.format_exc())  # Print full traceback to server logs
        # Optionally, redirect to an error page
        return Response("", status_code=302, headers={"Location": f"{settings.client_url}/login?error={urllib.parse.quote(str(e))}"})

@post(
    path="/refresh",
    tags=["Authentication"],
    summary="Refresh access token",
    description="Get new access token using refresh token"
)
async def refresh_token(request: Request) -> TokenResponse:
    """Refresh access token"""
    try:
        body = await request.json()
        refresh_token_request = RefreshTokenRequest(**body)
        return await refresh_access_token(refresh_token_request.refresh_token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )

@get(
    path="/google/url",
    tags=["Authentication"],
    summary="Get Google OAuth URL",
    description="Get the Google OAuth authorization URL for frontend redirect"
)
async def get_google_auth_url() -> dict:
    """Get Google OAuth authorization URL"""
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={settings.google_client_id}&"
        "response_type=code&"
        "scope=openid%20email%20profile&"
        f"redirect_uri={settings.google_redirect_uri}&"
        "access_type=offline"
    )
    return {
        "auth_url": google_auth_url,
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri
    } 