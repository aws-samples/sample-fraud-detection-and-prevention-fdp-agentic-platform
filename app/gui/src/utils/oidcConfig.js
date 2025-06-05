// Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

export const oidcConfig = {
  authority: process.env.REACT_APP_IDP_URL,
  client_id: process.env.REACT_APP_USER_CLIENT_ID,
  redirect_uri: process.env.REACT_APP_REDIRECT_SIGNIN,
  post_logout_redirect_uri: process.env.REACT_APP_REDIRECT_SIGNOUT,
  response_type: 'code',
  scope: 'aws.cognito.signin.user.admin openid email profile fdp/read fdp/write',
  automaticSilentRenew: true,
  loadUserInfo: true,
  revokeTokensOnSignout: true,
  extraTokenParameters: {
    client_id: process.env.REACT_APP_USER_CLIENT_ID
  },
};

export const getLoginUrl = () => {
  const cognitoDomain = process.env.REACT_APP_AUTH_URL;
  const clientId = process.env.REACT_APP_USER_CLIENT_ID;
  const redirectUri = encodeURIComponent(process.env.REACT_APP_REDIRECT_SIGNIN);
  
  return `${cognitoDomain}/login?client_id=${clientId}&response_type=code&scope=openid+email+profile+fdp/read+fdp/write&redirect_uri=${redirectUri}`;
};

export const getSignUpUrl = () => {
  const cognitoDomain = process.env.REACT_APP_AUTH_URL;
  const clientId = process.env.REACT_APP_USER_CLIENT_ID;
  const redirectUri = encodeURIComponent(process.env.REACT_APP_REDIRECT_SIGNIN);
  
  return `${cognitoDomain}/signup?client_id=${clientId}&response_type=code&scope=openid+email+profile+fdp/read+fdp/write&redirect_uri=${redirectUri}`;
};

export const getForgotPasswordUrl = () => {
  const cognitoDomain = process.env.REACT_APP_AUTH_URL;
  const clientId = process.env.REACT_APP_USER_CLIENT_ID;
  const redirectUri = encodeURIComponent(process.env.REACT_APP_REDIRECT_SIGNIN);
  
  return `${cognitoDomain}/forgotpassword?client_id=${clientId}&response_type=code&scope=openid+email+profile+fdp/read+fdp/write&redirect_uri=${redirectUri}`;
};
