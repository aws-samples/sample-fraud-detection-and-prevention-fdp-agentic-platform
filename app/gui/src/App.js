// Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import { useState, lazy, Suspense } from 'react';
import { useAuth } from "react-oidc-context";
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
import VerifiedUserIcon from '@mui/icons-material/VerifiedUser';

// Lazy load components to reduce initial bundle size
const DocumentAnalyzer = lazy(() => import('./components/DocumentAnalyzer'));
const PromptManager = lazy(() => import('./components/PromptManager'));
const ConfigurationManager = lazy(() => import('./components/ConfigurationManager'));
const GuestUser = lazy(() => import('./components/GuestUser'));
const StrandsVerification = lazy(() => import('./components/StrandsVerification'));
const Dashboard = lazy(() => import('./components/Dashboard'));

const expandedWidth = 240;
const collapsedWidth = 65;

function App() {
  const theme = useTheme();
  const auth = useAuth();
  const [selectedView, setSelectedView] = useState('dashboard');
  const [isExpanded, setIsExpanded] = useState(true);

  const menuItems = [
    { id: 'dashboard', text: 'Dashboard', icon: <ChevronRightIcon />, tooltip: 'Dashboard' },
    { id: 'analyzer', text: 'Document Analyzer', icon: <DocumentScannerIcon />, tooltip: 'Analyze Documents' },
    { id: 'verification', text: 'Advanced Verification', icon: <VerifiedUserIcon />, tooltip: 'Advanced Verification' },
    { id: 'prompts', text: 'Prompt Manager', icon: <AutoAwesomeIcon />, tooltip: 'Manage Prompts' },
    { id: 'configs', text: 'Configuration', icon: <SettingsIcon />, tooltip: 'System Configuration' },
    { id: 'signout', text: 'Sign Out', icon: <LogoutIcon />, tooltip: 'Sign Out', onClick: () => auth.removeUser() },
  ];

  // Show loading state while initializing auth
  if (auth.isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  // Show error state if authentication fails
  if (auth.error) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', flexDirection: 'column' }}>
        <Typography color="error" gutterBottom>
          Authentication Error
        </Typography>
        <Typography color="textSecondary" gutterBottom>
          {auth.error.message}
        </Typography>
        <IconButton onClick={() => auth.signinRedirect()}>
          Try Again
        </IconButton>
      </Box>
    );
  }

  // Show not logged in component if user is not authenticated
  if (!auth.isAuthenticated) {
    return (
      <Suspense fallback={
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
          <CircularProgress />
        </Box>
      }>
        <GuestUser />
      </Suspense>
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
                  {auth.user?.profile.username}
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
                case 'dashboard':
                  return <Dashboard setSelectedView={setSelectedView} />;
                case 'analyzer':
                  return <DocumentAnalyzer accessToken={auth.user?.access_token} />;
                case 'verification':
                  return <StrandsVerification accessToken={auth.user?.access_token} />;
                case 'prompts':
                  return <PromptManager accessToken={auth.user?.access_token} />;
                case 'configs':
                  return <ConfigurationManager accessToken={auth.user?.access_token} />;
                default:
                  return <Dashboard setSelectedView={setSelectedView} />;
              }
            })()}
          </Suspense>
        </Box>
      </Box>
    </Box>
  );
}

export default App;
