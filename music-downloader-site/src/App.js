import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LandingPage from './components/LandingPage';
import { GuidePage } from './pages/GuidePage';  // 新增我们的向导页面
import { FAQPage, ContactPage } from './pages/FAQPage';

// 引入样式文件（保留你的时尚品味！）
import './App.css';

function App() {
  return (
    // 注意这里我们加入了 basename，就像给房子加上了门牌号
    <Router basename="/qqmusicdownloader">
      <div className="min-h-screen bg-gray-50">
        <Routes>
          {/* 主页永远是我们温馨的客厅 */}
          <Route path="/" element={<LandingPage />} />
          {/* 使用教程就像是我们的图书室 */}
          <Route path="/guide" element={<GuidePage />} />
          <Route path="/faq" element={<FAQPage />} />        {/* 新添加的！*/}
          <Route path="/contact" element={<ContactPage />} /> {/* 新添加的！*/}
        </Routes>
      </div>
    </Router>
  );
}

export default App;