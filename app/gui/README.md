# React Application

This React application provides document analysis capabilities with AWS Cognito
authentication, including document scanning, prompt management, and system
configuration features.

## Features

- Document analysis and scanning
- Prompt management system
- System configuration interface
- User authentication with AWS Cognito
- Protected routes for authenticated users
- Responsive design with Material-UI

## Prerequisites

1. Node.js and npm installed
2. AWS account with Cognito User Pool set up
3. AWS Cognito User Pool and App Client credentials
4. AWS API Gateway endpoint configured

## Setup

1. Install dependencies:

   ```sh
   npm install
   ```

2. Configure environment variables:

   Create a `.env` file with the following variables:

   ```sh
   REACT_APP_AWS_REGION=YOUR_REGION
   REACT_APP_IDENTITY_POOL_ID=YOUR_IDENTITY_POOL_ID
   REACT_APP_USER_CLIENT_ID=YOUR_APP_CLIENT_ID
   REACT_APP_USER_POOL_ID=YOUR_USER_POOL_ID
   REACT_APP_IDP_URL=YOUR_COGNITO_IDP_URL
   REACT_APP_AUTH_URL=YOUR_COGNITO_AUTH_URL
   REACT_APP_API_URL=YOUR_API_GATEWAY_URL
   REACT_APP_REDIRECT_SIGNIN=YOUR_SIGNIN_URL
   REACT_APP_REDIRECT_SIGNOUT=YOUR_SIGNOUT_URL
   ```

3. Start the development server:

   ```sh
   npm start
   ```

## Project Structure

```sh
src/
├── components/
│   ├── ConfigurationManager.js
│   ├── DocumentAnalyzer.js
│   ├── GuestUser.js
│   ├── ProcessingAnimation.js
│   └── PromptManager.js
├── App.css
├── App.js
├── index.css
└── index.js
```

## Available Scripts

- `npm start`: Run development server
- `npm test`: Run tests
- `npm run build`: Build for production
- `npm run analyze`: Analyze bundle size

## Security Considerations

- Always use HTTPS in production
- Implement proper error handling
- Follow AWS security best practices
- Keep AWS credentials secure

## License

MIT
