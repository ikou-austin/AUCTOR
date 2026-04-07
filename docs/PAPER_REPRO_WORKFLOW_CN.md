# 论文复现最小工作流

如果你的目标只有一个:

> 给一篇论文, 找到可用代码, 没有就沿方法链往上回溯到最近的开源基座, 然后配环境、处理数据、改代码、跑实验、判断是否复现成功。

那你可以把 ARIS 视为一个很小的栈, 不需要整套科研流水线。

## 建议保留的最小模块

- `paper-reproduction`
- `experiment-bridge`
- `run-experiment`
- `monitor-experiment`
- `training-check` 可选
- `arxiv` / `research-lit` 仅在论文信息不完整时使用

其余如 `idea-discovery`、`novelty-check`、`paper-writing`、`grant-proposal`、`rebuttal` 都可以先不看。

## 单入口

```text
/paper-reproduction "论文 URL / PDF / 标题"
```

这个入口负责:

1. 固定复现目标
2. 搜官方代码
3. 若无官方代码, 递归回溯父方法 / 基座模型 / benchmark harness
4. 选择最近的可用开源 repo
5. 生成环境与数据准备计划
6. 生成代码修改清单
7. 转成可执行实验里程碑
8. 交给实验执行链跑起来

## 推荐文件

```text
PAPER_REPRO_TARGET.md
repro-logs/
  PAPER_REPRO_PLAN.md
  REPO_LINEAGE.md
  REPRO_TRACKER.md
  ASSUMPTIONS.md
refine-logs/
  EXPERIMENT_PLAN.md
  EXPERIMENT_TRACKER.md
```

其中:

- `PAPER_REPRO_TARGET.md` 是你真正关心什么
- `REPO_LINEAGE.md` 是代码回溯链
- `ASSUMPTIONS.md` 是论文没写清楚时我们的重建假设
- `refine-logs/*.md` 是交给现有执行工作流的桥

## 最小使用方式

### 方式 1: 直接给论文

```text
/paper-reproduction "https://arxiv.org/abs/xxxx.xxxxx"
```

适合你还没整理输入文件。

### 方式 2: 先写目标文件

先复制模板:

```bash
cp templates/PAPER_REPRO_TARGET_TEMPLATE.md PAPER_REPRO_TARGET.md
```

填完后执行:

```text
/paper-reproduction
```

适合你已经知道要复现哪张表、哪个指标、允许多大误差。

## 这个精简版本和原工作流的关系

- `paper-reproduction` 负责补上原 `workflow 1.5` 没覆盖的部分:
  - 论文解析
  - 官方代码搜索
  - 递归基座回溯
  - repo 选型决策
- `experiment-bridge` 继续负责:
  - 把计划落实成脚本
  - sanity check
  - 部署实验
  - 收集初始结果
- `run-experiment` / `monitor-experiment` 负责实际执行和监控

也就是说, 现在你只需要记住一条线:

```text
论文 -> /paper-reproduction -> /experiment-bridge -> /run-experiment -> /monitor-experiment
```

## 结果判定

最终只分四类:

- `REPRODUCED`: 目标指标在容差内
- `PARTIAL`: 趋势对了, 但绝对数值没到
- `BLOCKED`: 数据 / 代码 / 细节缺失, 无法公平复现
- `NEGATIVE`: 按当前最合理重建, 论文主结果站不住

不要在没有原始数字、命令和假设记录的情况下宣称“复现成功”。
