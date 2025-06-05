// Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import { render, screen, fireEvent } from '@testing-library/react';
import GuestUser from '../GuestUser';
import { getSignUpUrl, getForgotPasswordUrl } from '../../utils/oidcConfig';

// Mock the oidcConfig functions
jest.mock('../../utils/oidcConfig', () => ({
  getSignUpUrl: jest.fn(),
  getForgotPasswordUrl: jest.fn(),
}));

// Mock react-oidc-context
jest.mock('react-oidc-context', () => ({
  useAuth: () => ({
    signinRedirect: jest.fn(),
    isLoading: false,
    error: null,
  }),
}));

// Mock window.location
const mockLocation = {
  href: '',
};
Object.defineProperty(window, 'location', {
  value: mockLocation,
  writable: true,
});

describe('GuestUser', () => {
  let mockSigninRedirect;

  beforeEach(() => {
    // Reset all mocks before each test
    jest.clearAllMocks();
    window.location.href = '';

    // Set up default mock return values
    getSignUpUrl.mockReturnValue('https://test-domain/signup');
    getForgotPasswordUrl.mockReturnValue('https://test-domain/forgot');

    // Set up mock for signinRedirect
    mockSigninRedirect = jest.fn();
    jest.spyOn(require('react-oidc-context'), 'useAuth').mockImplementation(() => ({
      signinRedirect: mockSigninRedirect,
      isLoading: false,
      error: null,
    }));
  });

  it('renders welcome message', () => {
    render(<GuestUser />);
    expect(screen.getByText('FDP Agentic Platform')).toBeInTheDocument();
  });

  it('renders sign in button', () => {
    render(<GuestUser />);
    expect(screen.getByText('Sign In')).toBeInTheDocument();
  });

  it('renders create account button', () => {
    render(<GuestUser />);
    expect(screen.getByText('Create Account')).toBeInTheDocument();
  });

  it('renders forgot password button', () => {
    render(<GuestUser />);
    expect(screen.getByText('Forgot Password?')).toBeInTheDocument();
  });

  it('calls signinRedirect when sign in button is clicked', () => {
    render(<GuestUser />);
    fireEvent.click(screen.getByText('Sign In'));
    expect(mockSigninRedirect).toHaveBeenCalled();
  });

  it('redirects to signup URL when create account button is clicked', () => {
    render(<GuestUser />);
    fireEvent.click(screen.getByText('Create Account'));
    expect(window.location.href).toBe('https://test-domain/signup');
  });

  it('redirects to forgot password URL when forgot password button is clicked', () => {
    render(<GuestUser />);
    fireEvent.click(screen.getByText('Forgot Password?'));
    expect(window.location.href).toBe('https://test-domain/forgot');
  });

  it('shows loading state when auth is loading', () => {
    jest.spyOn(require('react-oidc-context'), 'useAuth').mockImplementation(() => ({
      signinRedirect: mockSigninRedirect,
      isLoading: true,
      error: null,
    }));

    render(<GuestUser />);
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('shows error state when auth fails', () => {
    jest.spyOn(require('react-oidc-context'), 'useAuth').mockImplementation(() => ({
      signinRedirect: mockSigninRedirect,
      isLoading: false,
      error: new Error('Auth failed'),
    }));

    render(<GuestUser />);
    expect(screen.getByText('Authentication Error')).toBeInTheDocument();
    expect(screen.getByText('Auth failed')).toBeInTheDocument();
  });
});
