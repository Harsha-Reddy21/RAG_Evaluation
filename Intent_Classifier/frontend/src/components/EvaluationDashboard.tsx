import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Paper, 
  Typography, 
  Button, 
  CircularProgress,
  Grid,
  Card,
  CardContent,
  FormControlLabel,
  Switch,
  TextField,
  Divider,
  Alert
} from '@mui/material';
import { getMetrics, runTests, Metrics } from '../services/api';

const EvaluationDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [loading, setLoading] = useState(false);
  const [testLoading, setTestLoading] = useState(false);
  const [useOpenAI, setUseOpenAI] = useState(false);
  const [numSamples, setNumSamples] = useState(5);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchMetrics();
  }, []);

  const fetchMetrics = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await getMetrics();
      setMetrics(response.metrics);
    } catch (error) {
      console.error('Error fetching metrics:', error);
      setError('Failed to fetch metrics. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleRunTests = async () => {
    setTestLoading(true);
    setError(null);
    
    try {
      await runTests({
        num_samples: numSamples,
        use_openai: useOpenAI
      });
      
      // Fetch updated metrics after tests run
      await fetchMetrics();
    } catch (error) {
      console.error('Error running tests:', error);
      setError('Failed to run tests. Please try again.');
    } finally {
      setTestLoading(false);
    }
  };

  const renderMetricCard = (title: string, value: number | string, suffix: string = '') => (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>
        <Typography variant="h4" color="primary">
          {typeof value === 'number' ? value.toFixed(2) : value}{suffix}
        </Typography>
      </CardContent>
    </Card>
  );

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Evaluation Dashboard
      </Typography>
      
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Run Tests
        </Typography>
        
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <TextField
            label="Number of Samples"
            type="number"
            value={numSamples}
            onChange={(e) => setNumSamples(Math.max(1, parseInt(e.target.value) || 1))}
            sx={{ width: 150 }}
            size="small"
          />
          
          <FormControlLabel
            control={
              <Switch
                checked={useOpenAI}
                onChange={(e) => setUseOpenAI(e.target.checked)}
              />
            }
            label="Use OpenAI"
          />
          
          <Button
            variant="contained"
            onClick={handleRunTests}
            disabled={testLoading}
            sx={{ ml: 'auto' }}
          >
            {testLoading ? <CircularProgress size={24} /> : 'Run Tests'}
          </Button>
        </Box>
        
        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}
      </Paper>
      
      <Typography variant="h5" gutterBottom>
        Performance Metrics
        <Button 
          variant="outlined" 
          size="small" 
          onClick={fetchMetrics} 
          disabled={loading}
          sx={{ ml: 2 }}
        >
          Refresh
        </Button>
      </Typography>
      
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      ) : metrics ? (
        <>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3, mb: 4 }}>
            <Box sx={{ width: { xs: '100%', sm: '47%', md: '23%' } }}>
              {renderMetricCard('Intent Accuracy', metrics.intent_accuracy * 100, '%')}
            </Box>
            <Box sx={{ width: { xs: '100%', sm: '47%', md: '23%' } }}>
              {renderMetricCard('Avg Relevance', metrics.avg_relevance * 100, '%')}
            </Box>
            <Box sx={{ width: { xs: '100%', sm: '47%', md: '23%' } }}>
              {renderMetricCard('Context Utilization', metrics.avg_context_utilization * 100, '%')}
            </Box>
            <Box sx={{ width: { xs: '100%', sm: '47%', md: '23%' } }}>
              {renderMetricCard('Avg Latency', metrics.avg_latency, 's')}
            </Box>
          </Box>
          
          <Divider sx={{ my: 3 }} />
          
          <Typography variant="h5" gutterBottom>
            Intent Distribution
          </Typography>
          
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3 }}>
            {Object.entries(metrics.samples_per_intent).map(([intent, count]) => (
              <Box key={intent} sx={{ width: { xs: '100%', sm: '31%' } }}>
                <Card>
                  <CardContent>
                    <Typography variant="h6">{intent}</Typography>
                    <Typography variant="h4" color="primary">
                      {count} samples
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {((count / metrics.total_samples) * 100).toFixed(1)}% of total
                    </Typography>
                  </CardContent>
                </Card>
              </Box>
            ))}
          </Box>
        </>
      ) : (
        <Alert severity="info" sx={{ mt: 2 }}>
          No metrics available. Run tests to generate evaluation data.
        </Alert>
      )}
    </Box>
  );
};

export default EvaluationDashboard; 