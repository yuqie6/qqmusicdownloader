// FAQPage.jsx
import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';

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
      question: "软件安全吗？为什么杀毒软件会报警？",
      answer: "我们的软件完全安全！由于软件需要访问网络和下载功能，某些杀毒软件可能会误报。您可以放心地将其添加到杀毒软件的白名单中。我们的源代码完全开源，您可以在GitHub上查看。"
    },
    {
      question: "下载的音乐在哪里？",
      answer: "默认情况下，音乐会下载到您的桌面‘QQMusic’文件夹中。您可以在软件中找到下载好的音乐文件。作者在1.2.0版本中添加了下载到指定文件夹的功能。"
    },
    {
      question: "音乐无法下载怎么办？",
      answer: "如果遇到下载问题，请检查：1. 网络连接是否正常；2. 是否有足够的磁盘空间；3. 杀毒软件是否拦截了下载。如果问题依然存在，可以在GitHub上提交issue，作者会及时处理。"
    },
    {
      question: "为什么选择开源？",
      answer: "作者选择开源是因为相信透明和共享能创造更好的软件。这不仅让用户可以验证软件的安全性，也欢迎社区贡献，一起让这个工具变得更好。"
    },
    {
      question: "为什么无法获取高音质音乐",
      answer: "受限于QQ音乐API，我们无法提供高音质音乐。您可以尝试使用其他音乐下载软件或使用其他音乐源。"
    },
    {
        question: "软件安装在哪？",
        answer: "由于作者水平有限，目前程序安装在C盘，后续会优化"
    },
    {
      question: "为什么软件界面这么难看？",
      answer: "作者只是个大一学生，界面设计能力有限，后续会改进"
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

        <div className="mt-12 p-6 bg-blue-50 rounded-lg max-w-3xl">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">还有问题？</h2>
          <p className="text-gray-600 mb-4">
            如果这里没有解答您的问题，欢迎通过以下方式联系作者：
          </p>
          <Link 
            to="/contact"
            className="text-blue-600 hover:text-blue-700 font-semibold inline-flex items-center"
          >
            联系我们
            <ArrowLeft className="w-4 h-4 ml-2 rotate-180" />
          </Link>
        </div>
      </div>
    </div>
  );
};
export default FAQPage;


