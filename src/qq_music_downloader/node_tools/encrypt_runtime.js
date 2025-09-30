const fs = require('fs');
const path = require('path');
const vm = require('vm');

function loadSource(relativePath) {
  const fullPath = path.resolve(__dirname, relativePath);
  return fs.readFileSync(fullPath, 'utf8');
}

function createSandbox() {
  let cookieStore = '';
  let capturedEncrypt = null;
  let capturedDecrypt = null;
  let capturedSign = null;

  const { TextEncoder, TextDecoder } = require('util');
  const { webcrypto } = require('crypto');

  const sandbox = {
    console,
    window: {},
    navigator: { userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' },
    location: {
      protocol: 'https:',
      host: 'y.qq.com',
      hostname: 'y.qq.com',
      href: 'https://y.qq.com/',
      get origin() {
        return 'https://y.qq.com';
      }
    },
    document: {
      get cookie() {
        return cookieStore;
      },
      set cookie(value) {
        cookieStore = cookieStore ? `${cookieStore}; ${value}` : value;
      },
      createElement(tag = '') {
        const element = {
          tag,
          style: {},
          setAttribute() { },
          appendChild() { },
          remove() { },
          parentNode: { removeChild() { } }
        };

        Object.defineProperty(element, 'src', {
          configurable: true,
          get() {
            return this._src;
          },
          set(value) {
            this._src = value;
            if (typeof value === 'string' && this.onload) {
              this.onload({ type: 'load', target: this });
            }
          }
        });

        Object.defineProperty(element, 'href', {
          configurable: true,
          get() {
            return this._href;
          },
          set(value) {
            this._href = value;
            if (this.tag === 'a' && typeof value === 'string') {
              try {
                const parsed = new URL(value, 'https://y.qq.com');
                this.protocol = parsed.protocol;
                this.host = parsed.host;
                this.hostname = parsed.hostname;
                this.pathname = parsed.pathname;
                this.search = parsed.search;
                this.hash = parsed.hash;
                this.port = parsed.port;
              } catch (err) {
                this.protocol = undefined;
                this.host = undefined;
                this.hostname = undefined;
                this.pathname = undefined;
                this.search = undefined;
                this.hash = undefined;
                this.port = undefined;
              }
            }
            if (this.onload) {
              this.onload({ type: 'load', target: this });
            }
          }
        });

        return element;
      },
      body: {
        appendChild() { },
        removeChild() { }
      },
      getElementsByTagName() {
        return [];
      },
      getElementsByClassName() {
        return [];
      }
    },
    XMLHttpRequest: function () {
      this.responseType = 'text';
      this.headers = {};
      this.open = function () { };
      this.setRequestHeader = function (k, v) {
        this.headers[k] = v;
      };
      this.send = function () {
        if (this.onreadystatechange) {
          this.onreadystatechange();
        }
      };
      this.abort = function () { };
    },
    setTimeout: (fn) => {
      fn();
      return 0;
    },
    clearTimeout: () => { },
    setInterval: (fn) => {
      fn();
      return 0;
    },
    clearInterval: () => { },
    Promise,
    regeneratorRuntime: {},
    performance: {
      now() {
        return Date.now();
      }
    },
    TextEncoder,
    TextDecoder,
    crypto: webcrypto
  };

  sandbox.window = sandbox;
  sandbox.self = sandbox.window;
  sandbox.global = sandbox;
  sandbox.context = {
    window: sandbox.window,
    request: { cookies: {} },
    response: {}
  };
  sandbox.window.document = sandbox.document;
  sandbox.window.navigator = sandbox.navigator;
  sandbox.window.location = sandbox.location;
  sandbox.window.TextEncoder = TextEncoder;
  sandbox.window.TextDecoder = TextDecoder;
  sandbox.window.crypto = webcrypto;
  sandbox.window.addEventListener = function () { };
  sandbox.window.requestAnimationFrame = function (fn) {
    return sandbox.setTimeout(fn, 0);
  };
  sandbox.window.cancelAnimationFrame = function () { };
  sandbox.window.reportCgi = { reportSend() { } };
  sandbox.window.Image = function () {
    return {
      set src(value) {
        if (this.onload) {
          this.onload({ type: 'load', target: { src: value } });
        }
      }
    };
  };

  vm.createContext(sandbox);

  const regeneratorRuntimeSrc = loadSource('regenerator-runtime.js');
  const runtimeSrc = loadSource('runtime.js');
  const vendorSrc = loadSource('vendor.js');
  const encryptHookReplacement =
    'var L=j.__cgiEncrypt,N=j.__cgiDecrypt;' +
    '(function(){' +
    'if(L){' +
    'window.__origCgiEncrypt=L;' +
    'L=function(e){' +
    'window.__latestEncryptPlain=e;' +
    'var r=window.__origCgiEncrypt.call(this,e);' +
    'if(r&&typeof r.then==="function"){return r.then(function(v){window.__latestEncryptOutput=v;return v;});}' +
    'window.__latestEncryptOutput=r;' +
    'return r;' +
    '};' +
    'window.__hookedCgiEncrypt=L;' +
    '}' +
    'if(N){' +
    'window.__origCgiDecrypt=N;' +
    'N=function(e){' +
    'var r=window.__origCgiDecrypt.call(this,e);' +
    'if(r&&typeof r.then==="function"){return r.then(function(v){window.__latestDecryptOutput=v;return v;});}' +
    'window.__latestDecryptOutput=r;' +
    'return r;' +
    '};' +
    'window.__hookedCgiDecrypt=N;' +
    '}' +
    '})();';
  const vendorWithEncryptHook = vendorSrc.replace(
    'var L=j.__cgiEncrypt,N=j.__cgiDecrypt;',
    encryptHookReplacement
  );
  const vendorWithHooks = vendorWithEncryptHook.replace(
    'var P=G._getSecuritySign;',
    'var P=G._getSecuritySign;window.__origGetSecuritySign=P;'
  );

  vm.runInContext(regeneratorRuntimeSrc, sandbox, { filename: 'regenerator-runtime.js' });
  const patchedRuntime = runtimeSrc.replace(
    'd.p="/ryqq/",d.oe',
    'd.p="/ryqq/";window.__webpack_require__=d;window.__webpack_modules__=e;d.oe'
  );
  vm.runInContext(patchedRuntime, sandbox, { filename: 'runtime.js' });
  vm.runInContext(vendorWithHooks, sandbox, { filename: 'vendor.js' });

  const modules = sandbox.window.__webpack_modules__;
  const req = sandbox.window.__webpack_require__;

  if (!modules || !req) {
    throw new Error('无法找到 webpack 运行时内部结构');
  }

  req('8');

  capturedEncrypt =
    sandbox.window.__origCgiEncrypt || sandbox.window.__hookedCgiEncrypt || capturedEncrypt;
  capturedDecrypt =
    sandbox.window.__origCgiDecrypt || sandbox.window.__hookedCgiDecrypt || capturedDecrypt;
  capturedSign = sandbox.window.__origGetSecuritySign || sandbox.window._getSecuritySign || capturedSign;

  if (!capturedEncrypt || !capturedDecrypt || !capturedSign) {
    throw new Error('未能捕获加密/解密函数');
  }

  return {
    encrypt(input) {
      const fn = sandbox.window.__hookedCgiEncrypt || capturedEncrypt;
      return fn.call(sandbox.window, input);
    },
    decrypt: capturedDecrypt,
    sign: capturedSign,
    sandbox,
    getLatestEncryptPlain() {
      return sandbox.window.__latestEncryptPlain;
    },
    getLatestEncryptOutput() {
      return sandbox.window.__latestEncryptOutput;
    },
    getLatestDecryptOutput() {
      return sandbox.window.__latestDecryptOutput;
    }
  };
}

const {
  encrypt,
  decrypt,
  sign,
  sandbox,
  getLatestEncryptPlain,
  getLatestEncryptOutput,
  getLatestDecryptOutput
} = createSandbox();

module.exports = {
  encrypt,
  decrypt,
  sign,
  sandbox,
  getLatestEncryptPlain,
  getLatestEncryptOutput,
  getLatestDecryptOutput
};
