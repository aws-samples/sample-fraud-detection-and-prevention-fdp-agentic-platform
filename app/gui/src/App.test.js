// Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import { render, screen, waitFor } from '@testing-library/react';
import App from './App';
import { AuthProvider } from "react-oidc-context";

// Mock the AuthProvider context
jest.mock("react-oidc-context", () => ({
  AuthProvider: ({ children }) => children,
  useAuth: () => ({
    isLoading: false,
    isAuthenticated: true,
    error: null,
    user: {
      profile: {
        email: 'test@example.com',
      },
      access_token: 'test-token',
    },
    removeUser: jest.fn(),
  }),
}));

// Mock the lazy-loaded components
jest.mock('./components/GuestUser', () => ({
  __esModule: true,
  default: () => <div data-testid="not-logged-in">Not Logged In Component</div>,
}));

jest.mock('./components/DocumentAnalyzer', () => ({
  __esModule: true,
  default: () => <div data-testid="document-analyzer">Document Analyzer Component</div>,
}));

jest.mock('./components/PromptManager', () => ({
  __esModule: true,
  default: () => <div data-testid="prompt-manager">Prompt Manager Component</div>,
}));

jest.mock('./components/ConfigurationManager', () => ({
  __esModule: true,
  default: () => <div data-testid="config-manager">Configuration Manager Component</div>,
}));

describe('App', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('shows loading state when auth is loading', () => {
    jest.spyOn(require("react-oidc-context"), "useAuth").mockImplementation(() => ({
      isLoading: true,
      isAuthenticated: false,
      error: null,
    }));

    render(<App />);
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('shows error state when auth fails', () => {
    jest.spyOn(require("react-oidc-context"), "useAuth").mockImplementation(() => ({
      isLoading: false,
      isAuthenticated: false,
      error: new Error('Auth failed'),
      signinRedirect: jest.fn(),
    }));

    render(<App />);
    expect(screen.getByText('Authentication Error')).toBeInTheDocument();
    expect(screen.getByText('Auth failed')).toBeInTheDocument();
  });

  it('shows GuestUser component when user is not authenticated', () => {
    jest.spyOn(require("react-oidc-context"), "useAuth").mockImplementation(() => ({
      isLoading: false,
      isAuthenticated: false,
      error: null,
    }));

    render(<App />);
    expect(screen.getByTestId('not-logged-in')).toBeInTheDocument();
  });

  it('shows main application when user is authenticated', () => {
    jest.spyOn(require("react-oidc-context"), "useAuth").mockImplementation(() => ({
      isLoading: false,
      isAuthenticated: true,
      error: null,
      user: {
        profile: {
          email: 'test@example.com',
        },
        access_token: 'test-token',
      },
      removeUser: jest.fn(),
    }));

    render(<App />);
    expect(screen.getByTestId('document-analyzer')).toBeInTheDocument();
  });
});