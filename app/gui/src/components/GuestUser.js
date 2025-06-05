// Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import {
  Box,
  Button,
  Typography,
  Paper,
  Container,
  CircularProgress,
} from '@mui/material';
import { useAuth } from "react-oidc-context";
import { getSignUpUrl, getForgotPasswordUrl } from '../utils/oidcConfig';

const GuestUser = () => {
  const auth = useAuth();

  const handleLogin = () => {
    auth.signinRedirect();
  };

  const handleSignUp = () => {
    window.location.href = getSignUpUrl();
  };

  const handleForgotPassword = () => {
    window.location.href = getForgotPasswordUrl();
  };

  if (auth.isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (auth.error) {
    return (
      <Container maxWidth="sm">
        <Box sx={{ marginTop: 8, textAlign: 'center' }}>
          <Typography color="error" gutterBottom>
            Authentication Error
          </Typography>
          <Typography color="textSecondary">
            {auth.error.message}
          </Typography>
          <Button
            variant="contained"
            onClick={() => auth.signinRedirect()}
            sx={{ mt: 2 }}
          >
            Try Again
          </Button>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="sm">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Paper
          elevation={3}
          sx={{
            p: 4,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            width: '100%',
          }}
        >
          <Typography component="h1" variant="h5" gutterBottom>
            FDP Agentic Platform
          </Typography>
          <Typography variant="body1" color="text.secondary" align="center" sx={{ mb: 3 }}>
            Please sign in to access the Fraud Detection and Prevention (FDP) Agentic Platform capabilities and features
          </Typography>
          <Box sx={{ mt: 1, width: '100%' }}>
            <Button
              fullWidth
              variant="contained"
              onClick={handleLogin}
              sx={{ mb: 2 }}
            >
              Sign In
            </Button>
            <Button
              fullWidth
              variant="outlined"
              onClick={handleSignUp}
              sx={{ mb: 2 }}
            >
              Create Account
            </Button>
            <Button
              fullWidth
              color="inherit"
              onClick={handleForgotPassword}
            >
              Forgot Password?
            </Button>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default GuestUser;
