// src/components/DocumentAnalyzer.js
import { useState, useEffect } from 'react';
import { generateClient } from 'aws-amplify/api';
import { signOut } from 'aws-amplify/auth';
import ProcessingAnimation from './ProcessingAnimation';
import {
  Box,
  Container,
  Paper,
  Typography,
  Button,
  Alert,
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
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import VisibilityIcon from '@mui/icons-material/Visibility';
import CloseIcon from '@mui/icons-material/Close';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { materialLight } from 'react-syntax-highlighter/dist/esm/styles/prism';

function DocumentAnalyzer({ accessToken }) {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [analyzedDocuments, setAnalyzedDocuments] = useState([]);
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedResult, setSelectedResult] = useState(null);
  const [openImageDialog, setOpenImageDialog] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);
  const client = generateClient();

  useEffect(() => {
    if (accessToken) {
      fetchVerifications();
    }
  }, [accessToken]);

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

    setError(errorMessage);
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

  const fetchVerifications = async () => {
    try {
      console.log('Fetching verifications...');

      const response = await client.get({
        apiName: 'documentAnalyzerApi',
        path: '/verifications',
        headers: {
          Authorization: accessToken
        }
      });

      console.log('Verification data:', response);

      // Ensure the response data is in the expected format
      if (Array.isArray(response)) {
        // Add data validation
        const validatedData = response.map(doc => ({
          ...doc,
          id: doc.id || `temp-${Date.now()}`, // Ensure each doc has an ID
          confidence: Number(doc.confidence), // Convert confidence to number
          preview_url: doc.preview_url || '', // Ensure preview_url exists
          document_type: doc.document_type || 'Unknown', // Ensure document_type exists
          timestamp: doc.timestamp || new Date().toISOString() // Ensure timestamp exists
        }));

        setAnalyzedDocuments(validatedData);
      } else {
        throw new Error('Invalid response format');
      }
    } catch (error) {
      console.error('Error details:', {
        message: error.message,
        response: error.response,
        stack: error.stack
      });

      handleAPIError(error);

      if (error.response?.status === 401) {
        handleAuthError(error);
      }
    }
  };

  const handleFileSelect = (event) => {
    const selectedFile = event.target.files[0];
    setFile(selectedFile);
    setError(null);

    if (selectedFile) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result);
      };
      reader.readAsDataURL(selectedFile);
    }
  };

  const handleOpenDialog = (doc) => {
    setSelectedResult(doc);
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedResult(null);
  };

  const handleSubmit = async () => {
    if (!file) return;

    setLoading(true);
    setError(null);

    try {
      const base64Image = preview.split(',')[1];

      const response = await client.post({
        apiName: 'documentAnalyzerApi',
        path: '/verifications',
        headers: {
          Authorization: accessToken
        },
        options: {
          body: {
            image_base64: base64Image
          }
        }
      });

      console.log('Analysis response:', response);

      const processedResponse = {
        ...response,
        confidence: Number(response.confidence),
        preview_url: response.preview_url
      };

      console.log('Processed response:', processedResponse);

      setAnalyzedDocuments(prev => [...prev, processedResponse]);
      setFile(null);
      setPreview(null);
    } catch (error) {
      console.error('Error:', error);
      setError(error.response?.data?.message || 'An error occurred during analysis');
    } finally {
      setLoading(false);
    }
  };

  const handleImageClick = (imageUrl) => {
    setSelectedImage(imageUrl);
    setOpenImageDialog(true);
  };

  const handleCloseImageDialog = () => {
    setOpenImageDialog(false);
    setSelectedImage(null);
  };

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Paper
        elevation={3}
        sx={{
          p: 4,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 3,
          backgroundColor: '#ffffff',
        }}
      >
        <Typography variant="h4" component="h1" gutterBottom align="center">
          Document Analyzer
        </Typography>

        {/* Upload Area */}
        <Box
          sx={{
            width: '100%',
            height: 200,
            border: '2px dashed #1976d2',
            borderRadius: 2,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'pointer',
            backgroundColor: '#f8f9fa',
            transition: 'all 0.3s ease',
            '&:hover': {
              borderColor: '#0d47a1',
              backgroundColor: '#e3f2fd',
            },
          }}
          component="label"
        >
          <input
            type="file"
            hidden
            accept="image/*"
            onChange={handleFileSelect}
            disabled={loading}
          />
          <CloudUploadIcon sx={{ fontSize: 48, color: '#1976d2', mb: 1 }} />
          <Typography color="textSecondary">
            {file ? file.name : 'Drag and drop or click to upload'}
          </Typography>
        </Box>

        {/* Preview */}
        {preview && (
          <Paper
            elevation={2}
            sx={{
              width: '100%',
              p: 2,
              display: 'flex',
              justifyContent: 'center',
              backgroundColor: '#f8f9fa',
            }}
          >
            <img
              src={preview}
              alt="Preview"
              style={{
                maxWidth: '100%',
                maxHeight: '300px',
                objectFit: 'contain',
              }}
            />
          </Paper>
        )}

        {/* Loading Animation */}
        {loading && (
          <Box 
            sx={{ 
              width: '100%',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: 2,
              py: 3
            }}
          >
            <ProcessingAnimation />
            <Box 
              sx={{ 
                display: 'flex', 
                flexDirection: 'column',
                alignItems: 'center',
                gap: 1 
              }}
            >
              <Typography 
                variant="body1" 
                color="primary"
                sx={{ fontWeight: 500 }}
              >
                Processing Document
              </Typography>
              <Typography 
                variant="body2" 
                color="text.secondary"
                sx={{ 
                  textAlign: 'center',
                  animation: 'fade 3s infinite',
                  '@keyframes fade': {
                    '0%, 100%': {
                      opacity: 1,
                    },
                    '50%': {
                      opacity: 0.5,
                    },
                  },
                }}
              >
                Analyzing security features and validating authenticity...
              </Typography>
            </Box>
          </Box>
        )}

        {/* Submit Button */}
        <Button
          variant="contained"
          onClick={handleSubmit}
          disabled={loading || !file}
          sx={{
            minWidth: 200,
            height: 48,
            textTransform: 'none',
            fontSize: '1.1rem',
            fontWeight: 500,
          }}
        >
          {loading ? 'Processing...' : 'Analyze Document'}
        </Button>

        {/* Error Message */}
        {error && (
          <Alert 
            severity="error" 
            sx={{ 
              width: '100%',
              '& .MuiAlert-message': { width: '100%' }
            }}
          >
            {error}
          </Alert>
        )}

        {/* Results Table */}
        {analyzedDocuments.length > 0 && (
          <>
            <Paper 
              elevation={2}
              sx={{ 
                width: '100%', 
                bgcolor: '#f8f9fa',
                borderRadius: 2,
                mt: 3
              }}
            >
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Document Image</TableCell>
                      <TableCell>Document Type</TableCell>
                      <TableCell>Verification Status</TableCell>
                      <TableCell>Date</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {analyzedDocuments.map((doc) => (
                      <TableRow key={doc.id}>
                        <TableCell>
                          <img
                            src={doc.preview_url}
                            alt="Document"
                            onClick={() => handleImageClick(doc.preview_url)}
                            style={{
                              width: '100px',
                              height: '70px',
                              objectFit: 'cover',
                              borderRadius: '4px',
                              cursor: 'pointer', // Add cursor pointer to indicate clickable
                              transition: 'transform 0.2s', // Add smooth hover effect
                              '&:hover': {
                                transform: 'scale(1.05)',
                              },
                            }}
                          />
                        </TableCell>
                        <TableCell>
                          <Typography
                            sx={{
                              bgcolor: 'primary.light',
                              color: 'primary.dark',
                              py: 0.5,
                              px: 1.5,
                              borderRadius: 1,
                              display: 'inline-block',
                              fontSize: '0.875rem',
                            }}
                          >
                            {doc.document_type}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          {typeof doc.confidence === 'number' && doc.confidence >= 0.95 ? (
                            <Typography
                              component="span"
                              sx={{
                                color: 'success.main',
                                bgcolor: 'success.light',
                                py: 1,
                                px: 2,
                                borderRadius: 1,
                                fontWeight: 'medium',
                              }}
                            >
                              Pass
                            </Typography>
                          ) : (
                            <Typography
                              component="span"
                              sx={{
                                color: 'error.main',
                                bgcolor: 'error.light',
                                py: 1,
                                px: 2,
                                borderRadius: 1,
                                fontWeight: 'medium',
                              }}
                            >
                              Review
                            </Typography>
                          )}
                        </TableCell>
                        <TableCell>
                          {new Date(doc.timestamp).toLocaleString()}
                        </TableCell>
                        <TableCell>
                          <IconButton
                            color="primary"
                            onClick={() => handleOpenDialog(doc)}
                            size="small"
                          >
                            <VisibilityIcon />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Paper>

            {/* Dialog for showing details */}
            <Dialog
              open={openDialog}
              onClose={handleCloseDialog}
              maxWidth="md"
              fullWidth
            >
              <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="h6">Analysis Results</Typography>
                <IconButton onClick={handleCloseDialog} size="small">
                  <CloseIcon />
                </IconButton>
              </DialogTitle>
              <DialogContent dividers>
                {selectedResult && (
                  <Box sx={{
                    backgroundColor: '#ffffff',
                    p: 3,
                    borderRadius: 1,
                  }}>
                    <ReactMarkdown
                      components={{
                        code({node, inline, className, children, ...props}) {
                          const match = /language-(\w+)/.exec(className || '');
                          return !inline && match ? (
                            <SyntaxHighlighter
                              style={materialLight}
                              language={match[1]}
                              PreTag="div"
                              {...props}
                            >
                              {String(children).replace(/\n$/, '')}
                            </SyntaxHighlighter>
                          ) : (
                            <code className={className} {...props}>
                              {children}
                            </code>
                          );
                        }
                      }}
                    >
                      {selectedResult.content_text}
                    </ReactMarkdown>
                  </Box>
                )}
              </DialogContent>
              <DialogActions>
                <Button 
                  onClick={handleCloseDialog}
                  variant="contained"
                  sx={{ textTransform: 'none' }}
                >
                  Close
                </Button>
              </DialogActions>
            </Dialog>

            {/*Dialog for full-size image */}
            <Dialog
              open={openImageDialog}
              onClose={handleCloseImageDialog}
              maxWidth="lg"
              fullWidth
              PaperProps={{
                style: {
                  backgroundColor: 'transparent',
                  boxShadow: 'none',
                },
              }}
            >
              <Box
                sx={{
                  position: 'relative',
                  backgroundColor: 'transparent',
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                }}
              >
                <IconButton
                  onClick={handleCloseImageDialog}
                  sx={{
                    position: 'absolute',
                    right: 8,
                    top: 8,
                    color: 'white',
                    backgroundColor: 'rgba(0, 0, 0, 0.5)',
                    '&:hover': {
                      backgroundColor: 'rgba(0, 0, 0, 0.7)',
                    },
                    zIndex: 1,
                  }}
                >
                  <CloseIcon />
                </IconButton>
                {selectedImage && (
                  <img
                    src={selectedImage}
                    alt="Full size document"
                    style={{
                      maxWidth: '100%',
                      maxHeight: '90vh',
                      objectFit: 'contain',
                    }}
                  />
                )}
              </Box>
            </Dialog>
          </>
        )}
      </Paper>
    </Container>
  );
}

export default DocumentAnalyzer;
