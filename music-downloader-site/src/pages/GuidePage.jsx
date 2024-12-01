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
            <li>首次使用时请确保联网</li>
            <li>建议使用最新版本以获得最佳体验</li>
            <li>如遇到问题，可以查看常见问题解答或联系我们获取帮助</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

// FAQPage.jsx
const FAQItem = ({ question, answer }) => (
  <div className="border-b border-gray-200 last:border-0">
    <details className="group p-6">
      <summary className="flex justify-between items-center cursor-pointer list-none">
        <span className="text-lg font-semibold text-gray-800">{question}</span>
        <span className="text-blue-600 group-open:rotate-180 transition-transform">
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </span>
      </summary>
      <p className="mt-4 text-gray-600">{answer}</p>
    </details>
  </div>
);

const FAQPage = () => {
  const faqs = [
    {
      question: "软件安装后打不开怎么办？",
      answer: "请检查是否有杀毒软件拦截了程序的运行。您可以将极简音乐下载器添加到杀毒软件的白名单中。如果问题仍然存在，请尝试以管理员身份运行程序。"
    },
    {
      question: "为什么有些音乐无法下载？",
      answer: "这可能是因为音乐版权的限制。我们会持续优化软件，以提供更好的下载体验。您也可以尝试搜索该歌曲的其他版本。"
    },
    {
      question: "下载的音乐保存在哪里？",
      answer: "默认情况下，下载的音乐文件会保存在桌面的QQMusic文件夹中。。"
    },
    {
      question: "软件完全免费吗？",
      answer: "是的，极简音乐下载器完全免费，没有任何隐藏收费。我们承诺为用户提供免费且优质的服务。"
    },
    {
        question: "程序安装在哪？",
        answer: "由于作者水平有限，目前程序安装在C盘，后续会优化"
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50 pt-20">
      <div className="container mx-auto px-4 py-8">
        <Link to="/" className="inline-flex items-center text-blue-600 hover:text-blue-700 mb-8">
          <ArrowLeft className="w-5 h-5 mr-2" />
          返回首页
        </Link>
        
        <h1 className="text-4xl font-bold text-gray-800 mb-8">常见问题</h1>
        
        <div className="max-w-3xl bg-white rounded-lg shadow-sm">
          {faqs.map((faq, index) => (
            <FAQItem key={index} {...faq} />
          ))}
        </div>
      </div>
    </div>
  );
};

// ContactPage.jsx
const ContactPage = () => {
  return (
    <div className="min-h-screen bg-gray-50 pt-20">
      <div className="container mx-auto px-4 py-8">
        <Link to="/" className="inline-flex items-center text-blue-600 hover:text-blue-700 mb-8">
          <ArrowLeft className="w-5 h-5 mr-2" />
          返回首页
        </Link>
        
        <h1 className="text-4xl font-bold text-gray-800 mb-8">联系我们</h1>
        
        <div className="max-w-3xl">
          <div className="bg-white rounded-lg shadow-sm p-8">
            <div className="space-y-6">
              <div>
                <h2 className="text-2xl font-semibold text-gray-800 mb-4">联系方式</h2>
                <p className="text-gray-600">
                  如果您在使用过程中遇到任何问题，或者有任何建议和反馈，欢迎通过以下方式联系我们：
                </p>
              </div>
              
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <svg className="w-6 h-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                  <span className="text-gray-600">邮箱：2140354088@qq.com</span>
                </div>
                
                <div className="flex items-center gap-3">
                  <svg className="w-6 h-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a1.994 1.994 0 01-1.414-.586m0 0L11 14h4a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2v4l.586-.586z" />
                  </svg>
                  <span className="text-gray-600">GitHub Issues: 欢迎在我们的GitHub仓库提交问题</span>
                </div>
              </div>
              
              <div className="pt-6 border-t border-gray-200">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">反馈建议</h3>
                <p className="text-gray-600">
                  我们非常重视用户的反馈和建议。如果您有任何想法或建议，都可以通过上述方式与我们取得联系。
                  我们会认真考虑每一条反馈，并在后续的版本中不断改进和优化。
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GuidePage;