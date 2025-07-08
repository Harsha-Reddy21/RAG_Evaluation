import React, { useState, useRef, useEffect } from 'react';
import { 
  Box, 
  TextField, 
  Button, 
  Paper, 
  Typography, 
  Chip,
  FormControlLabel,
  Switch,
  CircularProgress,
  Divider
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import ReactMarkdown from 'react-markdown';
import { sendQuery, streamQuery, QueryRequest, QueryResponse } from '../services/api';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  intent?: string;
  confidence?: number;
  context?: string[];
  latency?: number;
  contextUtilization?: number;
}

const ChatInterface: React.FC = () => {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [useOpenAI, setUseOpenAI] = useState(false);
  const [useStreaming, setUseStreaming] = useState(true);
  const [currentStreamingMessage, setCurrentStreamingMessage] = useState('');
  const messagesEndRef = useRef<null | HTMLDivElement>(null);
  const abortControllerRef = useRef<() => void | null>(null);

  // Scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, currentStreamingMessage]);

  // Clean up any active stream when component unmounts
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current();
      }
    };
  }, []);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: input,
      sender: 'user',
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const request: QueryRequest = {
        query: input,
        use_openai: useOpenAI,
      };

      if (useStreaming) {
        // Handle streaming response
        setCurrentStreamingMessage('');
        let metadata: any = null;

        // Clean up any previous stream
        if (abortControllerRef.current) {
          abortControllerRef.current();
        }

        const cleanup = streamQuery(
          request,
          (data) => {
            metadata = data;
          },
          (chunk) => {
            setCurrentStreamingMessage(prev => prev + chunk);
          },
          (completion) => {
            const botMessage: Message = {
              id: Date.now().toString(),
              text: currentStreamingMessage + completion.content || currentStreamingMessage,
              sender: 'bot',
              intent: metadata?.intent,
              confidence: metadata?.confidence,
              context: metadata?.context,
              latency: completion.latency,
              contextUtilization: completion.context_utilization
            };
            
            setMessages(prev => [...prev, botMessage]);
            setCurrentStreamingMessage('');
            setLoading(false);
          },
          (error) => {
            console.error('Streaming error:', error);
            setLoading(false);
            
            const errorMessage: Message = {
              id: Date.now().toString(),
              text: 'Sorry, there was an error processing your request.',
              sender: 'bot',
            };
            
            setMessages(prev => [...prev, errorMessage]);
          }
        );

        abortControllerRef.current = cleanup;
      } else {
        // Handle non-streaming response
        const response: QueryResponse = await sendQuery(request);
        
        const botMessage: Message = {
          id: Date.now().toString(),
          text: response.response,
          sender: 'bot',
          intent: response.intent,
          confidence: response.confidence,
          context: response.context,
          latency: response.latency,
          contextUtilization: response.context_utilization
        };
        
        setMessages(prev => [...prev, botMessage]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      
      const errorMessage: Message = {
        id: Date.now().toString(),
        text: 'Sorry, there was an error processing your request.',
        sender: 'bot',
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      if (!useStreaming) {
        setLoading(false);
      }
    }
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ p: 2, backgroundColor: 'primary.main', color: 'white' }}>
        <Typography variant="h6">Customer Support Chat</Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <FormControlLabel
            control={
              <Switch
                checked={useOpenAI}
                onChange={(e) => setUseOpenAI(e.target.checked)}
                color="default"
              />
            }
            label="Use OpenAI"
          />
          <FormControlLabel
            control={
              <Switch
                checked={useStreaming}
                onChange={(e) => setUseStreaming(e.target.checked)}
                color="default"
              />
            }
            label="Streaming"
          />
        </Box>
      </Box>

      <Box sx={{ flexGrow: 1, p: 2, overflow: 'auto' }}>
        {messages.map((message) => (
          <Box
            key={message.id}
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: message.sender === 'user' ? 'flex-end' : 'flex-start',
              mb: 2,
            }}
          >
            <Paper
              elevation={1}
              sx={{
                p: 2,
                maxWidth: '80%',
                backgroundColor: message.sender === 'user' ? 'primary.light' : 'grey.100',
                color: message.sender === 'user' ? 'white' : 'inherit',
                borderRadius: 2,
              }}
            >
              <ReactMarkdown>{message.text}</ReactMarkdown>
            </Paper>
            
            {message.sender === 'bot' && message.intent && (
              <Box sx={{ mt: 1, display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  <Chip 
                    label={`Intent: ${message.intent}`} 
                    size="small" 
                    color="primary" 
                    variant="outlined" 
                  />
                  <Chip 
                    label={`Confidence: ${(message.confidence! * 100).toFixed(1)}%`} 
                    size="small" 
                    color="primary" 
                    variant="outlined" 
                  />
                  <Chip 
                    label={`Latency: ${message.latency?.toFixed(2)}s`} 
                    size="small" 
                    color="primary" 
                    variant="outlined" 
                  />
                  {message.contextUtilization !== undefined && (
                    <Chip 
                      label={`Context Usage: ${(message.contextUtilization * 100).toFixed(1)}%`} 
                      size="small" 
                      color="primary" 
                      variant="outlined" 
                    />
                  )}
                </Box>
                
                {message.context && message.context.length > 0 && (
                  <Box sx={{ mt: 1 }}>
                    <Typography variant="caption" sx={{ fontWeight: 'bold' }}>
                      Context Used:
                    </Typography>
                    <Paper variant="outlined" sx={{ p: 1, mt: 0.5, backgroundColor: 'grey.50' }}>
                      {message.context.map((ctx, i) => (
                        <Typography key={i} variant="caption" component="div" sx={{ mb: 0.5 }}>
                          • {ctx}
                        </Typography>
                      ))}
                    </Paper>
                  </Box>
                )}
              </Box>
            )}
          </Box>
        ))}

        {currentStreamingMessage && (
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'flex-start',
              mb: 2,
            }}
          >
            <Paper
              elevation={1}
              sx={{
                p: 2,
                maxWidth: '80%',
                backgroundColor: 'grey.100',
                borderRadius: 2,
              }}
            >
              <ReactMarkdown>{currentStreamingMessage}</ReactMarkdown>
            </Paper>
          </Box>
        )}
        
        <div ref={messagesEndRef} />
      </Box>

      <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <TextField
            fullWidth
            placeholder="Type your message here..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            disabled={loading}
            multiline
            maxRows={4}
          />
          <Button
            variant="contained"
            color="primary"
            onClick={handleSend}
            disabled={loading || !input.trim()}
            sx={{ minWidth: '50px', height: '56px' }}
          >
            {loading ? <CircularProgress size={24} /> : <SendIcon />}
          </Button>
        </Box>
      </Box>
    </Box>
  );
};

export default ChatInterface; 