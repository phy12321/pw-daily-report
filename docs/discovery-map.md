# 具身进展检索地图（后台使用）

此文件用于发现、筛选和查漏，不是简报目录或正文模板；用户关注方向和商业问题以`config/focus.json`为准。每轮按事件价值动态选源；无需逐站逐标签机械巡检，更不能为了覆盖率凑稿。除`config/sources.json`中已启用的 arXiv RSS、已授权飞书范围，以及按需调用的 Search1API 外，下列均为**待 agent 检索的候选入口**，不是已接通的自动订阅。检索不到、访问失败与确无更新分开记录。新来源先核身份、更新时间与原始证据，再收入清单。

## 来源地图

| 来源层 | 优先检索入口 | 作用与核验 |
| --- | --- | --- |
| 论文与代码 | arXiv cs.RO/cs.LG（已接 RSS）；按主题补查 cs.CV/cs.AI、OpenReview、CoRL/RSS/ICRA/IROS、NeurIPS/ICLR/ICML、PMLR、作者项目页与 GitHub | RSS 是线索；以原文、版本、代码、评测协议核结论与时间。宽泛会议源不等于全量已接入。 |
| 用户指定重点 | [AMI Labs](https://amilabs.xyz/)及具体作者/项目页 | 区分 AMI 署名、LeCun 合著与仅转发；跟踪 JEPA、预测表征、规划和记忆。 |
| 大模型与具身研究团队 | [Google DeepMind Research](https://deepmind.google/research/)、[Microsoft Research](https://www.microsoft.com/en-us/research/blog/)、[NVIDIA Research](https://research.nvidia.com/)、Meta FAIR、Toyota Research Institute、Stanford/UC Berkeley/MIT/CMU 等论文与实验室主页 | 从论文/项目追到原始方法和视频；机构主页只是入口，不把通用 AI 消息当具身消息。 |
| 同行原始发布 | [Physical Intelligence](https://www.pi.website/)、[Skild AI](https://www.skild.ai/blogs)、[Generalist](https://generalistai.com/blog)、[Figure](https://www.figure.ai/news)、[AGIBOT](https://www.agibot.com/news)、[Unitree](https://www.unitree.com/news/)、Agility Robotics 等官方技术页与演示 | 追任务协议、起点/对象/环境变化、人工介入和客户确认；官方自述不等于独立验证。名单按公司竞争集动态增删。 |
| 公开评测与工具链 | [RoboDojo](https://robodojo-benchmark.com/)、[LIBERO-Plus](https://github.com/sylvestf/LIBERO-plus)、[RoboTwin](https://robotwin-platform.github.io/leaderboard)、[LeRobot](https://github.com/huggingface/lerobot)及相应代码/排行榜 | 对齐版本、任务、训练数据、成功率与复现条件；榜单分数不自动推断真实部署收益。 |
| 部署方与产业 | [IFR](https://ifr.org/ifr-press-releases)、[BMW Group Press](https://www.press.bmwgroup.com/global/)、[Amazon Robotics](https://www.aboutamazon.com/news/tag/robotics)、客户/集成商/监管方原始披露 | 关注实际任务、连续运行、接管、吞吐、成本和部署状态；复核后续更新或撤回。 |
| 跨领域前沿科学 | [bioRxiv neuroscience](https://www.biorxiv.org/collection/neuroscience)、[Nature Machine Intelligence](https://www.nature.com/natmachintell/articles)、Janelia、Google Research 等原始论文/项目 | 神经回路、运动学习、控制、物理仿真、传感/材料只有具身迁移链条明确才入候选；尚无机器人验证时标启发。 |
| 报道与公众号 | `config/sources.json`的八个用户指定公众号；IEEE Spectrum Robotics 等专业媒体与可信科技/产业媒体 | 仅作发现、采访和时间线索；追溯论文、演示、客户/合作方原始发布。Search1API 搜索不保证账号每日全量。 |

融资、合作、订单、开源发布和演示都可能是重要事件，但不得把传播量或融资额换算成模型能力。用户举过的果蝇大脑控制机械臂、模型控制机器人、ICL demo 是**发现目标类型**，不是预先证实的新闻。检索时加入中英文别名、作者/机构名、任务名、基准名及新旧版本；必要时从媒体反向追原始链接。

## 多轴技术分类：只用于内部检索与判断

每个候选标一个主机制叶子，可补多个次机制；另标机器人能力、数据/学习时机、证据与场景。不要把这些标签印进简报，也不要求每个叶子每天有结果。跨轴检索能找出“旧技术在新任务/新证据下发生的真正变化”。

| 机制轴 | 细粒度叶子与检索别名（中英文同搜） |
| --- | --- |
| 表征与世界模型 | JEPA/联合嵌入预测；动作条件动力学；视频生成/可交互模拟器；3D/4D空间与物体表征；接触/物理/因果建模；不确定性、价值/奖励；记忆、长期预测与目标/子目标规划。区分“会预测视频”与“能改善闭环行动”。 |
| 策略与动作生成 | VLA/视觉语言动作；通用策略/语言规划；扩散、flow 与 action chunk；分层技能组合；轨迹优化/MPC；抓取/灵巧手；双臂协同；移动操作；腿足/全身控制。区分离线生成轨迹与在线反馈控制。 |
| 学习与适应 | 模仿/行为克隆；人类视频迁移与跨本体；自监督/预测学习；示例提示与具身 ICL；test-time training/在线参数更新；离线/在线 RL；自博弈/自改进；终身学习、fleet learning。分清推理时检索、上下文适应与梯度更新。 |
| 数据与仿真 | 遥操作/UMI/第一视角采集；数据质量、去重与主动采样；合成数据/视频数据；仿真器、数字孪生与接触建模；domain randomization/sim-to-real；跨机器人动作重定向；数据效率和扩展律。 |
| 感知、本体与部署 | 视觉/深度/触觉/本体感受与主动感知；末端执行器、灵巧手与本体设计；端侧推理与云边协作；控制频率/延迟/能耗；安全约束、失败检测、恢复与人工接管；系统集成与单位任务成本。 |
| 评测与基础理论 | 多任务/跨场景/长时程评测；分布外鲁棒性；公开 benchmark 与复现；成功率、方差、失败归因与公平预算；可辨识性、泛化边界、控制/规划理论与反例。理论价值和工程收益分开判断。 |
| 可迁移前沿科学 | connectomics/神经回路控制；生物运动学习与记忆；神经形态计算；新型触觉与材料；控制论、物理和因果发现。写出“原领域机制→机器人可实现模块→尚缺的验证”。 |

其他轴：

- **机器人能力**：单臂/双臂、灵巧操作、移动操作、全身运动、人机协作；短时/长时，多物体/可变形物体，开放环境/受控环境。
- **数据与适应时机**：预训练数据、离线任务数据、演示/上下文、测试时更新、部署后在线学习；记录是否增加外部数据、检索库、算力或人工。
- **证据阶梯**：理论或模拟/toy → 公开复杂操作 benchmark → 多任务/跨域公开复现 → 真机演示 → 连续生产试点 → 客户验证的规模化部署。不是所有条目都必须爬到最后一级；理论突破可独立主推。
- **事件类型**：论文、代码/权重、评测、演示、产品、客户试点、部署扩张、合作/融资、政策/供应链。事件类型不等于证据等级。
- **业务场景**：制造/装配、仓储/分拣、零售/理货、家务服务、物流、实验室自动化、医疗/特种等；以公司实际业务关联为门槛，不因场景热门就入选。

## 检索到正文的压缩规则

后台可以宽搜、交叉核验、标多轴；正文只留下最新且此前未报道的少量结论。每条优先回答：**新变化是什么；为什么可能奏效；最硬的证据和限制是什么；对公司意味着什么**。能用常见词说清就不展示分类名、复杂术语、搜集过程或来源覆盖表。只在覆盖缺口会误导本期结论时用一句话披露。检索与编辑须对照`state/reported-events.json`和已投递简报；已报道事件的新转载或无实质变化修订不再入选，新的关键证据只写增量。同一期转载仍归并，文章/事件日期仍核准，发送回执与幂等保护不关闭。
