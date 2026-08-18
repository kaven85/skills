# Diagram Recipes

Complete, styled, copy-adaptable examples. Init directives are shown joined on one line exactly as they should be pasted. Contents:

- Flowchart (decision flow)
- Architecture (subgraph lanes)
- Sequence (alt/else, activation, note)
- ER (keys and crow's foot)
- UML Class
- State
- Mindmap
- Timeline
- Gantt
- Quadrant chart
- Sankey (beta)
- XY chart (beta)

## Flowchart (decision flow)

```mermaid
%%{init: {"theme": "base", "themeVariables": {"fontFamily": "-apple-system, 'PingFang SC', 'Segoe UI', sans-serif", "fontSize": "14px", "lineColor": "#64748b", "primaryTextColor": "#1f2937", "edgeLabelBackground": "#ffffff"}, "flowchart": {"curve": "basis", "nodeSpacing": 45, "rankSpacing": 55}}}%%
flowchart TD
  START(["资产登记申请"]):::success --> REVIEW["合规初审"]:::primary
  REVIEW --> PASS{"材料齐全?"}:::warning
  PASS -->|"是"| CHAIN["上链存证"]:::primary
  PASS -->|"否"| SUPP["补充材料"]:::danger
  SUPP --> REVIEW
  CHAIN --> DONE(["发放凭证"]):::success
  classDef primary fill:#dae8fc,stroke:#6c8ebf,stroke-width:1.5px,color:#1f2937;
  classDef success fill:#d5e8d4,stroke:#82b366,stroke-width:1.5px,color:#1f2937;
  classDef warning fill:#fff2cc,stroke:#d6b656,stroke-width:1.5px,color:#1f2937;
  classDef danger fill:#f8cecc,stroke:#b85450,stroke-width:1.5px,color:#1f2937;
  linkStyle 4 stroke:#82b366,stroke-width:2.5px;
```

`linkStyle 4` highlights the happy-path edge to the terminal node. Count edges from 0 in definition order.

## Architecture (subgraph lanes)

```mermaid
%%{init: {"theme": "base", "themeVariables": {"fontFamily": "-apple-system, 'PingFang SC', 'Segoe UI', sans-serif", "fontSize": "14px", "lineColor": "#64748b", "primaryTextColor": "#1f2937", "edgeLabelBackground": "#ffffff", "clusterBkg": "#f8fafc", "clusterBorder": "#cbd5e1"}, "flowchart": {"curve": "linear", "nodeSpacing": 45, "rankSpacing": 60}}}%%
flowchart LR
  subgraph CLIENT["客户端"]
    direction LR
    WEB["🌐 Web 控制台"]:::primary
    APP["📱 移动 App"]:::primary
  end
  subgraph EDGE["接入层"]
    GW["API 网关<br/>限流 · 鉴权"]:::warning
  end
  subgraph SVC["服务层"]
    direction LR
    ASSET["资产服务"]:::primary
    TRADE["交易服务"]:::primary
    KYC["身份核验"]:::external
  end
  subgraph DATA["数据层"]
    direction LR
    DB[("PostgreSQL")]:::danger
    CACHE[("Redis")]:::danger
    MQ[/"Kafka"/]:::neutral
  end
  WEB --> GW
  APP --> GW
  GW --> ASSET
  GW --> TRADE
  ASSET --> KYC
  TRADE --> KYC
  ASSET --> DB
  ASSET --> CACHE
  TRADE --> MQ
  classDef primary fill:#dae8fc,stroke:#6c8ebf,stroke-width:1.5px,color:#1f2937;
  classDef warning fill:#fff2cc,stroke:#d6b656,stroke-width:1.5px,color:#1f2937;
  classDef danger fill:#f8cecc,stroke:#b85450,stroke-width:1.5px,color:#1f2937;
  classDef neutral fill:#f5f5f5,stroke:#666666,stroke-width:1.2px,color:#374151;
  classDef external fill:#e1d5e7,stroke:#9673a6,stroke-width:1.5px,color:#1f2937;
  style CLIENT fill:#f0f7ff,stroke:#6c8ebf,color:#1e3a5f
  style EDGE fill:#fffbeb,stroke:#d6b656,color:#5c4a1f
  style SVC fill:#f0fdf4,stroke:#82b366,color:#1f4427
  style DATA fill:#fef2f2,stroke:#b85450,color:#5f2120
```

Lane order = reading order (left→right for LR). Keep inter-lane edges flowing one direction; a back-flow edge is a smell — check the semantic model.

## Sequence (alt/else, activation, note)

```mermaid
%%{init: {"theme": "base", "themeVariables": {"fontFamily": "-apple-system, 'PingFang SC', 'Segoe UI', sans-serif", "fontSize": "14px", "actorBkg": "#dae8fc", "actorBorder": "#6c8ebf", "actorTextColor": "#1f2937", "signalColor": "#475569", "signalTextColor": "#1f2937", "noteBkg": "#fff2cc", "noteBorder": "#d6b656", "noteTextColor": "#5c4a1f", "activationBkg": "#dbeafe", "activationBorder": "#6c8ebf", "sequenceNumberColor": "#ffffff"}}}%%
sequenceDiagram
  autonumber
  participant U as 👤 投资者
  participant W as 🌐 前端
  participant T as 💱 交易服务
  participant C as ⛓️ 链上合约
  U->>W: 提交买入委托
  W->>T: POST /orders
  activate T
  T->>C: transfer(assetId)
  alt 链上确认
    C-->>T: ✅ TxHash
    T-->>W: 200 成交
  else 超时回滚
    C-->>T: ❌ Revert
    T-->>W: 409 失败已退款
  end
  deactivate T
  Note over T,C: 确认超时阈值 30s<br/>超过进入人工对账
  W-->>U: 推送结果通知
```

Sequence diagrams have no classDefs — styling lives entirely in themeVariables. Use `rect rgb(240,249,255) ... end` to shade a phase.

## ER (keys and crow's foot)

```mermaid
%%{init: {"theme": "base", "themeVariables": {"fontFamily": "-apple-system, 'PingFang SC', 'Segoe UI', sans-serif", "fontSize": "14px"}}}%%
erDiagram
  INVESTOR ||--o{ HOLDING : "持有"
  ASSET ||--o{ HOLDING : "被持有"
  ASSET ||--|{ ISSUE_RECORD : "发行记录"
  HOLDING ||--o{ TRADE_ORDER : "产生"
  INVESTOR {
    bigint id PK
    varchar name "姓名"
    varchar kyc_level UK
  }
  ASSET {
    bigint id PK
    varchar title "资产名称"
    varchar chain_id UK
    decimal issue_price
  }
  HOLDING {
    bigint id PK
    bigint investor_id FK
    bigint asset_id FK
    decimal amount
  }
  TRADE_ORDER {
    bigint id PK
    bigint holding_id FK
    varchar side "buy/sell"
    varchar status
  }
  ISSUE_RECORD {
    bigint id PK
    bigint asset_id FK
    varchar tx_hash UK
    datetime issued_at
  }
```

ER diagrams ignore classDefs — the value is correct cardinality (`||--o{`, `}o--o{`, `||--||`) and PK/FK/UK markers.

## UML Class

```mermaid
%%{init: {"theme": "base", "themeVariables": {"fontFamily": "-apple-system, 'PingFang SC', 'Segoe UI', sans-serif", "fontSize": "14px"}}}%%
classDiagram
  class ValuationModel {
    <<interface>>
    +valuate(asset) Price
  }
  class DCFModel {
    +valuate(asset) Price
    -discountRate: float
  }
  class ComparableModel {
    +valuate(asset) Price
    -peers: List
  }
  class PricingService {
    +price(asset) Quote
    -model: ValuationModel
  }
  ValuationModel <|.. DCFModel : implements
  ValuationModel <|.. ComparableModel : implements
  PricingService --> ValuationModel : depends on
```

Relationship arrows: `<|--` inheritance, `<|..` realization, `-->` association, `--*` composition, `--o` aggregation, `..>` dependency.

## State

```mermaid
%%{init: {"theme": "base", "themeVariables": {"fontFamily": "-apple-system, 'PingFang SC', 'Segoe UI', sans-serif", "fontSize": "14px"}}}%%
stateDiagram-v2
  [*] --> 待确权
  待确权 --> 审核中 : 提交材料
  审核中 --> 已确权 : 通过
  审核中 --> 待确权 : 驳回
  已确权 --> 流通中 : 挂牌
  流通中 --> 已冻结 : 风控触发
  已冻结 --> 流通中 : 解冻
  流通中 --> 已注销 : 到期
  已注销 --> [*]
  审核中:::warn
  流通中:::ok
  已冻结:::bad
  classDef warn fill:#fff2cc,stroke:#d6b656,color:#1f2937;
  classDef ok fill:#d5e8d4,stroke:#82b366,color:#1f2937;
  classDef bad fill:#f8cecc,stroke:#b85450,color:#1f2937;
```

State names may be Chinese directly. Attach classes inline with `名称:::class` — the standalone `class 名称 className` statement only accepts ASCII ids (or declare `state "审核中" as REVIEW` and use `class REVIEW warn`). Composite states: `state 审核中 { [*] --> 自动校验 }`.

## Mindmap

```mermaid
mindmap
  root((数字资产<br/>总体方案))
    资产类别
      数据资产
      模型资产
      内容资产
    治理
      确权登记
      定价模型
      合规审计
    生命周期
      采集加工
      挂牌流通
      退出注销
```

Mindmap theming is limited — rely on structure and concise wording. `root((...))` circle, `))...((` bang, `{{...}}` hexagon.

## Timeline

```mermaid
timeline
  title 数字资产平台演进
  2026 Q3 : 资产盘点 : 元数据登记上线
  2026 Q4 : 确权与定价模型 : 内测交易
  2027 Q1 : 对外开放 : API 市场
```

## Gantt

```mermaid
%%{init: {"theme": "base", "themeVariables": {"fontFamily": "-apple-system, 'PingFang SC', 'Segoe UI', sans-serif", "fontSize": "13px", "gridColor": "#e2e8f0", "sectionBkgColor": "#f0f7ff", "altSectionBkgColor": "#ffffff", "taskBkgColor": "#dae8fc", "taskBorderColor": "#6c8ebf", "activeTaskBkgColor": "#fff2cc", "doneTaskBkgColor": "#d5e8d4", "critBkgColor": "#f8cecc", "todayLineColor": "#b85450"}}}%%
gantt
  title 一期建设排期
  dateFormat YYYY-MM-DD
  axisFormat %m-%d
  section 平台
    账户体系 :done, a1, 2026-08-10, 7d
    资产登记 :active, a2, after a1, 10d
    流通撮合 :a3, after a2, 12d
  section 合规
    确权流程 :crit, 2026-08-18, 12d
    审计接口 :2026-08-30, 8d
```

## Quadrant chart

```mermaid
quadrantChart
  title 资产流通优先级
  x-axis 低流动性 --> 高流动性
  y-axis 低价值 --> 高价值
  quadrant-1 优先流通
  quadrant-2 培育估值
  quadrant-3 暂不投入
  quadrant-4 快速变现
  数据资产: [0.8, 0.9]
  模型资产: [0.4, 0.8]
  内容资产: [0.9, 0.5]
  藏品资产: [0.3, 0.3]
```

## Sankey (beta)

```mermaid
sankey-beta
  raw_data,cleaned,600
  raw_data,discarded,150
  cleaned,training_set,450
  cleaned,test_set,150
  training_set,tradable_model_asset,300
```

sankey-beta accepts only ASCII labels (no CJK, no quotes) — use English or pinyin and put the Chinese explanation in the surrounding prose.

## XY chart (beta)

```mermaid
xychart-beta
  title "月度资产登记量"
  x-axis ["1月", "2月", "3月", "4月", "5月"]
  y-axis "登记数" 0 --> 500
  bar [120, 210, 180, 320, 460]
  line [120, 210, 180, 320, 460]
```
