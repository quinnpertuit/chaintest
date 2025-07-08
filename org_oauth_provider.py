import os
import httpx
import json
from fastapi import HTTPException
from chainlit.user import User
from chainlit.oauth_providers import OAuthProvider


class OrgOAuthProvider(OAuthProvider):
    id = "org-openid"
    env = [
        "OAUTH_ORG_CLIENT_ID",
        "OAUTH_ORG_CLIENT_SECRET",
        "OAUTH_ORG_AUTHORIZE_URL",
        "OAUTH_ORG_TOKEN_URL", 
        "OAUTH_ORG_USERINFO_URL"
    ]

    def __init__(self):
        self.client_id = os.environ.get("OAUTH_ORG_CLIENT_ID")
        self.client_secret = os.environ.get("OAUTH_ORG_CLIENT_SECRET")
        self.authorize_url = os.environ.get("OAUTH_ORG_AUTHORIZE_URL")
        self.token_url = os.environ.get("OAUTH_ORG_TOKEN_URL")
        self.userinfo_url = os.environ.get("OAUTH_ORG_USERINFO_URL")
        
        self.authorize_params = {
            "response_type": "code",
            "scope": "openid profile email groups",
            "response_mode": "query",
        }

    async def get_token(self, code: str, url: str) -> str:
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

            # Try access_token first, then id_token
            token = response_json.get("access_token") or response_json.get("id_token")
            
            if not token:
                raise HTTPException(
                    status_code=400, detail="Failed to get the access token"
                )

            return token

    async def get_user_info(self, token: str):
        headers = {"Authorization": f"Bearer {token}"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(self.userinfo_url, headers=headers)
            response.raise_for_status()
            user_info = response.json()
            
            print("Printing user info: \n", json.dumps(user_info, indent=2))
            
            # Check if user has required group
            user_groups = user_info.get('groups', [])
            required_group = 'us\\us.employees'
            
            if required_group not in user_groups:
                print(f"Access denied. User does not have required group: {required_group}")
                print(f"User groups: {user_groups}")
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
            
            print(f"Access granted for user: {user_name} ({user_email})")
            return user_info, user 