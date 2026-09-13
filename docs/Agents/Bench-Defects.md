# ABB 自身的缺陷清单

来自 2026-09-11/12 两轮全量实测（13 个 enabled agent 的 observe + 4 个完整 evaluate）。
**只列 bench 代码本身的问题**，agent 侧和环境侧的分在最后一节。
行号对 `yao/main` (7722909)。

---

## A. 已修，有分支

### A1. 调用了 KUMA SDK 里不存在的 API —— 所有 evaluate 一律崩

`agentbench/sdk/kuma/worker.py:17`

```python
from kuma import create_run, generate_cases     # generate_cases 不存在
...
run = create_run(case_batch=..., case_index=...)  # 这两个参数也不存在
```

SDK 从来没有批量出题入口。Case 的产生只有 `create_run(...)` 一条路，
复用只有 `Run.save_case(path)` + `create_run(case_path=...)`。

**症状**：容器里 `ImportError: cannot import name 'generate_cases' from 'kuma'`，
CLI 只报一句 `RuntimeError: Case batch generation failed`。任何 agent 都跑不了评测。
**不计费**（挂在任何 API 调用之前）。

**修**：`fix/kuma-case-api` → 官方仓 **PR #6**（OPEN，两天零 review）。+294/−196，6 个文件。

### A2. 没屏蔽 SDK 的版本检查 —— 把每一条 trace 判死

`agentbench/sdk/kuma/image.py:53`（评测 overlay 的 Dockerfile 拼接处）

KUMA SDK ≥0.2.0 一启动就发
`GET https://api.github.com/repos/DefuzeX-AI/KUMA-DefuzeX/releases/latest`
（`kuma/updates.py:16`）。`api.github.com` 不在声明路由里 → 拦截器 403 →
记成 `llm_error` → `InterceptionTraceState` 判死整条 invocation。

**症状**：`Agent invocation completed without a matched LLM request/response trace`，
**哪怕 agent 的模型调用全部 200**。每个容器恰好一次，casegen 容器和执行容器都中，
位置随 agent 调用次数浮动（见过第 1/3/5/7 次），所以极易误读成「agent 自己乱发请求」。
`observe` 不复现（它不在容器里跑 SDK），只有 `evaluate`/`certify`/`run` 会中。
**这条计费** —— 题都出完了才在执行阶段挂。

**修**：overlay 里加 `ENV KUMA_DISABLE_UPDATE_CHECK=1`（SDK 自带的开关）。
**不要去声明 `api.github.com`** —— 那是为一个在评测里毫无用处的检查给沙箱开真实外网口子。
分支 `fix/sdk-update-check-egress`（`efd2c25`），**尚未开 PR**。
SDK 0.2.2 里这个检查原样还在，所以修复依然必要。

### A3. `llm_error` 不说被拦的是谁 —— 接入全靠猜

`services/model-interceptor/src/defuzex_model_interceptor/addon.py:_emit_error`

```python
emit("llm_error", agent_id=..., call_id=..., error=..., framework_span_id=...)
```

而被拦请求的 `defuzex_source_host` / `defuzex_source_path` **就在同一个 `flow.metadata` 里**
（route 查找失败前几行刚设的，:45-46），偏偏没带出来。
拦截器容器的 stdout 也只有 `DEFUZEX_TRACE` 行，不记被拦的 host。
于是「哪个出站被拦了」在**任何产物里都查不到**。

**代价是实打实的**：ra-aid 那个未知 host 之前查了好几轮都没抓到；
补上三个字段（`source_host`/`source_path`/`method`）之后，一次就出来了 ——
`raw.githubusercontent.com/BerriAI/litellm/main/model_prices_and_context_window.json`。
同一轮里 06（`arxiv.org`）、08/12（`api.anthropic.com` 404）、01（`Client disconnected.`）
也全部一次定位，而且暴露出 01 根本不是拦截、是断线 —— 没有这个字段会一直误判。

**修**：同 `fix/sdk-update-check-egress` 分支。

---

## B. 已定位，还没修

### B1. 把 LangGraph 的控制流当成错误 —— 成功的运行被无故降级

`agentbench/observe/langchain.py:26`

```python
def _error(self, error, run_id, **kwargs):
    self.store.record("span_error", span_id=str(run_id), error=str(error))
```

这是 LangChain 的 `on_chain_error` 回调，**不做任何过滤**。
LangGraph 用抛异常的方式在子图之间路由（`Command(graph=..., update=...)`），
回调管理器把它当 chain error 递进来，ABB 就记成 `span_error`。

`agentbench/observe/service.py:42-47`：只要 `framework:span_error > 0`
就把 `succeeded` 降级成 `degraded`。

**症状**：unit 05 article-explainer —— 内层 `result.json` 明明是 `status: succeeded`、
答案完整，外层 `run.json` 却是 `degraded`，
warning 写「Report returned, but observed operations failed」。
`span_error` 的 error 字段里装的是 `Command(graph='__parent__', update={'messages': [...]})`。

**影响面**：凡是用子图 `Command` 路由的 LangGraph agent 都会中。本轮 12 个里 1 个确认。

**修法**：`_error` 里把 LangGraph 的控制流异常过滤掉
（`langgraph.errors.ParentCommand` / `GraphInterrupt` 这一类），别记进 `span_error`。

### B2. `--sdk-source` 的默认值指向一个不存在的目录

`agentbench/sdk/kuma/benchmark.py:38`

```python
self.sdk = Path(options.get('sdk_source', Path(__file__).resolve().parents[4] / 'Defuze-SDK'))
```

`parents[4]` = 仓库的上一级，拼出 `<workspace>/Defuze-SDK` —— 这个目录不存在，
而且 SDK 仓库的实际名字是 `KUMA-DefuzeX`，不是 `Defuze-SDK`（大概是改名后没跟）。
不显式传 `--sdk-source` 就必然 `ProviderSelectionError: Local KUMA SDK source unavailable`。
不计费，但 README 的快速上手路径直接走不通。

### B3. `run` 阻塞在 `input()`，没有非交互开关

`agentbench run` 会停下来等确认，而 CLI **没有 `--yes` 参数**。
脚本化/CI 里只能 `printf 'yes\n' |` 喂进去。

---

## C. 设计约束（不算 bug，但是接入成本的大头）

### C1. 只有一个 framework adapter

`agentbench/adapter/factory.py:74` → `{"langgraph": LangGraphAdapter.from_agent_dir}`，
`agentbench/observe/observers.py:25` 同名注册。就这一条。

非 LangChain 的 agent **也只能**注册成 `framework = "langgraph"`，
而且镜像里**必须装 `langchain-core`**，否则 worker 在 `observe/langchain.py` import 就崩。
好在 loader 只要求 binding 对象有 `.invoke()`，所以任何 Python agent
（哪怕是个驱动 CLI 的 subprocess）都能塞进来 —— 但标签是假的，这会误导后来的人。

### C2. 未声明出站判死整条 trace，且被标成 "LLM call"

严格出站是有意为之，没问题。问题是**呈现**：
一个 `arxiv.org` 的网页抓取会在终端上显示成
`LLM call 05 | model | FAILED`，看起来像模型调用失败。
配合 A3（不报 host），排查成本被放大了一个量级。

---

## D. 不是 ABB 的问题（对照组）

本轮 12 个 observe 的失败里，下面这些**不是 bench 的锅**：

| 单元 | 现象 | 归属 |
|---|---|---|
| 08、12 | `api.anthropic.com/v1/messages` 404 | agent 是 Anthropic 原生，上游端点选错 —— 换 `api.deepseek.com/anthropic/v1` |
| 06 | 拦 `arxiv.org` | agent 的业务必需出站，该在它自己的 `agent.toml` 里声明 |
| 11 | 拦 litellm 价格表 | agent 启动时联网，照 tiktoken 老办法 build 期预热或关掉 |
| 09 | `ExtendedSandboxedShellInput` 少传 `state.binary_path` | agent 自己调工具传错参，degraded 名副其实 |
| 01 | 20 次调用后 `Client disconnected.` 打在**已声明**路由上 | 传输层超时，调超时或减并发 |
| 10 | 900s 没跑完 | 纯慢，轨迹干净零拦截 |

---

## 汇总

| | 条目 | 状态 |
|---|---|---|
| A1 | SDK API 调用不存在的名字 | 已修，PR #6 OPEN 两天无人看 |
| A2 | 没屏蔽 SDK 版本检查，判死所有 trace | 已修，分支已推，**未开 PR** |
| A3 | `llm_error` 丢掉被拦的 host | 已修，同上分支 |
| B1 | LangGraph 控制流被当成 span 失败 | **未修** |
| B2 | `--sdk-source` 默认路径不存在 | **未修** |
| B3 | `run` 没有 `--yes` | **未修** |
| C1 | 只有一个 adapter | 设计约束 |
| C2 | 未声明出站的呈现方式误导 | 设计约束 |

**按影响排**：A2 最狠（所有 agent 全挂，且计费）→ A1（所有 agent 全挂，不计费）
→ A3（不挂但排查成本翻倍）→ B1（少数 agent 被误判）→ B2/B3（上手摩擦）。
