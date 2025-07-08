import React, { useState, useEffect } from 'react';
import './App.css';
import { 
  Container, 
  Typography, 
  TextField, 
  Button, 
  Paper, 
  Box, 
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  Divider,
  Alert,
  Card,
  CardContent,
  Grid,
  LinearProgress,
  Chip
} from '@mui/material';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import FileUploadIcon from '@mui/icons-material/FileUpload';
import SendIcon from '@mui/icons-material/Send';
import AssessmentIcon from '@mui/icons-material/Assessment';

// Create theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#388e3c',
    },
  },
});

function App() {
  const [query, setQuery] = useState('');
  const [answer, setAnswer] = useState('');
  const [sources, setSources] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [metricsHistory, setMetricsHistory] = useState([]);
  const [showMetrics, setShowMetrics] = useState(false);
  
  const API_URL = 'http://localhost:8000';
  
  // Fetch metrics history on component mount
  useEffect(() => {
    fetchMetricsHistory();
  }, []);
  
  const fetchMetricsHistory = async () => {
    try {
      const response = await fetch(`${API_URL}/metrics`);
      const data = await response.json();
      setMetricsHistory(data.metrics_history);
    } catch (error) {
      console.error('Error fetching metrics history:', error);
    }
  };
  
  const handleQuerySubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    
    setLoading(true);
    setAnswer('');
    setSources([]);
    setMetrics(null);
    
    try {
      const response = await fetch(`${API_URL}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query,
          evaluation: true,
        }),
      });
      
      const data = await response.json();
      
      setAnswer(data.answer);
      setSources(data.sources);
      setMetrics(data.evaluation_metrics);
      
      // Refresh metrics history
      fetchMetricsHistory();
      
    } catch (error) {
      console.error('Error querying API:', error);
      setAnswer('Error: Could not get response from the API');
    } finally {
      setLoading(false);
    }
  };
  
  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };
  
  const handleFileUpload = async (e) => {
    e.preventDefault();
    if (!file) return;
    
    setUploading(true);
    setUploadStatus(null);
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const response = await fetch(`${API_URL}/upload`, {
        method: 'POST',
        body: formData,
      });
      
      const data = await response.json();
      setUploadStatus({
        success: data.success,
        message: data.message,
      });
      
    } catch (error) {
      console.error('Error uploading file:', error);
      setUploadStatus({
        success: false,
        message: 'Error uploading file',
      });
    } finally {
      setUploading(false);
    }
  };
  
  const getMetricColor = (value) => {
    if (value >= 0.9) return 'success';
    if (value >= 0.75) return 'warning';
    return 'error';
  };
  
  const toggleMetricsView = () => {
    setShowMetrics(!showMetrics);
  };
  
  return (
    <ThemeProvider theme={theme}>
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom align="center">
          Medical Knowledge Assistant
        </Typography>
        
        <Grid container spacing={3}>
          {/* Document Upload Section */}
          <Grid item xs={12} md={4}>
            <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                Upload Medical Documents
              </Typography>
              <form onSubmit={handleFileUpload}>
                <Box sx={{ mb: 2 }}>
                  <input
                    accept="application/pdf"
                    style={{ display: 'none' }}
                    id="file-upload"
                    type="file"
                    onChange={handleFileChange}
                  />
                  <label htmlFor="file-upload">
                    <Button
                      variant="contained"
                      component="span"
                      startIcon={<FileUploadIcon />}
                      fullWidth
                    >
                      Select PDF
                    </Button>
                  </label>
                </Box>
                
                {file && (
                  <Typography variant="body2" gutterBottom>
                    Selected: {file.name}
                  </Typography>
                )}
                
                <Button
                  type="submit"
                  variant="contained"
                  color="secondary"
                  disabled={!file || uploading}
                  fullWidth
                >
                  {uploading ? <CircularProgress size={24} /> : 'Upload'}
                </Button>
                
                {uploadStatus && (
                  <Alert 
                    severity={uploadStatus.success ? 'success' : 'error'} 
                    sx={{ mt: 2 }}
                  >
                    {uploadStatus.message}
                  </Alert>
                )}
              </form>
            </Paper>
            
            {/* Metrics Dashboard Toggle */}
            <Button
              variant="outlined"
              startIcon={<AssessmentIcon />}
              onClick={toggleMetricsView}
              fullWidth
              sx={{ mb: 3 }}
            >
              {showMetrics ? 'Hide Metrics Dashboard' : 'Show Metrics Dashboard'}
            </Button>
            
            {/* Metrics Dashboard */}
            {showMetrics && (
              <Paper elevation={3} sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  RAGAS Metrics Dashboard
                </Typography>
                
                {metricsHistory.length > 0 ? (
                  <>
                    <Typography variant="subtitle2" gutterBottom>
                      Recent Evaluations
                    </Typography>
                    
                    {metricsHistory.slice(0, 5).map((entry, index) => (
                      <Card key={index} sx={{ mb: 2 }}>
                        <CardContent>
                          <Typography variant="body2" color="text.secondary" gutterBottom>
                            {new Date(entry.timestamp).toLocaleString()}
                          </Typography>
                          <Typography variant="body2" noWrap sx={{ mb: 1 }}>
                            Query: {entry.query}
                          </Typography>
                          
                          <Box sx={{ mb: 1 }}>
                            <Typography variant="body2" component="span">
                              Faithfulness: 
                            </Typography>
                            <LinearProgress 
                              variant="determinate" 
                              value={entry.metrics.faithfulness * 100}
                              color={getMetricColor(entry.metrics.faithfulness)}
                              sx={{ mx: 1, display: 'inline-block', width: '60%' }}
                            />
                            <Typography variant="body2" component="span">
                              {(entry.metrics.faithfulness * 100).toFixed(0)}%
                            </Typography>
                          </Box>
                          
                          <Box sx={{ mb: 1 }}>
                            <Typography variant="body2" component="span">
                              Context Precision: 
                            </Typography>
                            <LinearProgress 
                              variant="determinate" 
                              value={entry.metrics.context_precision * 100}
                              color={getMetricColor(entry.metrics.context_precision)}
                              sx={{ mx: 1, display: 'inline-block', width: '60%' }}
                            />
                            <Typography variant="body2" component="span">
                              {(entry.metrics.context_precision * 100).toFixed(0)}%
                            </Typography>
                          </Box>
                          
                          <Typography variant="body2">
                            Latency: {entry.latency.toFixed(2)}s
                          </Typography>
                        </CardContent>
                      </Card>
                    ))}
                  </>
                ) : (
                  <Typography variant="body1">
                    No evaluation data available yet. Ask questions to generate metrics.
                  </Typography>
                )}
              </Paper>
            )}
          </Grid>
          
          {/* Query Section */}
          <Grid item xs={12} md={8}>
            <Paper elevation={3} sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Ask Medical Questions
              </Typography>
              <form onSubmit={handleQuerySubmit}>
                <TextField
                  fullWidth
                  label="Enter your medical question"
                  variant="outlined"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  sx={{ mb: 2 }}
                />
                <Button
                  type="submit"
                  variant="contained"
                  endIcon={<SendIcon />}
                  disabled={loading || !query.trim()}
                  fullWidth
                >
                  {loading ? <CircularProgress size={24} /> : 'Ask'}
                </Button>
              </form>
              
              {/* Answer Section */}
              {answer && (
                <Box sx={{ mt: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    Answer
                  </Typography>
                  <Paper elevation={1} sx={{ p: 2, bgcolor: 'background.default' }}>
                    <Typography variant="body1">{answer}</Typography>
                  </Paper>
                  
                  {/* Metrics Section */}
                  {metrics && (
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="subtitle1" gutterBottom>
                        RAGAS Evaluation Metrics
                      </Typography>
                      <Grid container spacing={1}>
                        <Grid item xs={6} sm={3}>
                          <Chip 
                            label={`Faithfulness: ${(metrics.faithfulness * 100).toFixed(0)}%`}
                            color={getMetricColor(metrics.faithfulness)}
                            sx={{ width: '100%' }}
                          />
                        </Grid>
                        <Grid item xs={6} sm={3}>
                          <Chip 
                            label={`Context Precision: ${(metrics.context_precision * 100).toFixed(0)}%`}
                            color={getMetricColor(metrics.context_precision)}
                            sx={{ width: '100%' }}
                          />
                        </Grid>
                        <Grid item xs={6} sm={3}>
                          <Chip 
                            label={`Context Recall: ${(metrics.context_recall * 100).toFixed(0)}%`}
                            color={getMetricColor(metrics.context_recall)}
                            sx={{ width: '100%' }}
                          />
                        </Grid>
                        <Grid item xs={6} sm={3}>
                          <Chip 
                            label={`Answer Relevancy: ${(metrics.answer_relevancy * 100).toFixed(0)}%`}
                            color={getMetricColor(metrics.answer_relevancy)}
                            sx={{ width: '100%' }}
                          />
                        </Grid>
                      </Grid>
                    </Box>
                  )}
                  
                  {/* Sources Section */}
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="subtitle1" gutterBottom>
                      Sources
                    </Typography>
                    <List>
                      {sources.map((source, index) => (
                        <React.Fragment key={index}>
                          <ListItem alignItems="flex-start">
                            <ListItemText
                              primary={`Source ${index + 1}`}
                              secondary={source}
                            />
                          </ListItem>
                          {index < sources.length - 1 && <Divider />}
                        </React.Fragment>
                      ))}
                    </List>
                  </Box>
                </Box>
              )}
            </Paper>
          </Grid>
        </Grid>
      </Container>
    </ThemeProvider>
  );
}

export default App; 