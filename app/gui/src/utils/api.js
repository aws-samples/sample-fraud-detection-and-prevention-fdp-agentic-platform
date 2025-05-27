// Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import { getAuthToken } from './auth';
import { get, post, put, del } from 'aws-amplify/api';

// API wrapper functions with optional token parameter
export const apiGet = async (path, token = '', options = {}, apiName = 'secureApi') => {
  try {
    // Use provided token or fetch if not provided
    const authToken = token || await getAuthToken();

    const response = await get({
      apiName,
      path,
      options: {
        ...options,
        headers: {
          ...options.headers,
          // Authorization: authToken
          Authorization: `Bearer ${authToken}`
        },
        retryStrategy: {
          strategy: 'no-retry'
        }
      }
    });

    // Handle the case where response might not have body
    if (!response || !response.body) {
      console.error('Response or body is undefined');
    }

    return response.body;
  } catch (error) {
    console.error(`Error in GET request to ${path}:`, error);
    throw error;
  }
};

export const apiPost = async (path, token = '', options = {}, apiName = 'secureApi') => {
  try {
    // Use provided token or fetch if not provided
    const authToken = token || await getAuthToken();

    const response = await post({
      apiName,
      path,
      options: {
        ...options,
        headers: {
          ...options.headers,
          Authorization: `Bearer ${authToken}`
        },
        retryStrategy: {
          strategy: 'no-retry'
        }
      }
    });

    // Handle the case where response might not have body
    if (!response || !response.body) {
      console.error('Response or body is undefined');
    }

    return response.body;
  } catch (error) {
    console.error(`Error in POST request to ${path}:`, error);
    throw error;
  }
};

export const apiPut = async (path, token = '', options = {}, apiName = 'secureApi') => {
  try {
    // Use provided token or fetch if not provided
    const authToken = token || await getAuthToken();

    const response = await put({
      apiName,
      path,
      options: {
        ...options,
        headers: {
          ...options.headers,
          Authorization: `Bearer ${authToken}`
        },
        retryStrategy: {
          strategy: 'no-retry'
        }
      }
    });

    // Handle the case where response might not have body
    if (!response || !response.body) {
      console.error('Response or body is undefined');
    }

    return response.body;
  } catch (error) {
    console.error(`Error in PUT request to ${path}:`, error);
    throw error;
  }
};

export const apiDelete = async (path, token = '', options = {}, apiName = 'secureApi') => {
  try {
    // Use provided token or fetch if not provided
    const authToken = token || await getAuthToken();

    const response = await del({
      apiName,
      path,
      options: {
        ...options,
        headers: {
          ...options.headers,
          Authorization: `Bearer ${authToken}`
        },
        retryStrategy: {
          strategy: 'no-retry'
        }
      }
    });

    // Handle the case where response might not have body
    if (!response || !response.body) {
      console.error('Response or body is undefined');
    }

    return response.body;
  } catch (error) {
    console.error(`Error in DELETE request to ${path}:`, error);
    throw error;
  }
};
