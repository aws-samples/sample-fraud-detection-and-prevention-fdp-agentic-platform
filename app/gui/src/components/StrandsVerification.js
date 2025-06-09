import { useState, useEffect } from 'react';
import { 
  Box, 
  Button, 
  Card, 
  CardContent, 
  CircularProgress, 
  Container, 
  Grid, 
  Paper, 
  TextField, 
  Typography 
} from '@mui/material';
import { apiPost, apiGet, apiPut } from '../utils/api';
import { useDropzone } from 'react-dropzone';
import { styled } from '@mui/material/styles';

// Styled components
const VerificationCard = styled(Card)(({ theme }) => ({
  marginBottom: theme.spacing(3),
  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)'
}));

const DocumentPreview = styled('img')({
  width: '100%',
  maxHeight: '300px',
  objectFit: 'contain',
  marginBottom: '16px'
});

const DropzoneArea = styled('div')(({ theme }) => ({
  border: `2px dashed ${theme.palette.primary.main}`,
  borderRadius: theme.shape.borderRadius,
  padding: theme.spacing(4),
  textAlign: 'center',
  cursor: 'pointer',
  marginBottom: theme.spacing(3),
  '&:hover': {
    backgroundColor: theme.palette.action.hover
  }
}));

const StepItem = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  marginBottom: theme.spacing(2),
  backgroundColor: theme.palette.background.default
}));

const ConfidenceIndicator = styled(Box)(({ theme, value }) => ({
  width: '100%',
  height: '8px',
  backgroundColor: theme.palette.grey[300],
  borderRadius: '4px',
  position: 'relative',
  '&::after': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: 0,
    height: '100%',
    width: `${value * 100}%`,
    backgroundColor: value > 0.7 
      ? theme.palette.success.main 
      : value > 0.4 
        ? theme.palette.warning.main 
        : theme.palette.error.main,
    borderRadius: '4px'
  }
}));

const StrandsVerification = ({ accessToken }) => {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState('');
  const [loading, setLoading] = useState(false);
  const [verificationId, setVerificationId] = useState(null);
  const [verificationStatus, setVerificationStatus] = useState(null);
  const [additionalInfo, setAdditionalInfo] = useState('');
  const [statusPolling, setStatusPolling] = useState(null);

  const { getRootProps, getInputProps } = useDropzone({
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png']
    },
    onDrop: acceptedFiles => {
      const selectedFile = acceptedFiles[0];
      setFile(selectedFile);
      
      const reader = new FileReader();
      reader.onload = () => {
        setPreview(reader.result);
      };
      reader.readAsDataURL(selectedFile);
    }
  });

  useEffect(() => {
    return () => {
      // Clean up polling when component unmounts
      if (statusPolling) {
        clearInterval(statusPolling);
      }
    };
  }, [statusPolling]);

  const handleStartVerification = async () => {
    if (!file) return;
    
    setLoading(true);
    try {
      // Convert file to base64
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = async () => {
        const base64data = reader.result.split(',')[1];
        
        // Call API to start verification
        const response = await apiPost('/agent/verify', accessToken, {
          body: {
            image_base64: base64data,
            document_type: null, // Let the agent determine the document type
            metadata: {}
          }
        });
        
        setVerificationId(response.verification_id);
        
        // Start polling for status updates
        const interval = setInterval(() => {
          fetchVerificationStatus(response.verification_id);
        }, 3000);
        
        setStatusPolling(interval);
      };
    } catch (error) {
      console.error('Error starting verification:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchVerificationStatus = async (id) => {
    try {
      const status = await apiGet(`/agent/verify/${id}`, accessToken, {});
      setVerificationStatus(status);
      
      // Stop polling if verification is complete or failed
      if (status.status === 'completed' || status.status === 'failed') {
        clearInterval(statusPolling);
        setStatusPolling(null);
      }
    } catch (error) {
      console.error('Error fetching verification status:', error);
    }
  };

  const handleProvideAdditionalInfo = async () => {
    if (!additionalInfo || !verificationId) return;
    
    setLoading(true);
    try {
      await apiPut(`/agent/verify/${verificationId}`, accessToken, {
        body: {
          additional_info: additionalInfo
        }
      });
      
      // Refresh status
      fetchVerificationStatus(verificationId);
      
      // Clear input
      setAdditionalInfo('');
    } catch (error) {
      console.error('Error providing additional info:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderVerificationSteps = () => {
    if (!verificationStatus || !verificationStatus.steps || verificationStatus.steps.length === 0) {
      return <Typography>No verification steps available yet.</Typography>;
    }

    return (
      <Box>
        <Typography variant="h6" gutterBottom>Verification Steps</Typography>
        {verificationStatus.steps.map((step) => (
          <StepItem key={step.step_id} elevation={1}>
            <Typography variant="subtitle1" fontWeight="bold">{step.name}</Typography>
            <Typography variant="body2" color="textSecondary">{step.description}</Typography>
            <Box display="flex" alignItems="center" mt={1}>
              <Typography variant="body2" mr={1}>
                Status: <strong>{step.status}</strong>
              </Typography>
              {step.confidence && (
                <>
                  <Typography variant="body2" mr={1}>
                    Confidence: <strong>{(step.confidence * 100).toFixed(1)}%</strong>
                  </Typography>
                  <ConfidenceIndicator value={step.confidence} />
                </>
              )}
            </Box>
            {step.details && (
              <Box mt={1}>
                <Typography variant="body2">Details:</Typography>
                <pre style={{ 
                  backgroundColor: '#f5f5f5', 
                  padding: '8px', 
                  borderRadius: '4px',
                  overflowX: 'auto',
                  fontSize: '0.8rem'
                }}>
                  {JSON.stringify(step.details, null, 2)}
                </pre>
              </Box>
            )}
          </StepItem>
        ))}
      </Box>
    );
  };

  const renderVerificationSummary = () => {
    if (!verificationStatus) return null;

    return (
      <Box mt={3}>
        <Typography variant="h6" gutterBottom>Verification Summary</Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Paper elevation={1} sx={{ p: 2 }}>
              <Typography variant="subtitle2">Status</Typography>
              <Typography variant="body1" fontWeight="bold">
                {verificationStatus.status}
              </Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} md={6}>
            <Paper elevation={1} sx={{ p: 2 }}>
              <Typography variant="subtitle2">Document Type</Typography>
              <Typography variant="body1" fontWeight="bold">
                {verificationStatus.document_type || 'Unknown'}
              </Typography>
            </Paper>
          </Grid>
          {verificationStatus.confidence && (
            <Grid item xs={12}>
              <Paper elevation={1} sx={{ p: 2 }}>
                <Typography variant="subtitle2">Overall Confidence</Typography>
                <Box display="flex" alignItems="center">
                  <Typography variant="body1" fontWeight="bold" mr={2}>
                    {(verificationStatus.confidence * 100).toFixed(1)}%
                  </Typography>
                  <ConfidenceIndicator value={verificationStatus.confidence} />
                </Box>
              </Paper>
            </Grid>
          )}
          {verificationStatus.result_summary && (
            <Grid item xs={12}>
              <Paper elevation={1} sx={{ p: 2 }}>
                <Typography variant="subtitle2">Summary</Typography>
                <Typography variant="body1">
                  {verificationStatus.result_summary}
                </Typography>
              </Paper>
            </Grid>
          )}
        </Grid>
      </Box>
    );
  };

  const renderAdditionalInfoRequest = () => {
    if (!verificationStatus || verificationStatus.status !== 'needs_info') return null;

    return (
      <Box mt={3}>
        <Typography variant="h6" gutterBottom>Additional Information Needed</Typography>
        <Paper elevation={1} sx={{ p: 2 }}>
          <Typography variant="body1" mb={2}>
            {verificationStatus.needs_info?.message || 'Please provide additional information to continue verification.'}
          </Typography>
          <TextField
            fullWidth
            multiline
            rows={4}
            variant="outlined"
            label="Additional Information"
            value={additionalInfo}
            onChange={(e) => setAdditionalInfo(e.target.value)}
            margin="normal"
          />
          <Button 
            variant="contained" 
            color="primary"
            onClick={handleProvideAdditionalInfo}
            disabled={loading || !additionalInfo}
          >
            Submit Information
          </Button>
        </Paper>
      </Box>
    );
  };

  return (
    <Container maxWidth="lg">
      <Typography variant="h4" component="h1" gutterBottom>
        Advanced Document Verification
      </Typography>
      <Typography variant="body1" paragraph>
        Upload a document for advanced verification using AI agent technology.
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={5}>
          <VerificationCard>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Document Upload
              </Typography>
              
              {!verificationId ? (
                <>
                  <DropzoneArea {...getRootProps()}>
                    <input {...getInputProps()} />
                    {preview ? (
                      <DocumentPreview src={preview} alt="Document preview" />
                    ) : (
                      <Typography>
                        Drag and drop a document image here, or click to select a file
                      </Typography>
                    )}
                  </DropzoneArea>
                  
                  <Button
                    variant="contained"
                    color="primary"
                    fullWidth
                    disabled={!file || loading}
                    onClick={handleStartVerification}
                  >
                    {loading ? <CircularProgress size={24} /> : 'Start Verification'}
                  </Button>
                </>
              ) : (
                <>
                  {verificationStatus?.preview_url ? (
                    <DocumentPreview src={verificationStatus.preview_url} alt="Document" />
                  ) : preview ? (
                    <DocumentPreview src={preview} alt="Document preview" />
                  ) : null}
                  
                  <Typography variant="body2" color="textSecondary" align="center">
                    Verification ID: {verificationId}
                  </Typography>
                </>
              )}
            </CardContent>
          </VerificationCard>
          
          {renderVerificationSummary()}
          {renderAdditionalInfoRequest()}
        </Grid>
        
        <Grid item xs={12} md={7}>
          <VerificationCard>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Verification Process
              </Typography>
              
              {loading && !verificationStatus && (
                <Box display="flex" justifyContent="center" my={4}>
                  <CircularProgress />
                </Box>
              )}
              
              {verificationStatus?.status === 'in_progress' && (
                <Box display="flex" alignItems="center" mb={3}>
                  <CircularProgress size={20} sx={{ mr: 1 }} />
                  <Typography>Verification in progress...</Typography>
                </Box>
              )}
              
              {renderVerificationSteps()}
            </CardContent>
          </VerificationCard>
        </Grid>
      </Grid>
    </Container>
  );
};

export default StrandsVerification;
