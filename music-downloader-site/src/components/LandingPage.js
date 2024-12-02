import React from 'react';
import { Link } from 'react-router-dom';
import { Download, Music, Settings, Coffee, Github } from 'lucide-react';

// 导航组件 - 处理顶部导航栏的显示
const Navbar = () => (
  <nav className="fixed w-full top-0 bg-white/80 backdrop-blur-sm z-50 shadow-sm">
    <div className="container mx-auto px-4 py-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Music className="w-6 h-6 text-blue-600" />
          <span className="text-lg font-bold text-gray-800">极简音乐下载器</span>
        </div>
        <div className="flex items-center gap-4">
          <a 
            href="https://github.com/yuqie6/qqmusicdownloader" 
            target="_blank" 
            rel="noopener noreferrer"
            className="flex items-center gap-1 text-gray-600 hover:text-blue-600 transition-colors"
          >
            <Github className="w-5 h-5" />
            <span>GitHub</span>
          </a>
          <a 
            href="#download"
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            下载
          </a>
        </div>
      </div>
    </div>
  </nav>
);

// 特性卡片组件 - 用于显示产品特点
const FeatureCard = ({ icon, title, description }) => (
  <div className="bg-white p-6 rounded-xl border border-gray-200 hover:shadow-lg transition-all duration-300 group">
    <div className="text-blue-600 mb-4 group-hover:scale-110 transition-transform duration-300">
      {icon}
    </div>
    <h3 className="text-xl font-semibold text-gray-800 mb-2">
      {title}
    </h3>
    <p className="text-gray-600">
      {description}
    </p>
  </div>
);

// 下载按钮组件 - 统一的下载按钮样式
const DownloadButton = ({ className = '' }) => (
  <a
  href="https://github.com/yuqie6/qqmusicdownloader/releases/tag/v1.0.0"
    className={`inline-flex items-center px-6 py-3 bg-white text-blue-600 rounded-lg font-semibold 
    hover:bg-blue-50 active:bg-blue-100 transition-colors duration-200 shadow-lg ${className}`}
  >
    <Download className="w-5 h-5 mr-2" />
    立即下载 v1.0.0
  </a>
);

// 主页面组件
const LandingPage = () => {
  

  return (
    <div className="min-h-screen">
      <Navbar />
      
      {/* Hero Section - 主要展示区域 */}
      <div className="relative pt-16">
        <div className="bg-gradient-to-br from-blue-600 to-purple-600">
          <div className="container mx-auto px-4 py-24">
            <div className="max-w-3xl mx-auto text-center">
              <h1 className="text-4xl md:text-6xl font-bold text-white mb-6 animate-fade-in">
                极简音乐下载器
              </h1>
              <p className="text-lg md:text-xl text-white/90 mb-8">
                简单易用的音乐下载工具，让音乐触手可及
              </p>
              <DownloadButton />
            </div>
          </div>
        </div>
      </div>

      {/* Features Section - 功能特性展示区域 */}
      <div className="py-20 bg-gray-50">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center text-gray-800 mb-12">
            为什么选择我们？
          </h2>
          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            <FeatureCard
              icon={<Music className="w-8 h-8" />}
              title="文件无加密"
              description="文件没有任何加密下载到本地，可以无限制离线播放"
            />
            <FeatureCard
              icon={<Settings className="w-8 h-8" />}
              title="简单易用"
              description="界面直观友好，操作简单，一键下载你喜欢的音乐。"
            />
            <FeatureCard
              icon={<Coffee className="w-8 h-8" />}
              title="完美适配"
              description="完美适配windows系统，多次调试，完美兼容。 "
            />
          </div>
        </div>
      </div>

      {/* Download Section - 下载区域 */}
      <div id="download" className="py-20 bg-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold text-gray-800 mb-6">
            准备好开始了吗？
          </h2>
          <p className="text-gray-600 mb-8 max-w-2xl mx-auto">
            立即下载极简音乐下载器，开启你的音乐之旅。完全免费，无需注册。
          </p>
          <DownloadButton />
        </div>
      </div>

      {/* Footer - 页脚区域 */}
      <footer className="bg-gray-800 text-white py-12">
        <div className="container mx-auto px-4">
          <div className="max-w-6xl mx-auto">
            <div className="grid md:grid-cols-2 gap-8">
              <div>
                <h3 className="text-lg font-semibold mb-4">关于我们</h3>
                <p className="text-gray-400">
                  极简音乐下载器致力于为用户提供简单、高效的音乐下载体验。
                  一个开源项目，欢迎贡献和反馈。
                  下载文件不可商用，仅供个人学习使用。
                  只是作者用于学习交流，请勿用于商业用途。
        
                  须确保版权合法，否则后果自负。

                </p>
              </div>
              <div className="md:text-right">
                <h3 className="text-lg font-semibold mb-4">快速链接</h3>
                <div className="flex flex-col md:items-end gap-2">
                  {/* 把那些老式的 <a> 标签换成时尚的 Link 组件 */}
                  <Link 
                    to="/guide" 
                    className="text-gray-400 hover:text-white transition-colors"
                  >
                    使用教程
                  </Link>
                  <Link 
                    to="/faq" 
                    className="text-gray-400 hover:text-white transition-colors"
                  >
                    常见问题
                  </Link>
                  <Link 
                    to="/contact" 
                    className="text-gray-400 hover:text-white transition-colors"
                  >
                    联系我们
                  </Link>
                </div>
              </div>
            </div>
            <div className="border-t border-gray-700 mt-8 pt-8 text-center">
              <p className="text-gray-400">© 2024 极简音乐下载器. All rights reserved.</p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;