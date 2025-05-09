# React AWS Cognito Authentication App

This React application demonstrates authentication flow using AWS Cognito, including sign-in, sign-out, protected routes, and password reset functionality.

## Features

- User sign-in with AWS Cognito
- Protected routes for authenticated users
- Password reset flow
- Sign out functionality
- Responsive design

## Prerequisites

1. Node.js and npm installed
2. AWS account with Cognito User Pool set up
3. AWS Cognito User Pool and App Client credentials

## Setup

1. Install dependencies:

   ```sh
   npm install
   ```

2. Configure AWS Cognito:

   - Open `src/aws-exports.js`
   - Replace the following values with your AWS Cognito configuration:
     - YOUR_REGION
     - YOUR_USER_POOL_ID
     - YOUR_APP_CLIENT_ID
     - YOUR_COGNITO_DOMAIN

3. Start the development server:

   ```sh
   npm start
   ```

## AWS Cognito Setup

1. Create a User Pool in AWS Cognito
2. Create an App Client
3. Configure App Client settings:
   - Enable Cognito User Pool as an identity provider
   - Configure callback URLs (e.g., http://localhost:3000/)
   - Select OAuth 2.0 flows (Authorization code grant)
   - Select OAuth 2.0 scopes (email, openid, profile)

## Project Structure

```sh
src/
├── components/
│   ├── Dashboard.js
│   ├── ProtectedRoute.js
│   ├── ResetPassword.js
│   ├── SignIn.js
│   └── __tests__/
│       ├── Dashboard.test.js
│       ├── ProtectedRoute.test.js
│       ├── ResetPassword.test.js
│       └── SignIn.test.js
├── context/
│   └── AuthContext.js
├── aws-exports.js
└── App.js
```

## Available Scripts

- `npm start`: Run development server
- `npm test`: Run tests
- `npm run build`: Build for production

## Security Considerations

- Always use HTTPS in production
- Implement proper error handling
- Follow AWS security best practices
- Keep AWS credentials secure

## License

MIT

## Sources

- https://docs.amplify.aws/gen1/react/build-a-backend/auth/set-up-auth/
- https://docs.amplify.aws/gen1/react/build-a-backend/restapi/configure-rest-api/
- https://docs.amplify.aws/react/build-a-backend/auth/set-up-auth/
- https://docs.amplify.aws/react/build-a-backend/add-aws-services/rest-api/set-up-rest-api/
