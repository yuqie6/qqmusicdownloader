import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, Github, Mail } from 'lucide-react';

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
            <div className="space-y-8">
              <div>
                <h2 className="text-2xl font-semibold text-gray-800 mb-4">欢迎联系</h2>
                <p className="text-gray-600">
                  无论您有任何问题、建议或者想法，我们都非常期待听到您的声音！
                  您的反馈是我们持续改进的动力。
                </p>
              </div>
              
              <div className="space-y-6">
                <a
                  href="https://github.com/yuqie6/qqmusicdownloader/issues"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <Github className="w-6 h-6 text-blue-600" />
                  <div>
                    <h3 className="text-lg font-semibold text-gray-800">GitHub Issues</h3>
                    <p className="text-gray-600">报告问题或提出建议</p>
                  </div>
                </a>
                
                <a
                  href="mailto:yuqie6@gmail.com"
                  className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <Mail className="w-6 h-6 text-blue-600" />
                  <div>
                    <h3 className="text-lg font-semibold text-gray-800">电子邮件</h3>
                    <p className="text-gray-600">2140354088@qq.com</p>
                  </div>
                </a>
                
              </div>
              
              <div className="pt-6 border-t border-gray-200">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">开源协作</h3>
                <p className="text-gray-600">
                  我们是一个开源项目，欢迎所有形式的贡献！如果您对开发感兴趣，
                  可以在GitHub上fork我们的项目，提交pull request，或者参与讨论。
                  让我们一起把这个工具做得更好！
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ContactPage;