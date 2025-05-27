// Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import { getCurrentUser, fetchAuthSession, signOut } from 'aws-amplify/auth';

// Check if user is authenticated
export const isAuthenticated = async () => {
  try {
    await getCurrentUser();
    return true;
  } catch (error) {
    return false;
  }
};

// Get current authenticated user
export const getUser = async () => {
  try {
    return await getCurrentUser();
  } catch (error) {
    console.error('Error getting current user:', error);
    return null;
  }
};

// Get JWT tokens
export const getAuthToken = async () => {
  try {
    const { accessToken } = (await fetchAuthSession()).tokens ?? {};
    return accessToken;
  } catch (error) {
    console.error('Error getting auth token:', error);
    throw error;
  }
};

// Sign out user
export const forceLogout = async () => {
  try {
    await signOut();
    return true;
  } catch (error) {
    console.error('Error signing out:', error);
    return false;
  }
};
