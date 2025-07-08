import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { 
  Box, 
  AppBar, 
  Toolbar, 
  Typography, 
  Button, 
  Container, 
  CssBaseline,
  ThemeProvider,
  createTheme
} from '@mui/material';
import ChatInterface from './components/ChatInterface';
import EvaluationDashboard from './components/EvaluationDashboard';

// Create a theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#f50057',
    },
  },
});

const App: React.FC = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
          <AppBar position="static">
            <Toolbar>
              <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                RAG Pipeline with Intent Detection
              </Typography>
              <Button color="inherit" component={Link} to="/">
                Chat
              </Button>
              <Button color="inherit" component={Link} to="/evaluation">
                Evaluation
              </Button>
            </Toolbar>
          </AppBar>
          
          <Container sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', p: 0 }}>
            <Routes>
              <Route path="/" element={<ChatInterface />} />
              <Route path="/evaluation" element={<EvaluationDashboard />} />
            </Routes>
          </Container>
          
          <Box component="footer" sx={{ py: 2, textAlign: 'center', bgcolor: 'background.paper' }}>
            <Typography variant="body2" color="text.secondary">
              © {new Date().getFullYear()} RAG Pipeline with Intent Detection
            </Typography>
          </Box>
        </Box>
      </Router>
    </ThemeProvider>
  );
};

export default App; 