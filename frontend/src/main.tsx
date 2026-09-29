import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import App from './App';
import { AstraXFamilyPage } from './pages/AstraXFamilyPage';
import { AstraThemeProvider } from './brand/AstraThemeContext';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <AstraThemeProvider>
        <Routes>
          <Route path="/" element={<App />} />
          <Route path="/astrax" element={<AstraXFamilyPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AstraThemeProvider>
    </BrowserRouter>
  </React.StrictMode>,
);
