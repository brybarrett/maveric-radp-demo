import React, { useEffect } from 'react';
import Dashboard from './components/Dashboard';
import './App.css';

function App() {
  const client = process.env.REACT_APP_CLIENT || 'docbot';
  const isMaveric = client === 'maveric';

  // Dynamically inject Maveric theme CSS if needed
  useEffect(() => {
    if (isMaveric) {
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = '/maveric-theme.css';
      document.head.appendChild(link);
      
      return () => {
        document.head.removeChild(link);
      };
    }
  }, [isMaveric]);

  return (
    <div className="App">
      <Dashboard />
    </div>
  );
}

export default App;