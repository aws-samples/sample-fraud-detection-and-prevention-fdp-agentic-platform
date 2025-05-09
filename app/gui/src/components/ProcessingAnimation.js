// src/components/ProcessingAnimation.js
import { Box } from '@mui/material';
import DocumentScannerIcon from '@mui/icons-material/DocumentScanner';

const ProcessingAnimation = () => {
  return (
    <Box
      sx={{
        position: 'relative',
        width: '200px',
        height: '250px',
        margin: '0 auto',
        '@keyframes scan': {
          '0%': {
            transform: 'translateY(0)',
            opacity: 0.5,
          },
          '50%': {
            opacity: 1,
          },
          '100%': {
            transform: 'translateY(200px)',
            opacity: 0.5,
          },
        },
      }}
    >
      {/* Document background */}
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          backgroundColor: '#f5f5f5',
          border: '1px solid #ddd',
          borderRadius: '4px',
        }}
      />

      {/* Scanning line */}
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '2px',
          backgroundColor: '#2196f3',
          animation: 'scan 2s linear infinite',
          boxShadow: '0 0 8px rgba(33, 150, 243, 0.8)',
        }}
      />

      {/* Scanner icon */}
      <DocumentScannerIcon
        sx={{
          position: 'absolute',
          top: '-24px',
          left: '50%',
          transform: 'translateX(-50%)',
          color: '#2196f3',
          fontSize: '48px',
        }}
      />
    </Box>
  );
};

export default ProcessingAnimation;
