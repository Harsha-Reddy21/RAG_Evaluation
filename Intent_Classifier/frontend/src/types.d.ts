declare module 'react-markdown' {
  import React from 'react';
  
  interface ReactMarkdownProps {
    children: string;
    [key: string]: any;
  }
  
  const ReactMarkdown: React.FC<ReactMarkdownProps>;
  export default ReactMarkdown;
}

declare module 'react-chartjs-2' {
  import React from 'react';
  
  interface ChartProps {
    data: any;
    options?: any;
    [key: string]: any;
  }
  
  export const Line: React.FC<ChartProps>;
  export const Bar: React.FC<ChartProps>;
  export const Pie: React.FC<ChartProps>;
  export const Doughnut: React.FC<ChartProps>;
} 