// Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import { getAuthToken } from './auth';

// API wrapper functions with optional token parameter
export const apiGet = async (path, token = '', options = {}, apiName = 'secureApi') => {
  try {
    // Use provided token or fetch if not provided
    const authToken = token || await getAuthToken();

    console.log('Making GET request with fetch API to:', path);

    // Use fetch API directly
    const apiUrl = process.env.REACT_APP_API_URL || '';
    const fullUrl = `${apiUrl}${path}`;

    const response = await fetch(fullUrl, {
      method: 'GET',
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log('Fetch API response data:', data);
    return data;
  } catch (error) {
    console.error(`Error in GET request to ${path}:`, error);
    throw error;
  }
};

export const apiPost = async (path, token = '', options = {}, apiName = 'secureApi') => {
  try {
    // Use provided token or fetch if not provided
    const authToken = token || await getAuthToken();

    console.log('Making POST request with fetch API to:', path);

    // Use fetch API directly
    const apiUrl = process.env.REACT_APP_API_URL || '';
    const fullUrl = `${apiUrl}${path}`;

    const response = await fetch(fullUrl, {
      method: 'POST',
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(options.body || {})
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log('Fetch API response data:', data);
    return data;
  } catch (error) {
    console.error(`Error in POST request to ${path}:`, error);
    throw error;
  }
};

export const apiPut = async (path, token = '', options = {}, apiName = 'secureApi') => {
  try {
    // Use provided token or fetch if not provided
    const authToken = token || await getAuthToken();

    // Define apiUrl and fullUrl before using them
    const apiUrl = process.env.REACT_APP_API_URL || '';
    const fullUrl = `${apiUrl}${path}`;

    console.log('Making PUT request with fetch API to:', path);
    console.log('Full URL for request:', fullUrl);

    const response = await fetch(fullUrl, {
      method: 'PUT',
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(options.body || {})
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log('Fetch API response data:', data);
    return data;
  } catch (error) {
    console.error(`Error in PUT request to ${path}:`, error);
    throw error;
  }
};

export const apiDelete = async (path, token = '', options = {}, apiName = 'secureApi') => {
  try {
    // Use provided token or fetch if not provided
    const authToken = token || await getAuthToken();

    // Define apiUrl and fullUrl before using them
    const apiUrl = process.env.REACT_APP_API_URL || '';
    const fullUrl = `${apiUrl}${path}`;

    console.log('Making DELETE request with fetch API to:', path);
    console.log('Full URL for request:', fullUrl);

    const response = await fetch(fullUrl, {
      method: 'DELETE',
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    // Some DELETE endpoints might not return JSON
    try {
      const data = await response.json();
      console.log('Fetch API response data:', data);
      return data;
    } catch (jsonError) {
      // If the response is not JSON, return an empty object
      console.log('DELETE response is not JSON, returning empty object');
      return {};
    }
  } catch (error) {
    console.error(`Error in DELETE request to ${path}:`, error);
    throw error;
  }
};
