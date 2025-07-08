import os
import httpx
import jwt
from fastapi import HTTPException
from chainlit.user import User
from chainlit.oauth_providers import OAuthProvider
import json


class OrgOAuthProvider(OAuthProvider):
    id = "org-openid"
    env = [
        "OAUTH_ORG_CLIENT_ID",
        "OAUTH_ORG_CLIENT_SECRET", 
        "OAUTH_ORG_AUTHORIZE_URL",
        "OAUTH_ORG_TOKEN_URL",
        "OAUTH_ORG_USERINFO_URL",
        "OAUTH_ORG_JWKS_URL",  # Optional for JWT validation
        "OAUTH_ORG_ISSUER",    # Optional for JWT validation
    ]

    def __init__(self):
        self.client_id = os.environ.get("OAUTH_ORG_CLIENT_ID")
        self.client_secret = os.environ.get("OAUTH_ORG_CLIENT_SECRET")
        self.authorize_url = os.environ.get("OAUTH_ORG_AUTHORIZE_URL")
        self.token_url = os.environ.get("OAUTH_ORG_TOKEN_URL")
        self.userinfo_url = os.environ.get("OAUTH_ORG_USERINFO_URL")
        self.jwks_url = os.environ.get("OAUTH_ORG_JWKS_URL")
        self.issuer = os.environ.get("OAUTH_ORG_ISSUER")
        
        self.authorize_params = {
            "response_type": "code",
            "scope": "openid profile email groups",
            "response_mode": "query",
        }

    async def get_token(self, code: str, url: str) -> str:
        """Exchange authorization code for access token"""
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": url,
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(self.token_url, data=payload)
            response.raise_for_status()
            response_json = response.json()

            # Try to get access_token first, then id_token as fallback
            token = response_json.get("access_token") or response_json.get("id_token")
            
            if not token:
                raise HTTPException(
                    status_code=400, detail="Failed to get the access token"
                )

            return token

    async def get_user_info(self, token: str):
        """Get user information from the OpenID userinfo endpoint"""
        headers = {"Authorization": f"Bearer {token}"}
        
        async with httpx.AsyncClient() as client:
            try:
                # Try userinfo endpoint first
                response = await client.get(self.userinfo_url, headers=headers)
                response.raise_for_status()
                user_info = response.json()
                
                print("OpenID user info:", json.dumps(user_info, indent=2))
                
                # Check if user has required group
                user_groups = user_info.get('groups', [])
                required_group = 'us\\us.employees'
                
                if required_group not in user_groups:
                    raise HTTPException(
                        status_code=403, 
                        detail=f"Access denied. User must be member of '{required_group}' group."
                    )
                
                # Create user object
                user_name = user_info.get('name', 'Unknown User')
                user_email = user_info.get('sub', user_info.get('email', 'unknown@unknown.com'))
                employee_id = user_info.get('employee_id', '')
                
                user = User(
                    identifier=user_email,
                    metadata={
                        "name": user_name,
                        "employee_id": employee_id,
                        "groups": user_groups,
                        "provider": "org-openid"
                    }
                )
                
                return user_info, user
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    # Try to decode JWT token directly if userinfo endpoint fails
                    try:
                        # Decode without verification for debugging
                        decoded = jwt.decode(token, options={"verify_signature": False})
                        print("Decoded JWT:", json.dumps(decoded, indent=2))
                        
                        # Check groups
                        user_groups = decoded.get('groups', [])
                        required_group = 'us\\us.employees'
                        
                        if required_group not in user_groups:
                            raise HTTPException(
                                status_code=403, 
                                detail=f"Access denied. User must be member of '{required_group}' group."
                            )
                        
                        user_name = decoded.get('name', 'Unknown User')
                        user_email = decoded.get('sub', decoded.get('email', 'unknown@unknown.com'))
                        employee_id = decoded.get('employee_id', '')
                        
                        user = User(
                            identifier=user_email,
                            metadata={
                                "name": user_name,
                                "employee_id": employee_id,
                                "groups": user_groups,
                                "provider": "org-openid"
                            }
                        )
                        
                        return decoded, user
                        
                    except Exception as jwt_error:
                        print(f"JWT decode error: {jwt_error}")
                        raise HTTPException(
                            status_code=400, detail="Failed to get user info from token"
                        )
                else:
                    raise e
            except Exception as e:
                print(f"Error getting user info: {e}")
                raise HTTPException(
                    status_code=400, detail="Failed to get the user info"
                ) 