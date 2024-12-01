// ./src/App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LandingPage from './components/LandingPage';
import GuidePage from './pages/GuidePage';  // 如果 GuidePage 使用默认导出
import FAQPage from './pages/FAQPage';      // 默认导出
import ContactPage from './pages/ContactPage'; // 默认导出

// 引入样式文件
import './App.css';

function App() {
  return (
    <Router basename="/qqmusicdownloader">
      <div className="min-h-screen bg-gray-50">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/guide" element={<GuidePage />} />
          <Route path="/faq" element={<FAQPage />} />
          <Route path="/contact" element={<ContactPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
