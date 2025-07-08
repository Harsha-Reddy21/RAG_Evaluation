import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Types
export interface QueryRequest {
  query: string;
  use_openai: boolean;
  true_intent?: string;
}

export interface QueryResponse {
  query: string;
  intent: string;
  confidence: number;
  response: string;
  latency: number;
  context: string[];
  relevance?: number;
  context_utilization?: number;
}

export interface TestRequest {
  num_samples: number;
  use_openai: boolean;
}

export interface Metrics {
  intent_accuracy: number;
  avg_relevance: number;
  avg_context_utilization: number;
  avg_latency: number;
  samples_per_intent: Record<string, number>;
  total_samples: number;
}

export interface EvaluationResponse {
  metrics: Metrics;
}

// API functions
export const sendQuery = async (request: QueryRequest): Promise<QueryResponse> => {
  try {
    const response = await axios.post(`${API_URL}/query`, request);
    return response.data;
  } catch (error) {
    console.error('Error sending query:', error);
    throw error;
  }
};

export const streamQuery = (
  request: QueryRequest,
  onMetadata: (metadata: any) => void,
  onChunk: (chunk: string) => void,
  onCompletion: (completion: any) => void,
  onError: (error: any) => void
) => {
  const controller = new AbortController();
  const signal = controller.signal;

  fetch(`${API_URL}/query/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
    signal
  })
  .then(response => {
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    
    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('Response body is null');
      return;
    }
    
    const decoder = new TextDecoder();
    
    function processStream(): Promise<void> {
      // We've already checked that reader is not undefined above
      return reader!.read().then(({ done, value }) => {
        if (done) {
          return;
        }
        
        const text = decoder.decode(value, { stream: true });
        const lines = text.split('\n').filter(line => line.trim() !== '');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.substring(6));
              
              if (data.type === 'metadata') {
                onMetadata(data);
              } else if (data.type === 'chunk') {
                onChunk(data.content);
              } else if (data.type === 'completion') {
                onCompletion(data);
                return; // Stop processing after completion
              }
            } catch (e) {
              console.error('Error parsing SSE data:', e, line);
            }
          }
        }
        
        return processStream();
      });
    }
    
    processStream().catch((error: Error) => {
      onError(error);
    });
  })
  .catch((error: Error) => {
    onError(error);
  });

  return () => {
    controller.abort();
  };
};

export const runTests = async (request: TestRequest): Promise<EvaluationResponse> => {
  try {
    const response = await axios.post(`${API_URL}/test`, request);
    return response.data;
  } catch (error) {
    console.error('Error running tests:', error);
    throw error;
  }
};

export const getMetrics = async (): Promise<EvaluationResponse> => {
  try {
    const response = await axios.get(`${API_URL}/metrics`);
    return response.data;
  } catch (error) {
    console.error('Error getting metrics:', error);
    throw error;
  }
}; 