import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';

const link = document.createElement('link');
link.href = 'https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap';
link.rel = 'stylesheet';
document.head.appendChild(link);

ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById('root')
);

reportWebVitals();
