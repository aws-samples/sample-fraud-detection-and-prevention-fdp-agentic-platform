// src/components/PromptManager.js
import { useState, useEffect } from 'react';
import { generateClient } from 'aws-amplify/api';
import { signOut } from 'aws-amplify/auth';
import {
  Box,
  Paper,
  Typography,
  Button,
  TextField,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Checkbox,
  FormControlLabel,
  CircularProgress,
  Snackbar,
  Alert,
  Tooltip,
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import VisibilityIcon from '@mui/icons-material/Visibility';

function PromptManager({ accessToken }) {
  const [prompts, setPrompts] = useState([]);
  const [openDialog, setOpenDialog] = useState(false);
  const [currentPrompt, setCurrentPrompt] = useState({ role: '', tasks: '', is_active: false });
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [deletePromptId, setDeletePromptId] = useState(null);
  const [formErrors, setFormErrors] = useState({});
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [previewPrompt, setPreviewPrompt] = useState(null);
  const client = generateClient();

  useEffect(() => {
    if (accessToken) {
      fetchPrompts();
    }
  }, [accessToken]);

  const fetchPrompts = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await client.get({
        apiName: 'documentAnalyzerApi',
        path: '/prompts',
        headers: {
          Authorization: accessToken
        }
      });
      setPrompts(response);
    } catch (error) {
      console.error('Error details:', {
        message: error.message,
        response: error.response,
        stack: error.stack
      });
      handleAPIError(error);
    } finally {
      setLoading(false);
    }
  };

  const validateForm = () => {
    const errors = {};
    if (!currentPrompt.role.trim()) {
      errors.role = 'Role is required';
    }
    if (!currentPrompt.tasks.trim()) {
      errors.tasks = 'Tasks are required';
    }
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validateForm()) return;

    setLoading(true);
    try {
      if (isEditing) {
        await client.put({
          apiName: 'documentAnalyzerApi',
          path: `/prompts/${currentPrompt.id}`,
          headers: {
            Authorization: accessToken
          },
          options: {
            body: currentPrompt
          }
        });
        setSnackbar({
          open: true,
          message: 'Prompt updated successfully',
          severity: 'success'
        });
      } else {
        await client.post({
          apiName: 'documentAnalyzerApi',
          path: '/prompts',
          headers: {
            Authorization: accessToken
          },
          options: {
            body: currentPrompt
          }
        });
        setSnackbar({
          open: true,
          message: 'Prompt created successfully',
          severity: 'success'
        });
      }
      handleClose();
      fetchPrompts();
    } catch (error) {
      handleAPIError(error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    try {
      await client.del({
        apiName: 'documentAnalyzerApi',
        path: `/prompts/${deletePromptId}`,
        headers: {
          Authorization: accessToken
        }
      });
      setSnackbar({
        open: true,
        message: 'Prompt deleted successfully',
        severity: 'success'
      });
      fetchPrompts();
    } catch (error) {
      handleAPIError(error);
    } finally {
      setDeletePromptId(null);
    }
  };

  const handleAPIError = (error) => {
    console.error('API Error:', error);
    let errorMessage = 'An unexpected error occurred';
  
    if (error.response) {
      errorMessage = error.response.data.message || 
                    error.response.data.error || 
                    `Error: ${error.response.status}`;
    } else if (error.message) {
      errorMessage = error.message;
    }

    setSnackbar({
      open: true,
      message: errorMessage,
      severity: 'error'
    });
  };

  const handleAuthError = async (error) => {
    if (error.response?.status === 401) {
      try {
        await signOut();
        // Handle redirect after signout if needed
      } catch (signOutError) {
        console.error('Error signing out:', signOutError);
      }
    }
  };

  const handleClose = () => {
    setOpenDialog(false);
    setCurrentPrompt({ role: '', tasks: '', is_active: false });
    setIsEditing(false);
    setFormErrors({});
  };

  const handlePreviewClose = () => {
    setPreviewPrompt(null);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h5" sx={{ mb: 3 }}>
        Prompt Manager
      </Typography>

      <Button 
        variant="contained" 
        onClick={() => setOpenDialog(true)}
        sx={{ mb: 3 }}
      >
        Add New Prompt
      </Button>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell width="25%">Role</TableCell>
              <TableCell width="45%">Tasks</TableCell>
              <TableCell width="10%">Active</TableCell>
              <TableCell width="20%">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={4} align="center" sx={{ py: 3 }}>
                  <CircularProgress size={24} />
                </TableCell>
              </TableRow>
            ) : error ? (
              <TableRow>
                <TableCell colSpan={4} align="center" sx={{ color: 'error.main' }}>
                  {error}
                </TableCell>
              </TableRow>
            ) : prompts.length === 0 ? (
              <TableRow>
                <TableCell colSpan={4} align="center">
                  No prompts found. Add a new prompt to get started.
                </TableCell>
              </TableRow>
            ) : (
              prompts.map((prompt) => (
                <TableRow key={prompt.id}>
                  <TableCell>{prompt.role}</TableCell>
                  <TableCell>
                    <Typography
                      sx={{
                        maxHeight: '60px',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        display: '-webkit-box',
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: 'vertical',
                      }}
                    >
                      {prompt.tasks}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Checkbox
                      checked={prompt.is_active}
                      disabled
                    />
                  </TableCell>
                  <TableCell>
                    <Tooltip title="View">
                      <IconButton 
                        onClick={() => setPreviewPrompt(prompt)}
                        size="small"
                      >
                        <VisibilityIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Edit">
                      <IconButton 
                        onClick={() => {
                          setCurrentPrompt(prompt);
                          setIsEditing(true);
                          setOpenDialog(true);
                        }}
                        size="small"
                      >
                        <EditIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete">
                      <IconButton 
                        onClick={() => setDeletePromptId(prompt.id)}
                        color="error"
                        size="small"
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Add/Edit Dialog */}
      <Dialog 
        open={openDialog} 
        onClose={handleClose}
        maxWidth="md"
        fullWidth={true}    
      >
        <DialogTitle>
          {isEditing ? 'Edit Prompt' : 'New Prompt'}
        </DialogTitle>
        <DialogContent 
          sx={{ 
            p: 3, 
            '&.MuiDialogContent-root': {
              paddingTop: '24px !important' // Override Material-UI's default padding
            }
          }}
        >
          <TextField
            fullWidth
            multiline
            rows={2}
            label="Role"
            value={currentPrompt.role}
            onChange={(e) => {
              setCurrentPrompt({ ...currentPrompt, role: e.target.value });
              setFormErrors({ ...formErrors, role: '' });
            }}
            error={Boolean(formErrors.role)}
            helperText={formErrors.role}
            sx={{ mb: 2 }}
          />
          <TextField
            fullWidth
            multiline
            rows={8}
            label="Tasks"
            value={currentPrompt.tasks}
            onChange={(e) => {
              setCurrentPrompt({ ...currentPrompt, tasks: e.target.value });
              setFormErrors({ ...formErrors, tasks: '' });
            }}
            error={Boolean(formErrors.tasks)}
            helperText={formErrors.tasks}
            sx={{ mb: 2 }}
          />
          <FormControlLabel
            control={
              <Checkbox
                checked={currentPrompt.is_active}
                onChange={(e) => setCurrentPrompt({ ...currentPrompt, is_active: e.target.checked })}
              />
            }
            label="Set as Active Prompt"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button 
            onClick={handleSubmit} 
            variant="contained"
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : isEditing ? 'Update' : 'Save'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Preview Dialog */}
      <Dialog
        open={Boolean(previewPrompt)}
        onClose={handlePreviewClose}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">
              Prompt Details
            </Typography>
            <Button
              startIcon={<EditIcon />}
              onClick={() => {
                setCurrentPrompt(previewPrompt);
                setIsEditing(true);
                setOpenDialog(true);
                handlePreviewClose();
              }}
            >
              Edit
            </Button>
          </Box>
        </DialogTitle>
        <DialogContent sx={{ pt: 2 }}>
          <Typography variant="subtitle1" color="primary" gutterBottom>
            Role
          </Typography>
          <Typography paragraph sx={{ whiteSpace: 'pre-wrap' }}>
            {previewPrompt?.role}
          </Typography>

          <Typography variant="subtitle1" color="primary" gutterBottom>
            Tasks
          </Typography>
          <Typography 
            sx={{ 
              whiteSpace: 'pre-wrap',
              backgroundColor: 'grey.50',
              p: 2,
              borderRadius: 1,
              maxHeight: '400px',
              overflow: 'auto'
            }}
          >
            {previewPrompt?.tasks}
          </Typography>

          <Box sx={{ mt: 2, display: 'flex', alignItems: 'center' }}>
            <Typography variant="subtitle1" color="primary" sx={{ mr: 1 }}>
              Active Status:
            </Typography>
            <Checkbox
              checked={previewPrompt?.is_active || false}
              disabled
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handlePreviewClose}>
            Close
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={Boolean(deletePromptId)}
        onClose={() => setDeletePromptId(null)}
      >
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          Are you sure you want to delete this prompt?
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeletePromptId(null)}>Cancel</Button>
          <Button 
            onClick={handleDelete}
            color="error"
            variant="contained"
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert 
          onClose={() => setSnackbar({ ...snackbar, open: false })} 
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}

export default PromptManager;
