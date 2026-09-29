# 时光小屋：粒子世界具身进展简报

本地可运行的采集、增量去重、证据审核和飞书机器人简报原型。编辑面向粒子世界全公司（含CEO）的决策需要；自2026-09-28起在“PW产研组”做每日内部测试，私聊测试为另一独立目标。运行环境：Python 3标准库、已授权的lark-cli。私有配置、群聊缓存、认知档案与简报均排除在Git之外。

## 运行

完整端到端标准见[简报 SOP](docs/briefing-sop.md)，包含四路信息覆盖（学术、产业同行、工业场景、相关前沿科学）、工作认知、微信筛选、PR校准、动态模型调度、写作、投递及故障处理；具体运行协议见[agent-workflow](docs/agent-workflow.md)。细粒度来源与技术分类见[检索地图](docs/discovery-map.md)，仅供后台使用，不进入简报正文。四路都要检查，但不按类别凑条数。

可复用入口为仓库内的[particle-work-briefing skill](skills/particle-work-briefing/SKILL.md)，显式调用`$particle-work-briefing`。本机另有已安装的同名技能；仓库版本以相对路径引用本项目，便于在其他检出目录安装。安装技能不等于开启定时任务。

```bash
python3 -m unittest discover -s tests -v
python3 pipeline.py collect
# 由agent按docs/agent-workflow.md审阅新增证据，更新context-delta/reviewed-items/editorial-brief
python3 pipeline.py render
python3 pipeline.py prepare-publish
# 审核预览后，以用户已确认的CLI机器人向本人私聊发送
python3 pipeline.py publish-chat
```

用户已确认更换发送者。私聊用`publish-chat`，每日群聊用`publish-group`；均固定CLI应用profile并显式采用bot身份，不使用旧工作伙伴会话。`state/publish-ledger.json`按目标和正文哈希防止误发；`state/reported-events.json`另用于跨期选题去重。2026-09-28首次群发已取得回执，当前仍是临时本地定时运行，不是云端部署。Aily原生发送仅保留为历史验证，不代表CLI机器人会更新工作伙伴记忆。

## 配置与产物

- `config/private.json`：只读群范围、Wiki链接、用户ID、核实后的发布会话；不保存密钥。
- `config/focus.json`：可直接编辑的关注方向、技术路线、topic、商业问题与优先级；`rss_topic_patterns`同时驱动脚本的RSS候选初筛。未确认的公司商业模式和候选场景单独标记，不当作既定战略。
- `config/sources.json`：arXiv公开RSS、来源清单、四路检索规则、跨期内容去重政策、时间范围和分页预算。`state/reported-events.json`保存已送达简报的选题历史；`docs/discovery-map.md`扩充候选来源与细粒度技术轴，候选入口不代表脚本已接通新闻订阅。
- `state/raw/`：完整原始读取响应，含私有资料，限本地使用。
- `state/packet.json`：最近一次增量；`state/evidence-queue.json`保留尚待处理的历史增量。
- `state/context-summary.json`：已有工作/认知基线；`state/context-delta.json`：子agent提出的证据增量，未自动当作掌握状态。
- `state/reviewed-items.json`：公开候选的证据审核；`state/editorial-brief.md`：主agent编辑的简报。
- `reports/latest.md`：可阅读的简报；`state/publish-ledger.json`：实际发送回执。

## Agent配合

确定性脚本先完成已接入来源的采集、ID/版本/hash去重。私有上下文agent只处理新增工作证据；公开信息agent逐类检索四路候选，不接触群聊原文；主agent优先合并不超过3条主推，必要时附少量快讯。每轮深核最多3项（论文、报道或演示），避免重复读全部原文。详情见[运行协议](docs/agent-workflow.md)。

按质量优先原则，在Luna、Terra、Sol、Astra、Jev之间动态选型，不固定阶段与模型，见`config/model-routing.json`。这是宿主调度协议，尚未接无人值守模型执行器；不代表单独运行Python脚本就会调用模型。

这是agent协作驱动的原型，`collect`本身不调用模型，也不自动启动sub-agent。当前每日任务仅在本机Codex运行时触发，不具备云端无人值守执行能力。

## 微信入口

默认使用Search1API（每次显式调用，不自动充值）：`python3 search1api_client.py search --query '公众号名 主题'`只搜线索，`python3 search1api_client.py crawl --url 'https://mp.weixin.qq.com/s/文章'`提取正文，`python3 search1api_client.py usage`查余额。结果保存到`state/search1api/`，是待审核证据，尚未自动汇入简报。密钥优先读`SEARCH1API_KEY`，其次读被Git排除的`config/secrets.json`；不要回显该文件。尚无云端定时执行。

```bash
python3 pipeline.py import-wechat --url 'https://mp.weixin.qq.com/s/具体文章'
python3 pipeline.py import-wechat --file './exports/article.md'
```

URL入口只登记待采集线索；导出文件入口读入实际文本。二者均不等于读取个人微信关注列表，也不保证抓取文章正文。已验证的RSS可加入sources配置。微信CLI方案核验见[微信接入说明](docs/wechat-integration.md)，当前未安装未验证的客户端解密工具。

## 覆盖限制

- 首轮群聊最近7天，之后重叠1小时增量；旧消息编辑及所有线程回复未完整覆盖。分页未结束时保存游标，不推进成功水位。
- arXiv RSS只覆盖当前feed窗口；RSS公告时间不等于论文首次投稿日期。最终简报以原文投稿/修订日期为准。
- 产业、工业和前沿科学目前靠agent逐类检索，并非已部署的无人值守订阅；每轮记录检查与缺口。尚无云端每日调度或第一时间广播能力。
- 提及论文、列入分享计划、已读消息均不等于用户掌握；认知状态更新保留证据和待确认项。
- 表格实验结果为作者报告，不代表独立复现或统计显著；融资/PR叙述不作为验证证据。
- 任何来源失败都保留error/partial状态，不能解释为“今天没有新信息”。
