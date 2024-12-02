import React from 'react';
import { ArrowLeft, Download, Search, Cookie, Music, MousePointerClick, Chrome } from 'lucide-react';
import { Link } from 'react-router-dom';

const GuideStep = ({ number, title, description, icon, children }) => (
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
      {children}
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
            title="获取 Cookie"
            description="在使用之前，我们需要先获取你的 QQ音乐 VIP 账号 cookie："
            icon={<Cookie className="w-6 h-6 text-blue-600" />}
          >
            <div className="mt-4 space-y-2 bg-gray-50 p-4 rounded-lg text-sm">
              <p className="font-medium text-gray-700">获取 Cookie 步骤：</p>
              <ol className="list-decimal list-inside space-y-2 text-gray-600">
                <li>使用 Chrome 或 Edge 浏览器打开 QQ音乐官网 (y.qq.com)</li>
                <li>登录你的 QQ音乐 VIP 账号</li>
                <li>在页面任意位置点击右键，选择"检查"或按 F12 打开开发者工具</li>
                <li>在开发者工具中点击"网络/Network"选项卡</li>
                <li>在网页中随便点击一首歌</li>
                <li>在开发者工具的网络面板中找到以 fcg 开头的请求</li>
                <li>点击该请求，在右侧找到"请求标头/Headers"中的"Cookie"字段</li>
                <li>复制整个 Cookie 内容（通常以 uin= 开头）</li>
              </ol>
            </div>
          </GuideStep>
          
          <GuideStep
            number="2"
            title="输入 Cookie"
            description="将复制的 Cookie 粘贴到软件的 Cookie 输入框中。别担心，这些信息都存储在本地，完全开源透明，作者也看不见哦！"
            icon={<Chrome className="w-6 h-6 text-blue-600" />}
          />
          
          <GuideStep
            number="3"
            title="搜索音乐"
            description="在搜索框中输入你想找的歌曲或歌手名称，让音乐来找你。"
            icon={<Search className="w-6 h-6 text-blue-600" />}
          />
          
          <GuideStep
            number="4"
            title="浏览结果"
            description="点击搜索后，浏览搜索结果列表，找到你心仪的音乐。"
            icon={<Music className="w-6 h-6 text-blue-600" />}
          />

          <GuideStep
            number="5"
            title="选择歌曲"
            description="在列表中找到你想要的歌曲，确认歌手和版本是否正确。"
            icon={<MousePointerClick className="w-6 h-6 text-blue-600" />}
          />
          
          <GuideStep
            number="6"
            title="一键下载"
            description="选好歌曲后，只需点击下载按钮，就能将音乐收入囊中，就这么简单！下载的音乐文件将保存在桌面'QQMusic'文件夹中。"
            icon={<Download className="w-6 h-6 text-blue-600" />}
          />
        </div>
        
        <div className="mt-12 p-6 bg-blue-50 rounded-lg">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">温馨提示</h2>
          <ul className="list-disc list-inside text-gray-600 space-y-2">
            <li>使用时请确保网络连接正常</li>
            <li>建议使用最新版本以获得最佳体验</li>
            <li>Cookie 信息仅保存在本地，请放心使用</li>
            <li>Cookie 有效期通常为1-2周，过期后需要重新获取</li>
            <li>如遇到问题，可以查看常见问题解答或联系我们获取帮助</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default GuidePage;