"""
Authentication service using AWS Cognito
"""

import os
import boto3
import jwt
from typing import Optional, Dict
from datetime import datetime, timedelta
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from botocore.exceptions import ClientError


class CognitoAuth:
    def __init__(self):
        self.region = os.getenv('AWS_REGION', 'us-east-1')
        self.user_pool_id = os.getenv('COGNITO_USER_POOL_ID')
        self.client_id = os.getenv('COGNITO_CLIENT_ID')
        self.client_secret = os.getenv('COGNITO_CLIENT_SECRET')

        # Initialize Cognito client
        self.cognito_client = boto3.client('cognito-idp', region_name=self.region)

        # JWT verification keys
        self.jwks_url = f"https://cognito-idp.{self.region}.amazonaws.com/{self.user_pool_id}/.well-known/jwks.json"

    def sign_up(self, email: str, password: str, full_name: str) -> Dict:
        """
        Register a new user in Cognito
        """
        try:
            response = self.cognito_client.sign_up(
                ClientId=self.client_id,
                Username=email,
                Password=password,
                UserAttributes=[
                    {'Name': 'email', 'Value': email},
                    {'Name': 'name', 'Value': full_name}
                ]
            )

            return {
                'user_sub': response['UserSub'],
                'user_confirmed': response.get('UserConfirmed', False),
                'message': 'User registered successfully. Please check your email for verification code.'
            }
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'UsernameExistsException':
                raise HTTPException(status_code=400, detail="User already exists")
            elif error_code == 'InvalidPasswordException':
                raise HTTPException(status_code=400, detail="Password does not meet requirements")
            else:
                raise HTTPException(status_code=400, detail=str(e))

    def confirm_sign_up(self, email: str, confirmation_code: str) -> Dict:
        """
        Confirm user registration with verification code
        """
        try:
            self.cognito_client.confirm_sign_up(
                ClientId=self.client_id,
                Username=email,
                ConfirmationCode=confirmation_code
            )

            return {'message': 'Email confirmed successfully'}
        except ClientError as e:
            raise HTTPException(status_code=400, detail=str(e))

    def sign_in(self, email: str, password: str) -> Dict:
        """
        Sign in a user and get JWT tokens
        """
        try:
            # Initiate authentication
            response = self.cognito_client.initiate_auth(
                ClientId=self.client_id,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': email,
                    'PASSWORD': password
                }
            )

            return {
                'access_token': response['AuthenticationResult']['AccessToken'],
                'id_token': response['AuthenticationResult']['IdToken'],
                'refresh_token': response['AuthenticationResult']['RefreshToken'],
                'expires_in': response['AuthenticationResult']['ExpiresIn'],
                'token_type': response['AuthenticationResult']['TokenType']
            }
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NotAuthorizedException':
                raise HTTPException(status_code=401, detail="Invalid email or password")
            elif error_code == 'UserNotConfirmedException':
                raise HTTPException(status_code=403, detail="Email not confirmed. Please verify your email.")
            else:
                raise HTTPException(status_code=400, detail=str(e))

    def refresh_token(self, refresh_token: str) -> Dict:
        """
        Refresh access token using refresh token
        """
        try:
            response = self.cognito_client.initiate_auth(
                ClientId=self.client_id,
                AuthFlow='REFRESH_TOKEN_AUTH',
                AuthParameters={
                    'REFRESH_TOKEN': refresh_token
                }
            )

            return {
                'access_token': response['AuthenticationResult']['AccessToken'],
                'id_token': response['AuthenticationResult']['IdToken'],
                'expires_in': response['AuthenticationResult']['ExpiresIn'],
                'token_type': response['AuthenticationResult']['TokenType']
            }
        except ClientError as e:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

    def verify_token(self, token: str) -> Dict:
        """
        Verify and decode JWT token
        """
        try:
            # Decode without verification first to get header
            unverified_headers = jwt.get_unverified_header(token)

            # In production, fetch and cache JWKS keys from Cognito
            # For now, decode without verification (NOT PRODUCTION READY)
            decoded = jwt.decode(
                token,
                options={"verify_signature": False}  # TODO: Add proper verification in production
            )

            # Verify token expiration
            if decoded.get('exp', 0) < datetime.now().timestamp():
                raise HTTPException(status_code=401, detail="Token has expired")

            return decoded
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=401, detail="Invalid token")

    def get_user_info(self, access_token: str) -> Dict:
        """
        Get user information from Cognito
        """
        try:
            response = self.cognito_client.get_user(
                AccessToken=access_token
            )

            user_attributes = {attr['Name']: attr['Value'] for attr in response['UserAttributes']}

            return {
                'username': response['Username'],
                'email': user_attributes.get('email'),
                'name': user_attributes.get('name'),
                'email_verified': user_attributes.get('email_verified') == 'true',
                'sub': user_attributes.get('sub')
            }
        except ClientError as e:
            raise HTTPException(status_code=401, detail="Invalid access token")

    def sign_out(self, access_token: str) -> Dict:
        """
        Sign out user (invalidate token)
        """
        try:
            self.cognito_client.global_sign_out(
                AccessToken=access_token
            )

            return {'message': 'User signed out successfully'}
        except ClientError as e:
            raise HTTPException(status_code=400, detail=str(e))

    def forgot_password(self, email: str) -> Dict:
        """
        Initiate forgot password flow
        """
        try:
            self.cognito_client.forgot_password(
                ClientId=self.client_id,
                Username=email
            )

            return {'message': 'Password reset code sent to your email'}
        except ClientError as e:
            raise HTTPException(status_code=400, detail=str(e))

    def confirm_forgot_password(self, email: str, confirmation_code: str, new_password: str) -> Dict:
        """
        Confirm forgot password with code and set new password
        """
        try:
            self.cognito_client.confirm_forgot_password(
                ClientId=self.client_id,
                Username=email,
                ConfirmationCode=confirmation_code,
                Password=new_password
            )

            return {'message': 'Password reset successfully'}
        except ClientError as e:
            raise HTTPException(status_code=400, detail=str(e))


# Security dependency
security = HTTPBearer()

# Global auth instance
cognito_auth = None


def get_cognito_auth() -> CognitoAuth:
    """Get or create CognitoAuth instance"""
    global cognito_auth
    if cognito_auth is None:
        cognito_auth = CognitoAuth()
    return cognito_auth


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    auth: CognitoAuth = Depends(get_cognito_auth)
) -> Dict:
    """
    Dependency to get current authenticated user from JWT token
    """
    token = credentials.credentials

    # Verify and decode token
    decoded_token = auth.verify_token(token)

    # Get user info
    user_info = auth.get_user_info(token)

    return {
        'user_id': user_info['sub'],
        'email': user_info['email'],
        'name': user_info['name'],
        'token_claims': decoded_token
    }


async def get_current_user_optional(
    auth: CognitoAuth = Depends(get_cognito_auth),
    credentials: Optional[HTTPAuthorizationCredentials] = None
) -> Optional[Dict]:
    """
    Optional authentication - returns None if no token provided
    """
    if credentials is None:
        return None

    token = credentials.credentials
    decoded_token = auth.verify_token(token)
    user_info = auth.get_user_info(token)

    return {
        'user_id': user_info['sub'],
        'email': user_info['email'],
        'name': user_info['name'],
        'token_claims': decoded_token
    }
