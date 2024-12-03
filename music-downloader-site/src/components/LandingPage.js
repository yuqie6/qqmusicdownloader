import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Download, Music, Settings, Coffee, Github, AlertTriangle, Clock } from 'lucide-react';

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

const LegalWarning = () => (
  <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-8 rounded">
    <div className="flex items-center">
      <AlertTriangle className="w-5 h-5 text-red-500 mr-2" />
      <p className="text-red-700">
        本软件仅供个人学习和研究使用，严禁用于商业用途。用户需确保下载内容符合相关版权法规，
        任何因违规使用造成的法律责任由用户自行承担。
      </p>
    </div>
  </div>
);

const Changelog = () => {
  const versions = [
    {
      version: 'v1.2.0',
      date: '2024-12-03',
      type: '功能更新',
      features: [
        {
          title: '✨ 新增功能',
          changes: [
            '📁 新增了路径选择，方便用户自定义下载位置',
            '💡 在选择格式时新增温馨提示，方便用户使用'
          ]
        },
        {
          title: '💄 界面优化',
          changes: [
            '🎨 重新设计了界面布局，采用现代化的卡片式设计',
            '✨ 优化了按钮和控件的视觉效果',
            '📁 新增了路径选择按钮，方便用户自定义下载位置',
            '🔄 把音质选择改为了文件格式选择，更加准确',
            '🎯 设计了单独的程序图标'
          ]
        },
        {
          title: '🐛 修复问题',
          changes: [
            '修复了文件已存在时仍会下载',
            '修改了about信息'
          ]
        },
        {
          title: '⚠️ 已知问题',
          changes: [
            '进度条还是有问题，作者能力有限',
            '多次搜索，搜索栏会遗留歌名，点击即可看见真实歌名'
          ]
        }
      ]
    },
    {
      version: 'v1.1.0',
      date: '2024-12-02',
      type: '重大更新',
      features: [
        {
          title: '✨ 新增功能',
          changes: [
            '🚀 支持批量下载 - 终于可以一次下载至多20首歌了！',
            '⏯️ 新增下载暂停/继续功能 - 当你的网速像蜗牛时，至少可以暂停一下~',
            '📊 下载进度实时显示 - 再也不用盯着文件夹傻等了'
          ]
        },
        {
          title: '💄 优化',
          changes: [
            '界面有所改动，增加了下载暂停/继续按钮',
            '下载完成后通知更及时，再也不用盯着文件夹傻等了'
          ]
        },
        {
          title: '⚠️ 已知问题',
          changes: [
            '进度条会抽风',
            'cookie检验机制有问题，不保证100%可用'
          ]
        }
      ]
    },
    {
      version: 'v1.0.0',
      date: '2024-12-01',
      type: '首次发布',
      features: [
        {
          title: '🎉 首次发布',
          changes: [
            '🔍 支持QQ音乐歌曲搜索',
            '⬇️ 单曲下载功能',
            '🎨 简洁的界面设计'
          ]
        }
      ]
    }
  ];

  return (
    <div className="max-w-3xl mx-auto">
      <h3 className="text-xl font-semibold mb-6 flex items-center gap-2">
        <Clock className="w-5 h-5" />
        更新日志
      </h3>
      <div className="space-y-6">
        {versions.map((release) => (
          <div key={release.version} className="border-l-2 border-blue-600 pl-4 mb-8">
            <div className="flex items-center gap-2 mb-2">
              <h4 className="font-semibold text-xl text-blue-600">{release.version}</h4>
              <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs">{release.type}</span>
              <span className="text-sm text-gray-500">{release.date}</span>
            </div>
            
            {release.features.map((feature, idx) => (
              <div key={idx} className="mb-4">
                <h5 className="font-medium text-gray-800 mb-2">{feature.title}</h5>
                <ul className="space-y-2 text-gray-600">
                  {feature.changes.map((change, changeIdx) => (
                    <li key={changeIdx} className="flex items-start gap-2">
                      <span className="inline-block">•</span>
                      <span>{change}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
};

const DownloadButton = ({ className = '', version }) => {
  const [selectedVersion, setSelectedVersion] = useState(version);

  const getDownloadLink = (ver) => {
    switch (ver) {
      case 'v1.2.0':
        return 'https://github.com/yuqie6/qqmusicdownloader/releases/tag/v1.2.0';
      case 'v1.1.0':
        return 'https://github.com/yuqie6/qqmusicdownloader/releases/tag/v1.1.0';
      case 'v1.0.0':
        return 'https://github.com/yuqie6/qqmusicdownloader/releases/tag/v1.0.0';
      default:
        return 'https://github.com/yuqie6/qqmusicdownloader/releases';
    }
  };
  
  return (
    <div className="flex flex-col items-center gap-4">
      <div className="relative">
        <select 
          className="appearance-none px-6 py-3 pr-12 bg-white text-blue-600 rounded-lg font-semibold 
          hover:bg-blue-50 active:bg-blue-100 transition-colors duration-200 shadow-lg cursor-pointer
          focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={selectedVersion}
          onChange={(e) => setSelectedVersion(e.target.value)}
        >
          <option value="v1.2.0">v1.2.0 - 最新版本</option>
          <option value="v1.1.0">v1.1.0 - 稳定版 </option>
          <option value="v1.0.0">v1.0.0 - 初始版本</option>
        </select>
        <div className="absolute right-3 top-1/2 transform -translate-y-1/2 pointer-events-none">
          <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>
      <a
        href={getDownloadLink(selectedVersion)}
        className={`inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold 
        hover:bg-blue-700 active:bg-blue-800 transition-colors duration-200 ${className}`}
        target="_blank"
        rel="noopener noreferrer"
      >
        <Download className="w-5 h-5 mr-2" />
        立即下载 {selectedVersion}
      </a>
      <p className="text-sm text-gray-500">请选择您需要的版本进行下载</p>
    </div>
  );
};

const LandingPage = () => {
  const [selectedVersion] = useState('v1.2.0');

  return (
    <div className="min-h-screen">
      <Navbar />
      
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
              <DownloadButton version={selectedVersion} />
            </div>
          </div>
        </div>
      </div>

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

      <div id="download" className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-800 mb-6">
              准备好开始了吗？
            </h2>
            <p className="text-gray-600 mb-8 max-w-2xl mx-auto">
              立即下载极简音乐下载器，开启你的音乐之旅。完全免费，无需注册。
            </p>
            <LegalWarning />
            <DownloadButton version={selectedVersion} />
          </div>
          
          <div className="mt-16">
            <Changelog />
          </div>
        </div>
      </div>

      <footer className="bg-gray-800 text-white py-12">
        <div className="container mx-auto px-4">
          <div className="max-w-6xl mx-auto">
            <div className="grid md:grid-cols-2 gap-8">
              <div>
                <h3 className="text-lg font-semibold mb-4">关于我们</h3>
                <p className="text-gray-400">
                  极简音乐下载器致力于为用户提供简单、高效的音乐下载体验。
                  这是一个开源项目，欢迎贡献和反馈。下载文件仅供个人学习使用，
                  不得用于商业用途。作者创作初衷仅为学习交流，请遵守相关法律法规。
                </p>
              </div>
              <div className="md:text-right">
                <h3 className="text-lg font-semibold mb-4">快速链接</h3>
                <div className="flex flex-col md:items-end gap-2">
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