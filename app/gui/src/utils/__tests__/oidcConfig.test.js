// Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import { oidcConfig } from '../oidcConfig';

describe('OIDC Configuration', () => {
  const OLD_ENV = process.env;

  beforeEach(() => {
    jest.resetModules();
    process.env = { ...OLD_ENV };
    process.env.REACT_APP_IDP_URL = 'https://cognito-idp.region.amazonaws.com/userPoolId';
    process.env.REACT_APP_AUTH_URL = 'https://auth.domain.com';
    process.env.REACT_APP_USER_CLIENT_ID = 'test-client-id';
    process.env.REACT_APP_REDIRECT_SIGNIN = 'https://app.domain.com';
    process.env.REACT_APP_REDIRECT_SIGNOUT = 'https://app.domain.com/signout';
  });

  afterEach(() => {
    process.env = OLD_ENV;
  });

  test('should have all required OIDC configuration properties', () => {
    expect(oidcConfig).toHaveProperty('authority');
    expect(oidcConfig).toHaveProperty('client_id');
    expect(oidcConfig).toHaveProperty('redirect_uri');
    expect(oidcConfig).toHaveProperty('response_type');
    expect(oidcConfig).toHaveProperty('scope');
    expect(oidcConfig).toHaveProperty('metadata_url');
    expect(oidcConfig).toHaveProperty('authority_configuration');
  });

  test('should have correct authority configuration endpoints', () => {
    expect(oidcConfig.authority_configuration).toHaveProperty('authorization_endpoint');
    expect(oidcConfig.authority_configuration).toHaveProperty('token_endpoint');
    expect(oidcConfig.authority_configuration).toHaveProperty('userinfo_endpoint');
    expect(oidcConfig.authority_configuration).toHaveProperty('end_session_endpoint');
    
    expect(oidcConfig.authority_configuration.authorization_endpoint)
      .toBe('https://auth.domain.com/oauth2/authorize');
    expect(oidcConfig.authority_configuration.token_endpoint)
      .toBe('https://auth.domain.com/oauth2/token');
    expect(oidcConfig.authority_configuration.userinfo_endpoint)
      .toBe('https://cognito-idp.region.amazonaws.com/userPoolId/oauth2/userInfo');
    expect(oidcConfig.authority_configuration.end_session_endpoint)
      .toBe('https://auth.domain.com/logout');
  });

  test('should have correct metadata URL', () => {
    expect(oidcConfig.metadata_url)
      .toBe('https://cognito-idp.region.amazonaws.com/userPoolId/.well-known/openid-configuration');
  });

  test('should have correct OAuth scopes', () => {
    expect(oidcConfig.scope).toContain('openid');
    expect(oidcConfig.scope).toContain('email');
    expect(oidcConfig.scope).toContain('profile');
    expect(oidcConfig.scope).toContain('fdp/read');
    expect(oidcConfig.scope).toContain('fdp/write');
  });
});