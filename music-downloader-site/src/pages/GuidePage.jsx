// GuidePage.jsx
import React from 'react';
import { ArrowLeft, PlayCircle, Download, Search } from 'lucide-react';
import { Link } from 'react-router-dom';

const GuideStep = ({ number, title, description, icon }) => (
  <div className="flex gap-4 p-6 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow">
    <div className="flex-shrink-0 w-8 h-8 flex items-center justify-center rounded-full bg-blue-100 text-blue-600 font-semibold">
      {number}
    </div>
    <div>
      <div className="flex items-center gap-2 mb-2">
        {icon}
        <h3 className="text-xl font-semibold text-gray-800">{title}</h3>
      </div>
      <p className="text-gray-600">{description}</p>
    </div>
  </div>
);

const GuidePage = () => {
  return (
    <div className="min-h-screen bg-gray-50 pt-20">
      <div className="container mx-auto px-4 py-8">
        <Link to="/" className="inline-flex items-center text-blue-600 hover:text-blue-700 mb-8">
          <ArrowLeft className="w-5 h-5 mr-2" />
          返回首页
        </Link>
        
        <h1 className="text-4xl font-bold text-gray-800 mb-8">使用教程</h1>
        
        <div className="space-y-6 max-w-3xl">
          <GuideStep
            number="1"
            title="下载并安装"
            description="从官网下载最新版本的极简音乐下载器，双击安装包进行安装。安装过程中如果遇到杀毒软件提示，请允许程序的运行权限。"
            icon={<Download className="w-6 h-6 text-blue-600" />}
          />
          
          <GuideStep
            number="2"
            title="搜索音乐"
            description="打开软件后，在搜索框中输入想要下载的歌曲名称或歌手名，点击搜索按钮进行搜索。"
            icon={<Search className="w-6 h-6 text-blue-600" />}
          />
          
          <GuideStep
            number="3"
            title="开始下载"
            description="在搜索结果中找到想要下载的歌曲，点击下载按钮即可开始下载。下载完成后的音乐文件将保存在桌面‘QQMusic’文件夹中。"
            icon={<PlayCircle className="w-6 h-6 text-blue-600" />}
          />
        </div>
        
        <div className="mt-12 p-6 bg-blue-50 rounded-lg">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">温馨提示</h2>
          <ul className="list-disc list-inside text-gray-600 space-y-2">
            <li>使用时请确保联网</li>
            <li>建议使用最新版本以获得最佳体验</li>
            <li>如遇到问题，可以查看常见问题解答或联系我们获取帮助</li>
          </ul>
        </div>
      </div>
    </div>
  );
};



export default GuidePage;