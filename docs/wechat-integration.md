# 微信公众号接入核验

核验日期：2026-09-27。当前状态：**未连接个人微信关注列表，未读取微信聊天或数据库，未安装或初始化微信 CLI**。

## 本机实际结果

- `uname -sm`：Darwin arm64。
- `/Applications/WeChat.app/Contents/Info.plist`：WeChat 4.1.13。
- `command -v wx wechat-cli wechat mp-weixin-cli wewe-rss`：均未发现。
- 已有 Node/npm/Homebrew；未发现 Docker 或 Podman。
- `npm list -g --depth=0`：现有全局包为 `@larksuite/cli@1.0.95`、`lark-channel-bridge@0.7.1`。
- `npm view @jackwener/wx-cli version scripts bin dist.integrity --json`：registry 存在 0.3.0；包含 `postinstall: node install.js`。此检查未执行安装脚本。

## 三种能力不要混淆

| 能力 | 当前可行入口 | 边界 |
|---|---|---|
| 自动取得个人微信关注公众号清单 | 尚无在本机验证成功的接入 | 公众号运营者 CLI 的 AppID/API 不等于个人订阅列表接口 |
| 读取已知文章 | 提供 `mp.weixin.qq.com` 公开文章链接，进入 URL 输入队列 | 可能遇到登录、验证码或删除；失败应记录为 unavailable，不生成伪摘要 |
| 持续订阅选定公众号 | 已有 RSS 地址，或后续部署经过验证的公众号 RSS 服务 | 订阅源需显式添加；不能宣称自动同步个人微信全部关注 |

## 已核验的候选

### wx-cli：暂不初始化

[项目地址](https://github.com/jackwener/wx-cli) 的 Web 读取本次返回 451；原始 main README 返回 404。搜索索引存在 `biz-articles` 功能描述，但不能据此声称当前源码、4.1.13兼容性或初始化步骤已经验证。npm 包仍存在，参见 [发布者页面](https://www.npmjs.com/~jackwener)。

此路线应在取得可审查的当前官方源码与安装说明后再评估。本次没有执行 `wx init`、内存扫描、数据库密钥提取、微信重签名、系统隐私权限重置或 SIP 修改。仅安装一个二进制并不能打通订阅列表。

### WeWe RSS：不选为新部署默认项

[原仓库](https://github.com/cooderl/wewe-rss) 已于 2026-05-11 归档。其 README 说明需要扫码登录微信读书、手工添加公众号文章分享链接，并有部分请求通过第三方服务转发。本次未安装、未登录。

### WeRSS：可继续评估的 RSS 适配服务

[WeRSS 仓库](https://github.com/rachelos/we-mp-rss) 提供公众号订阅和 RSS。其 [weread_mp 模式官方说明](https://github.com/rachelos/we-mp-rss/blob/main/docs/weread-mp.md) 明确：请求直接到微信读书；需要用户登录后的会话；每个公众号只返回最新一篇，不能回补历史列表。配置与登录尚未执行，Mac 本机兼容性未实测。

如采用该路线：先部署到本机环回地址，在本地管理页由用户完成登录；会话只保存在本地受限配置，不粘贴到聊天、代码仓库或日志。订阅选定公众号后，将实际生成的 RSS URL 填入本系统。认证失效时标记 `needs_login` 并通知，避免反复重试。

## 与信息流水线的接口

首版入口接受两种已存在的数据，不依赖微信私有数据库：

1. `article_url`：单篇文章链接。优先从用户提供链接、授权飞书群里的分享链接提取。
2. `rss_url`：实际可访问的订阅地址。采集器保留文章 URL、标题、作者/公众号、发布时间、提取状态与内容哈希。

公众号文章作为发现线索。模型效果、真实机器人实验和理论结论须继续追溯论文、项目代码或原始实验报告；公众号宣传不自动视为技术证据。

验收应分开记录 `installed`、`authenticated`、`subscriptions_discovered`、`articles_fetched`。目前四项均未完成；本文件是接入核验与后续路径，不是接入成功证明。
