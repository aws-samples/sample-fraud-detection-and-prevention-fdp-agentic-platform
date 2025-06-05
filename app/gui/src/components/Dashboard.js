import { 
  Box, 
  Card, 
  CardContent, 
  Grid, 
  Typography, 
  Button,
  useTheme
} from '@mui/material';
import DocumentScannerIcon from '@mui/icons-material/DocumentScanner';
import VerifiedUserIcon from '@mui/icons-material/VerifiedUser';
import SettingsIcon from '@mui/icons-material/Settings';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';

const FeatureCard = ({ title, description, icon, onClick }) => {
  const theme = useTheme();
  
  return (
    <Card 
      sx={{ 
        height: '100%', 
        display: 'flex', 
        flexDirection: 'column',
        transition: 'transform 0.2s, box-shadow 0.2s',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: '0 8px 16px rgba(0, 0, 0, 0.1)',
        }
      }}
    >
      <CardContent sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
        <Box 
          sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            mb: 2,
            color: theme.palette.primary.main
          }}
        >
          {icon}
          <Typography variant="h6" component="h2" ml={1} fontWeight="500">
            {title}
          </Typography>
        </Box>
        <Typography variant="body1" color="text.secondary" paragraph sx={{ flexGrow: 1 }}>
          {description}
        </Typography>
        <Button 
          variant="contained" 
          color="primary"
          onClick={onClick}
          fullWidth
        >
          Open
        </Button>
      </CardContent>
    </Card>
  );
};

const Dashboard = ({ setSelectedView }) => {
  const features = [
    {
      id: 'analyzer',
      title: 'Document Analyzer',
      description: 'Upload and analyze documents to extract information and detect potential fraud.',
      icon: <DocumentScannerIcon fontSize="large" />,
    },
    {
      id: 'verification',
      title: 'Advanced Verification',
      description: 'Use AI agent technology for in-depth document verification with interactive feedback.',
      icon: <VerifiedUserIcon fontSize="large" />,
    },
    {
      id: 'prompts',
      title: 'Prompt Manager',
      description: 'Create and manage prompts used for document analysis and verification.',
      icon: <AutoAwesomeIcon fontSize="large" />,
    },
    {
      id: 'configs',
      title: 'Configuration',
      description: 'Manage system configurations including model settings and inference parameters.',
      icon: <SettingsIcon fontSize="large" />,
    }
  ];

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom fontWeight="500">
        Fraud Detection Platform
      </Typography>
      <Typography variant="body1" paragraph>
        Welcome to the Fraud Detection and Prevention Platform. Use the tools below to analyze and verify documents.
      </Typography>
      
      <Grid container spacing={3} mt={2}>
        {features.map((feature) => (
          <Grid item xs={12} md={6} key={feature.id}>
            <FeatureCard
              title={feature.title}
              description={feature.description}
              icon={feature.icon}
              onClick={() => setSelectedView(feature.id)}
            />
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default Dashboard;
