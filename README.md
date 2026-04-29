# 🤖 AI 每日简报 Agent

每天早上自动抓取 AI 资讯，经 Kimi AI 智能筛选总结后，推送到你的飞书群。

---

## ✨ 效果预览

飞书群每天会收到一条精美卡片消息，包含：
- **5-8 条精选 AI 动态**（已去重分类）
- 四大分类：【前沿研究】【产品动态】【开源项目】【行业观点】
- 一句话中文摘要 + 原文链接
- 💡 **今日观察**（趋势总结）

---

## 🚀 5 分钟部署指南（无需写代码）

### 第一步：准备两个「钥匙」

#### 1. Kimi API Key（AI 总结用）
1. 打开 [platform.moonshot.cn](https://platform.moonshot.cn)
2. 注册/登录账号
3. 进入「API Key 管理」→「创建 API Key」
4. 复制生成的 Key（以 `sk-` 开头），**先保存在记事本里**

> 💡 新用户有免费额度，每天运行一次够用几个月。

#### 2. 飞书 Webhook 地址（推送用）
1. 打开你想接收简报的**飞书群**
2. 点击群设置 →「群机器人」→「添加机器人」
3. 选择「自定义机器人」
4. 给机器人起个名字（如「AI 简报」），点击「添加」
5. 复制 **Webhook 地址**（如 `https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxx`）
6. **先保存在记事本里**

> 安全设置可以先不管，后续如需加关键词可配置为「简报」。

---

### 第二步：在 GitHub 上创建仓库

1. 打开 [github.com/new](https://github.com/new) 创建一个新仓库
   - 仓库名：`ai-daily-briefing`
   - 勾选「Add a README file」
   - 点击「Create repository」

2. **上传代码文件**：
   - 在本项目文件夹里，找到 `main.py`
   - 在 GitHub 仓库页面点击「Add file」→「Upload files」
   - 把 `main.py` 拖进去上传
   - 再点击「Add file」→「Create new file」
   - **文件名输入**：`.github/workflows/daily.yml`（输入这个路径会自动创建文件夹）
   - 把本项目的 `daily.yml` 内容复制粘贴进去
   - 点击「Commit changes」

3. **配置密钥**（最关键的一步）：
   - 在你的仓库页面，点击顶部「Settings」
   - 左侧找到「Secrets and variables」→「Actions」
   - 点击「New repository secret」
   - 添加第一个：Name 填 `KIMI_API_KEY`，Secret 填你的 Kimi API Key
   - 再点击「New repository secret」
   - 添加第二个：Name 填 `FEISHU_WEBHOOK_URL`，Secret 填你的飞书 Webhook 地址

---

### 第三步：手动测试运行

1. 在你的仓库页面点击顶部「Actions」
2. 左侧 workflows 列表里选择「AI Daily Briefing」
3. 点击右侧绿色按钮「Run workflow」→「Run workflow」
4. 等待 1-2 分钟，去你的飞书群里查看是否收到消息 🎉

如果收到消息，说明一切正常！

---

### 第四步：坐等每日推送

GitHub Actions 已设置为**每天早上 9 点（北京时间）**自动运行。

只要 GitHub 服务正常，你的飞书群就会每天准时收到简报，完全无需维护。

---

## 🛠 进阶：自定义资讯源

如果你想增加或修改 RSS 源，编辑仓库里的 `main.py`，找到 `SOURCES` 列表即可：

```python
SOURCES = [
    {
        "name": "显示名称",
        "url": "RSS地址",
        "lang": "zh",  # 或 "en"
    },
    # ...
]
```

修改后提交即可生效。

---

## ❓ 常见问题

**Q: 飞书没收到消息怎么办？**
- 去 GitHub 仓库的「Actions」页面查看运行记录
- 如果有红色 ❌，点击进去看报错信息
- 常见原因：API Key 填错了、Webhook 地址填错了、网络超时重试即可

**Q: 可以修改推送时间吗？**
- 可以。编辑 `.github/workflows/daily.yml` 里的 `cron` 表达式：
  - 早 8 点：`cron: "0 0 * * *"`
  - 早 9 点 + 晚 6 点：`cron: "0 1,10 * * *"`

**Q: 可以在本地电脑测试吗？**
- 可以。打开 Mac 终端，进入本项目文件夹，执行：
  ```bash
  export KIMI_API_KEY="sk-你的Key"
  export FEISHU_WEBHOOK_URL="https://open.feishu.cn/..."
  pip3 install requests feedparser
  python3 main.py
  ```

---

## 📡 默认资讯源说明

| 来源 | 语言 | 内容特点 |
|------|------|----------|
| **机器之心** | 中文 | 国内头部 AI 媒体，覆盖论文、产品、行业 |
| **量子位** | 中文 | 国内 AI 媒体，偏产品和商业 |
| **Hugging Face** | 英文 | 开源模型、工具、论文更新 |
| **TechCrunch AI** | 英文 | 海外 AI 产品发布、融资新闻 |
| **Hacker News** | 英文 | 工程师社区讨论的 AI 热点 |

---

Made with ❤️ by Kimi
