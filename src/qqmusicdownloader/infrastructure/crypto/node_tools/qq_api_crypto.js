#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const readline = require('readline');

const { encrypt, decrypt, sign } = require('./encrypt_runtime');

function readText(filePath) {
  return fs.readFileSync(path.resolve(filePath), 'utf8');
}

function readBinary(filePath) {
  return fs.readFileSync(path.resolve(filePath));
}

function writeText(filePath, content) {
  fs.writeFileSync(path.resolve(filePath), content, 'utf8');
}

function writeJson(filePath, obj) {
  fs.writeFileSync(path.resolve(filePath), JSON.stringify(obj, null, 2), 'utf8');
}

function printUsage() {
  console.log('用法:');
  console.log('  node qq_api_crypto.js --encrypt <plain.json> [--out-body <body.txt>] [--out-sign <sign.txt>]');
  console.log('  node qq_api_crypto.js --decrypt <response.bin> [--out-json <decoded.json>]');
  console.log('  node qq_api_crypto.js --server  # 启动长驻进程, 通过 stdin/stdout 处理请求');
}

function respond(message) {
  const text = JSON.stringify(message);
  console.log(text);
  return text;
}

async function handleServerRequest(payload) {
  if (!payload || typeof payload.action !== 'string') {
    return { ok: false, error: '缺少 action 字段' };
  }

  try {
    if (payload.action === 'encrypt') {
      if (typeof payload.plain !== 'string') {
        throw new Error('encrypt 需要 plain 字符串');
      }
      const signature = sign(payload.plain);
      const encrypted = await encrypt(payload.plain);
      return { ok: true, data: { sign: signature, body: encrypted } };
    }

    if (payload.action === 'decrypt') {
      if (typeof payload.base64 !== 'string') {
        throw new Error('decrypt 需要 base64 字符串');
      }
      const binary = Buffer.from(payload.base64, 'base64');
      const decodedText = await decrypt(new Uint8Array(binary).buffer);
      let parsed = null;
      try {
        parsed = JSON.parse(decodedText);
      } catch (err) {
        parsed = null;
      }
      return { ok: true, data: { text: decodedText, json: parsed } };
    }

    throw new Error(`未知 action: ${payload.action}`);
  } catch (err) {
    return { ok: false, error: err && err.message ? err.message : String(err) };
  }
}

function startServer() {
  const rl = readline.createInterface({ input: process.stdin, crlfDelay: Infinity });
  rl.on('line', (line) => {
    if (!line.trim()) {
      return;
    }

    let payload;
    try {
      payload = JSON.parse(line);
    } catch (err) {
      respond({ ok: false, error: `JSON 解析失败: ${line}` });
      return;
    }

    handleServerRequest(payload)
      .then((message) => respond(message))
      .catch((err) => {
        respond({ ok: false, error: err && err.message ? err.message : String(err) });
      });
  });

  rl.on('close', () => {
    process.exit(0);
  });
}

async function handleEncrypt(args, options) {
  const fileIndex = args.indexOf('--encrypt');
  const inputPath = args[fileIndex + 1];
  if (!inputPath) {
    throw new Error('请提供待加密的 JSON 文件路径');
  }

  const payload = readText(inputPath).trim();
  const signature = sign(payload);
  const encrypted = await encrypt(payload);

  const bodyOutIndex = args.indexOf('--out-body');
  if (bodyOutIndex !== -1 && args[bodyOutIndex + 1]) {
    writeText(args[bodyOutIndex + 1], encrypted);
  }

  const signOutIndex = args.indexOf('--out-sign');
  if (signOutIndex !== -1 && args[signOutIndex + 1]) {
    writeText(args[signOutIndex + 1], signature);
  }

  if (options.outputJson) {
    const result = {
      sign: signature,
      body: encrypted,
      plain: payload
    };
    console.log(JSON.stringify(result));
    return;
  }

  console.log('加密完成:');
  console.log('  sign:', signature);
  console.log('  body(base64) 前 80 字符:', encrypted.slice(0, 80));
  console.log('  body(base64) 长度:', encrypted.length);
}

async function handleDecrypt(args, options) {
  const fileIndex = args.indexOf('--decrypt');
  const inputPath = args[fileIndex + 1];
  if (!inputPath) {
    throw new Error('请提供响应二进制文件路径');
  }

  const binary = readBinary(inputPath);
  const decodedText = await decrypt(new Uint8Array(binary).buffer);
  let parsed;
  try {
    parsed = JSON.parse(decodedText);
  } catch (err) {
    parsed = null;
  }

  const outIndex = args.indexOf('--out-json');
  if (parsed && outIndex !== -1 && args[outIndex + 1]) {
    writeJson(args[outIndex + 1], parsed);
  }

  if (options.outputJson) {
    const result = {
      text: decodedText,
      json: parsed
    };
    console.log(JSON.stringify(result));
    return;
  }

  console.log('解密完成:');
  console.log('  文本前 80 字符:', decodedText.slice(0, 80));
  if (parsed) {
    console.log('  JSON 顶层键:', Object.keys(parsed));
  } else {
    console.log('  无法直接解析为 JSON');
  }
}

async function main() {
  const args = process.argv.slice(2);
  if (args.includes('--server')) {
    startServer();
    return;
  }

  if (args.length === 0 || (!args.includes('--encrypt') && !args.includes('--decrypt'))) {
    printUsage();
    process.exit(1);
  }

  const options = {
    outputJson: args.includes('--json')
  };

  if (args.includes('--encrypt')) {
    await handleEncrypt(args, options);
  }

  if (args.includes('--decrypt')) {
    await handleDecrypt(args, options);
  }
}

main().catch((err) => {
  console.error('执行失败:', err);
  process.exit(1);
});
