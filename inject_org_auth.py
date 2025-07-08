import os
from chainlit.oauth_providers import providers
from org_oauth_provider import OrgOAuthProvider


def org_oauth_enabled():
    """Check if all required OAuth environment variables are set"""
    required_vars = [
        "OAUTH_ORG_CLIENT_ID",
        "OAUTH_ORG_CLIENT_SECRET", 
        "OAUTH_ORG_AUTHORIZE_URL",
        "OAUTH_ORG_TOKEN_URL",
        "OAUTH_ORG_USERINFO_URL"
    ]
    
    for var in required_vars:
        if not os.environ.get(var):
            print(f"Missing required environment variable: {var}")
            return False
    
    print("Organization OAuth configured.")
    return True


def provider_id_in_instance_list(provider_id: str):
    """Check if provider is already registered"""
    if providers is None:
        print("No providers found")
        return False
    if not any(provider.id == provider_id for provider in providers):
        print(f"Provider {provider_id} not found")
        return False
    else:
        print(f"Provider {provider_id} found")
        return True


def add_org_oauth_provider():
    """Add the organization's OAuth provider to Chainlit"""
    provider_id = "org-openid"
    
    if org_oauth_enabled() and not provider_id_in_instance_list(provider_id):
        org_provider = OrgOAuthProvider()
        providers.append(org_provider)
        print(f"Added provider: {provider_id}")
        return True
    else:
        print(f"Organization OAuth is not enabled or provider {provider_id} already exists")
        return False 