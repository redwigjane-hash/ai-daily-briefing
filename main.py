  #!/usr/bin/env python3
  # -*- coding: utf-8 -*-
  """
  AI 每日简报 Agent
  自动抓取 RSS 源，通过 Kimi AI 总结，推送到飞书。
  """

  import os
  import re
  from datetime import datetime, timezone, timedelta

  import requests
  import feedparser


  # ==================== 配置区域 ====================

  KIMI_API_KEY = os.getenv("KIMI_API_KEY")
  FEISHU_WEBHOOK_URL = os.getenv("FEISHU_WEBHOOK_URL")

  # RSS 资讯源列表
  SOURCES = [
      {
          "name": "机器之心",
          "url": "https://www.jiqizhixin.com/rss",
          "lang": "zh",
      },
      {
          "name": "量子位",
          "url": "https://www.qbitai.com/feed",
          "lang": "zh",
      },
      {
          "name": "Hugging Face",
          "url": "https://huggingface.co/blog/feed.xml",
          "lang": "en",
      },
      {
          "name": "TechCrunch AI",
          "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
          "lang": "en",
      },
      {
          "name": "Hacker News",
          "url": "https://hnrss.org/newest?q=AI+OR+LLM+OR+GPT+OR+Claude+OR+OpenAI",
          "lang": "en",
      },
  ]

  # 每个源最多抓取前几篇文章
  MAX_PER_SOURCE = 5
  # 抓取最近几天的文章（容错）
  DAYS_BACK = 2


  # ==================== 工具函数 ====================

  def clean_html(raw_html: str) -> str:
      """移除 HTML 标签"""
      if not raw_html:
          return ""
      clean = re.sub(r"<[^>]+>", "", raw_html)
      return clean.replace("&nbsp;", " ").strip()


  def fetch_articles():
      """从所有 RSS 源抓取文章"""
      articles = []
      cutoff = datetime.now(timezone.utc) - timedelta(days=DAYS_BACK)

      for source in SOURCES:
          try:
              print(f"正在抓取: {source['name']} ...")
              fp = feedparser.parse(source["url"])

              for entry in fp.entries[:MAX_PER_SOURCE]:
                  # 解析发布时间
                  if hasattr(entry, "published_parsed") and entry.published_parsed:
                      pub = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                  elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                      pub = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
                  else:
                      pub = datetime.now(timezone.utc)  # 无法解析则保留

                  # 跳过太旧的文章
                  if pub < cutoff:
                      continue

                  title = getattr(entry, "title", "无标题")
                  link = getattr(entry, "link", "")
                  summary = clean_html(
                      getattr(entry, "summary", "") or getattr(entry, "description", "")
                  )

                  articles.append({
                      "title": title,
                      "link": link,
                      "summary": summary[:400],
                      "source": source["name"],
                      "lang": source["lang"],
                  })

          except Exception as e:
              print(f"[WARN] {source['name']} 抓取失败: {e}")

      # 去重（基于链接）
      seen = set()
      unique = []
      for a in articles:
          if a["link"] and a["link"] not in seen:
              seen.add(a["link"])
              unique.append(a)

      print(f"共抓取 {len(unique)} 篇 unique 文章")
      return unique


  def summarize(articles):
      """调用 Kimi API 生成简报"""
      if not KIMI_API_KEY:
          raise ValueError("缺少环境变量 KIMI_API_KEY")

      # 构建输入文本
      lines = []
      for idx, a in enumerate(articles, 1):
          lines.append(
              f"{idx}. 来源：{a['source']}({a['lang']})\n"
              f"标题：{a['title']}\n"
              f"链接：{a['link']}\n"
              f"摘要：{a['summary']}\n"
          )
      content = "\n".join(lines)

      system_prompt = (
          "你是一位资深的 AI 行业编辑，负责整理每日 AI 简报。\n"
          "任务要求：\n"
          "1. 从以下文章中筛选出 5-8 条最值得关注的动态（去重，合并相似报道）。\n"
          "2. 按以下分类标注：【前沿研究】【产品动态】【开源项目】【行业观点】。\n"
          "3. 输出格式（严格遵循，每条一行）：\n"
          '   - **[分类]** [标题](链接) —— 一句话中文摘要（30字以内）\n'
          "   - 英文标题请保留原文，括号内可补充中文关键词。\n"
          "4. 最后添加一段「💡 今日观察」（2-3句话总结今日趋势）。\n"
          "5. 总字数控制在 1500 字以内，只输出 Markdown，不要任何额外解释。"
      )

      resp = requests.post(
          "https://api.moonshot.cn/v1/chat/completions",
          headers={
              "Authorization": f"Bearer {KIMI_API_KEY}",
              "Content-Type": "application/json",
          },
          json={
              "model": "moonshot-v1-8k",
              "messages": [
                  {"role": "system", "content": system_prompt},
                  {"role": "user", "content": content},
              ],
              "temperature": 0.3,
              "max_tokens": 2048,
          },
          timeout=120,
      )
      resp.raise_for_status()
      result = resp.json()["choices"][0]["message"]["content"]
      return result


  def send_to_feishu(markdown_text: str):
      """发送飞书卡片消息"""
      if not FEISHU_WEBHOOK_URL:
          raise ValueError("缺少环境变量 FEISHU_WEBHOOK_URL")

      today = datetime.now().strftime("%Y-%m-%d")

      payload = {
          "msg_type": "interactive",
          "card": {
              "config": {"wide_screen_mode": True},
              "header": {
                  "title": {"tag": "plain_text", "content": f"🚀 AI 每日简报 | {today}"},
                  "template": "blue",
              },
              "elements": [
                  {
                      "tag": "div",
                      "text": {
                          "tag": "lark_md",
                          "content": markdown_text,
                      },
                  },
                  {"tag": "hr"},
                  {
                      "tag": "note",
                      "elements": [
                          {
                              "tag": "plain_text",
                              "content": "🤖 由 Kimi AI 自动整理 | 来源：机器之心、量子位、Hugging Face、TechCrunch 等",
                          }
                      ],
                  },
              ],
          },
      }

      r = requests.post(FEISHU_WEBHOOK_URL, json=payload, timeout=30)
      r.raise_for_status()
      data = r.json()
      if data.get("code") != 0:
          raise RuntimeError(f"飞书推送失败: {data}")
      print("✅ 飞书推送成功")


  # ==================== 主流程 ====================

  def main():
      print("=" * 40)
      print("AI 每日简报 Agent 开始运行")
      print("=" * 40)

      articles = fetch_articles()
      if not articles:
          print("⚠️ 未抓取到任何文章，跳过本次推送。")
          return

      print("正在调用 Kimi AI 总结...")
      summary = summarize(articles)

      print("正在推送至飞书...")
      send_to_feishu(summary)

      print("✅ 全部完成！")


  if __name__ == "__main__":
      main()
