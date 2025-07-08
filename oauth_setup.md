# Organization OAuth/OpenID Setup Guide

## Required Environment Variables

Add these environment variables to your `.env` file:

```bash
# Required for Chainlit authentication
CHAINLIT_AUTH_SECRET=your_generated_secret

# Custom Organization OAuth Provider
OAUTH_ORG_CLIENT_ID=your_client_id
OAUTH_ORG_CLIENT_SECRET=your_client_secret
OAUTH_ORG_AUTHORIZE_URL=https://your-org.com/oauth/authorize
OAUTH_ORG_TOKEN_URL=https://your-org.com/oauth/token
OAUTH_ORG_USERINFO_URL=https://your-org.com/userinfo

# Your existing LLM configuration
LLM_API_KEY=your_llm_api_key
LLM_MODEL=your_preferred_model
```

## OpenID Connect Response Format

The system expects user info in this format:
```json
{
  "sub": "e23432@x3343.com",
  "employee_id": "99999", 
  "name": "Karl D Lone",
  "groups": ["us\\all.employees", "us\\us.employees"],
  "email": "karl.lone@company.com"
}
```

## How It Works

This implementation follows the Chainlit cookbook pattern for custom OAuth providers:

1. **Custom Provider Class**: `OrgOAuthProvider` extends Chainlit's `OAuthProvider` base class
2. **Runtime Injection**: The provider is added to Chainlit's `providers` list at startup
3. **Group Validation**: Access control happens in the provider's `get_user_info()` method
4. **Personalized Sessions**: Creates user objects with organization metadata

## Implementation Files

- `org_oauth_provider.py` - Custom OAuth provider class
- `inject_org_auth.py` - Injects provider into Chainlit's providers list
- `main.py` - Imports and executes the injection at startup

## Access Control

- Users must be members of the `us\us.employees` group to access the application
- Users without this group will receive a 403 Forbidden error
- The app displays "Welcome, {name}!" for authenticated users

## OAuth Flow

1. User visits the application
2. If not authenticated, they're redirected to your organization's OAuth provider
3. After successful authentication, the app validates group membership
4. If authorized, user sees personalized welcome message
5. Unauthorized users are denied access

## Testing

To test the OAuth integration:

1. Set up the environment variables in your `.env` file
2. Configure your OAuth provider to redirect to: `http://localhost:8000/auth/callback`
3. Install dependencies: `pip install -r requirements.txt`
4. Start the application: `chainlit run main.py`
5. You should see console output confirming the provider was added
6. Visit the app - you should be redirected to your organization's login
7. After successful login with group membership, you'll see the personalized welcome

## Troubleshooting

- Check the console logs for OAuth debugging information
- Ensure your OAuth provider supports the OpenID Connect scopes: `openid profile email groups`
- Verify the redirect URI matches your OAuth provider configuration
- Make sure the `groups` claim includes the required group name 