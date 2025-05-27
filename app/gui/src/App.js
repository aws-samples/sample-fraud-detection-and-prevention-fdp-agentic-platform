// Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import { useState, useEffect, lazy, Suspense } from 'react';
import { Amplify } from 'aws-amplify';
import { getAuthToken } from './utils/auth';
import { withAuthenticator } from '@aws-amplify/ui-react';
import '@aws-amplify/ui-react/styles.css';
import {
  Box,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Typography,
  CssBaseline,
  IconButton,
  useTheme,
  Divider,
  Tooltip,
  CircularProgress,
} from '@mui/material';
import DocumentScannerIcon from '@mui/icons-material/DocumentScanner';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import SettingsIcon from '@mui/icons-material/Settings';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import LogoutIcon from '@mui/icons-material/Logout';

// Lazy load components to reduce initial bundle size
const DocumentAnalyzer = lazy(() => import('./components/DocumentAnalyzer'));
const PromptManager = lazy(() => import('./components/PromptManager'));
const ConfigurationManager = lazy(() => import('./components/ConfigurationManager'));

const expandedWidth = 240;
const collapsedWidth = 65;

// Amplify Configuration
Amplify.configure({
  Auth: {
    Cognito: {
      region: process.env.REACT_APP_AWS_REGION,
      identityPoolId: process.env.REACT_APP_IDENTITY_POOL_ID,
      userPoolId: process.env.REACT_APP_USER_POOL_ID,
      userPoolClientId: process.env.REACT_APP_USER_CLIENT_ID,
      mfa: {
        status: "OFF",
        types: ["SMS"]
      },
      // oauth: {
      //   domain: process.env.REACT_APP_AUTH_URL,
      //   clientId: process.env.REACT_APP_USER_CLIENT_ID,
      //   scopes: [
      //     'aws.cognito.signin.user.admin', 'openid',
      //     'email', 'profile', 'fdp/read', 'fdp/write'
      //   ],
      //   // redirectSignIn: 'http://localhost:3000/',
      //   // redirectSignOut: 'http://localhost:3000/',
      //   // responseType: 'code'
      // },
      passwordFormat: {
        minLength: 8
      },
      signUpAttributes: ["EMAIL"],
      verificationMechanisms: ["EMAIL"]
    }
  },
  API: {
    REST: {
      secureApi: {
        endpoint: process.env.REACT_APP_API_URL,
        region: process.env.REACT_APP_AWS_REGION
      }
    }
  }
});

function App({ signOut, user }) {
  const theme = useTheme();
  const [selectedView, setSelectedView] = useState('analyzer');
  const [isExpanded, setIsExpanded] = useState(true);
  const [accessToken, setAccessToken] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  // Fetch access token when component mounts
  useEffect(() => {
    const getAccessToken = async () => {
      try {
        setIsLoading(true);
        const jwtToken = await getAuthToken();
        console.log("JWT Token available:", Boolean(jwtToken));
        setAccessToken(jwtToken);
      } catch (error) {
        console.error('Error fetching auth session:', error);
      } finally {
        setIsLoading(false);
      }
    };

    getAccessToken();
  }, []);

  const menuItems = [
    { id: 'analyzer', text: 'Document Analyzer', icon: <DocumentScannerIcon />, tooltip: 'Analyze Documents' },
    { id: 'prompts', text: 'Prompt Manager', icon: <AutoAwesomeIcon />, tooltip: 'Manage Prompts' },
    { id: 'configs', text: 'Configuration', icon: <SettingsIcon />, tooltip: 'System Configuration' },
    { id: 'signout', text: 'Sign Out', icon: <LogoutIcon />, tooltip: 'Sign Out', onClick: signOut },
  ];

  // Show loading state while fetching access token
  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      <Drawer
        variant="permanent"
        sx={{
          width: isExpanded ? expandedWidth : collapsedWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: isExpanded ? expandedWidth : collapsedWidth,
            boxSizing: 'border-box',
            overflowX: 'hidden',
            transition: 'width 0.2s',
            backgroundColor: theme.palette.background.default,
            borderRight: `1px solid ${theme.palette.divider}`,
          },
        }}
      >
        <Box sx={{ 
          overflow: 'hidden', 
          mt: 2,
          display: 'flex',
          flexDirection: 'column',
          height: '100%',
        }}>
          <Box sx={{ 
            display: 'flex', 
            alignItems: 'center',
            justifyContent: 'space-between',
            px: 2,
            py: 1,
          }}>
            {isExpanded && (
              <>
                <Typography 
                  variant="h6" 
                  sx={{ 
                    fontWeight: 600,
                    color: theme.palette.primary.main 
                  }}
                >
                  Document Analysis
                </Typography>
                <Typography variant="body2" sx={{ ml: 1 }}>
                  {user.username}
                </Typography>
              </>
            )}
            <IconButton 
              onClick={() => setIsExpanded(!isExpanded)}
              sx={{ 
                ml: isExpanded ? 0 : 'auto',
                mr: isExpanded ? 0 : 'auto',
                '&:hover': {
                  backgroundColor: theme.palette.action.hover,
                }
              }}
            >
              {isExpanded ? <ChevronLeftIcon /> : <ChevronRightIcon />}
            </IconButton>
          </Box>
          <Divider sx={{ my: 1 }} />
          <List>
            {menuItems.map((item) => (
              <Tooltip 
                key={item.id}
                title={!isExpanded ? item.tooltip : ''}
                placement="right"
              >
                <ListItem
                  button
                  selected={selectedView === item.id}
                  onClick={() => {
                    if (item.onClick) {
                      item.onClick();
                    } else {
                      setSelectedView(item.id);
                    }
                  }}
                  sx={{
                    justifyContent: isExpanded ? 'initial' : 'center',
                    px: isExpanded ? 2 : 1,
                    my: 0.5,
                    borderRadius: 1,
                    '&.Mui-selected': {
                      backgroundColor: theme.palette.primary.light,
                      '&:hover': {
                        backgroundColor: theme.palette.primary.light,
                      }
                    },
                    '&:hover': {
                      backgroundColor: theme.palette.action.hover,
                    }
                  }}
                >
                  <ListItemIcon sx={{
                    minWidth: isExpanded ? 40 : 'auto',
                    justifyContent: 'center',
                    color: selectedView === item.id ? theme.palette.primary.main : 'inherit'
                  }}>
                    {item.icon}
                  </ListItemIcon>
                  {isExpanded && (
                    <ListItemText 
                      primary={item.text}
                      sx={{
                        '& .MuiListItemText-primary': {
                          color: selectedView === item.id ? theme.palette.primary.main : 'inherit'
                        }
                      }}
                    />
                  )}
                </ListItem>
              </Tooltip>
            ))}
          </List>
        </Box>
      </Drawer>
      <Box 
        component="main" 
        sx={{ 
          flexGrow: 1,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'flex-start',
          p: 3,
          transition: 'all 0.2s',
          width: '100%',
          backgroundColor: theme.palette.background.default,
        }}
      >
        <Box sx={{ 
          width: '100%',
          maxWidth: '1200px',
          mx: 'auto',
          transition: 'all 0.2s',
        }}>
          <Suspense fallback={
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
              <CircularProgress />
            </Box>
          }>
            {(() => {
              switch (selectedView) {
                case 'analyzer':
                  return <DocumentAnalyzer accessToken={accessToken} />;
                case 'prompts':
                  return <PromptManager accessToken={accessToken} />;
                case 'configs':
                  return <ConfigurationManager accessToken={accessToken} />;
                default:
                  return <DocumentAnalyzer accessToken={accessToken} />;
              }
            })()}
          </Suspense>
        </Box>
      </Box>
    </Box>
  );
}

export default withAuthenticator(App);
