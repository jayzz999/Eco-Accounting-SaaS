# AWS Cognito Setup Guide

This guide explains how to set up AWS Cognito for user authentication in the Eco-Accounting SaaS platform.

## Prerequisites

- AWS Account with access to AWS Cognito
- AWS CLI configured (optional but recommended)

## Step 1: Create Cognito User Pool

1. Navigate to **AWS Cognito** in the AWS Console
2. Click **"Create user pool"**

### Step 1.1: Configure Sign-in Experience

- **Sign-in options**: Select **Email**
- **User name requirements**: Leave defaults
- Click **Next**

### Step 1.2: Configure Security Requirements

- **Password policy**: Choose **Cognito defaults** or customize:
  - Minimum length: 8 characters
  - Require uppercase, lowercase, numbers, special characters
- **Multi-factor authentication (MFA)**: Optional (recommended for production)
  - Select "Optional MFA" or "No MFA" for development
- **User account recovery**: Select **Email only**
- Click **Next**

### Step 1.3: Configure Sign-up Experience

- **Self-registration**: Enable "Allow users to sign themselves up"
- **Attribute verification**: Check **Send email message, verify email address**
- **Required attributes**: Select:
  - name
  - email (automatically included)
- **Custom attributes**: None needed for now
- Click **Next**

### Step 1.4: Configure Message Delivery

- **Email provider**: Choose one:
  - **Send email with Cognito** (Easiest for testing, limited to 50 emails/day)
  - **Send email with Amazon SES** (For production, unlimited emails)
- **FROM email address**: Use default or configure custom
- **Reply-to email address**: Optional
- Click **Next**

### Step 1.5: Integrate Your App

- **User pool name**: `eco-accounting-users` (or your preferred name)
- **Hosted authentication pages**: Not needed (we're using custom frontend)
- **Domain**: Skip for now (optional)

#### App Client Settings:

- **App client name**: `eco-accounting-app`
- **Client secret**: Generate (we'll use this)
- **Authentication flows**:
  - ✅ **ALLOW_USER_PASSWORD_AUTH** (Required)
  - ✅ **ALLOW_REFRESH_TOKEN_AUTH** (Required)
  - ✅ **ALLOW_ADMIN_USER_PASSWORD_AUTH** (Optional)
- **Token expiration**:
  - Access token: 1 hour
  - ID token: 1 hour
  - Refresh token: 30 days
- Click **Next**

### Step 1.6: Review and Create

- Review all settings
- Click **"Create user pool"**

## Step 2: Get Configuration Values

After creating the user pool:

1. **User Pool ID**:
   - Go to your user pool
   - Copy the **User Pool ID** (format: `us-east-1_XXXXXXXXX`)

2. **App Client ID**:
   - Navigate to **"App integration"** tab
   - Under **"App clients and analytics"**, click your app client
   - Copy the **Client ID**

3. **App Client Secret**:
   - In the same app client page
   - Click **"Show client secret"**
   - Copy the **Client secret**

## Step 3: Update Backend Configuration

Add the following to your `.env` file:

```env
# AWS Cognito Configuration
COGNITO_USER_POOL_ID=us-east-1_XXXXXXXXX
COGNITO_CLIENT_ID=your-client-id-here
COGNITO_CLIENT_SECRET=your-client-secret-here
```

## Step 4: Enable USER_PASSWORD_AUTH Flow

By default, Cognito may not allow `USER_PASSWORD_AUTH` flow. To enable it:

### Option A: Via AWS Console

1. Go to your User Pool
2. Click **"App integration"** tab
3. Under **"App clients and analytics"**, select your app client
4. Click **"Edit"**
5. Scroll to **"Authentication flows"**
6. Check **"ALLOW_USER_PASSWORD_AUTH"**
7. Check **"ALLOW_REFRESH_TOKEN_AUTH"**
8. Click **"Save changes"**

### Option B: Via AWS CLI

```bash
aws cognito-idp update-user-pool-client \
    --user-pool-id us-east-1_XXXXXXXXX \
    --client-id your-client-id \
    --explicit-auth-flows ALLOW_USER_PASSWORD_AUTH ALLOW_REFRESH_TOKEN_AUTH
```

## Step 5: Install Required Python Package

```bash
cd backend
source venv/bin/activate
pip install PyJWT==2.8.0
```

## Step 6: Test Authentication

### 6.1 Start the Backend Server

```bash
cd backend
source venv/bin/activate
python main.py
```

### 6.2 Test Sign Up

```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!@#",
    "full_name": "Test User"
  }'
```

Expected response:
```json
{
  "user_sub": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "user_confirmed": false,
  "message": "User registered successfully. Please check your email for verification code."
}
```

### 6.3 Check Email and Confirm Sign Up

Check the email inbox for verification code, then:

```bash
curl -X POST http://localhost:8000/api/auth/confirm-signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "confirmation_code": "123456"
  }'
```

### 6.4 Test Sign In

```bash
curl -X POST http://localhost:8000/api/auth/signin \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!@#"
  }'
```

Expected response:
```json
{
  "access_token": "eyJraWQiOiI...",
  "id_token": "eyJraWQiOiI...",
  "refresh_token": "eyJjdHkiOiJ...",
  "expires_in": 3600,
  "token_type": "Bearer"
}
```

### 6.5 Test Protected Endpoint

```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

## API Endpoints

### Authentication Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/signup` | POST | Register new user |
| `/api/auth/confirm-signup` | POST | Confirm email with verification code |
| `/api/auth/signin` | POST | Sign in and get tokens |
| `/api/auth/refresh` | POST | Refresh access token |
| `/api/auth/me` | GET | Get current user info (protected) |
| `/api/auth/signout` | POST | Sign out user (protected) |
| `/api/auth/forgot-password` | POST | Request password reset |
| `/api/auth/confirm-forgot-password` | POST | Reset password with code |

## Security Notes

### For Development:

- ✅ Email verification is required
- ⚠️ JWT signature verification is **disabled** (set in `services/auth.py`)
- ⚠️ Using Cognito's default email (limited to 50/day)

### For Production:

1. **Enable JWT Signature Verification**:
   - Update `services/auth.py` in the `verify_token` method
   - Fetch JWKS keys from Cognito and cache them
   - Use proper signature verification

2. **Use Amazon SES for Emails**:
   - Configure SES in Cognito settings
   - Verify your domain
   - Set up DKIM and SPF records

3. **Enable MFA**:
   - Go to User Pool settings
   - Enable MFA (TOTP or SMS)

4. **Set Up Custom Domain** (Optional):
   - Configure a custom domain for Cognito hosted UI
   - Use your own domain instead of AWS default

5. **API Gateway Integration**:
   - Use Cognito authorizers in API Gateway
   - Enable request/response validation

## Troubleshooting

### Issue: "NotAuthorizedException: Incorrect username or password"

- Check that USER_PASSWORD_AUTH flow is enabled
- Verify the app client settings

### Issue: "UserNotConfirmedException"

- User needs to confirm email first
- Resend confirmation code if needed

### Issue: "InvalidPasswordException"

- Password must meet requirements (8+ chars, uppercase, lowercase, numbers, special chars)

### Issue: "UsernameExistsException"

- Email already registered
- Use forgot password flow or different email

## Next Steps

1. ✅ Cognito is now configured
2. Integrate authentication in frontend (Next.js)
3. Add protected routes
4. Link user_id from Cognito to organization_id in database
5. Implement role-based access control (RBAC)

## Resources

- [AWS Cognito Documentation](https://docs.aws.amazon.com/cognito/)
- [Cognito User Pool Auth Flow](https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-authentication-flow.html)
- [JWT Token Verification](https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-tokens-verifying-a-jwt.html)
