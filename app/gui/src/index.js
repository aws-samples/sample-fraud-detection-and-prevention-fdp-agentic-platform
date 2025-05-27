// Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';

// Enable React.lazy in development mode
if (process.env.NODE_ENV === 'development') {
  React.Suspense = React.Suspense || function(props) {
    return props.children;
  };
}

const container = document.getElementById('root');
const root = createRoot(container);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
