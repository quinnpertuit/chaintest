# Organization OAuth/OpenID Setup Guide

## Required Environment Variables

Add these environment variables to your `.env` file:

```bash
# OAuth Configuration
OAUTH_ORG_CLIENT_ID=your_client_id
OAUTH_ORG_CLIENT_SECRET=your_client_secret
OAUTH_ORG_AUTHORIZE_URL=https://your-org.com/oauth/authorize
OAUTH_ORG_TOKEN_URL=https://your-org.com/oauth/token
OAUTH_ORG_USERINFO_URL=https://your-org.com/userinfo

# Optional (for JWT validation)
OAUTH_ORG_JWKS_URL=https://your-org.com/.well-known/jwks.json
OAUTH_ORG_ISSUER=https://your-org.com

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
3. Start the application: `chainlit run main.py`
4. Visit the app - you should be redirected to login
5. After login, you should see the personalized welcome message

## Troubleshooting

- Check the console logs for OAuth debugging information
- Ensure your OAuth provider supports the OpenID Connect scopes: `openid profile email groups`
- Verify the redirect URI matches your OAuth provider configuration
- Make sure the `groups` claim includes the required group name 