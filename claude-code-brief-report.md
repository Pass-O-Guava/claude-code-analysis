# Claude Code 泄露代码简要分析报告

**分析主题**: BUDDY 电子宠物系统  
**报告日期**: 2026年4月1日  
**代码来源**: Kuberwastaken/claude-code (Clean-room Rust 实现)  
**分析文件**: `crates/buddy/src/lib.rs`

---

## 一、系统概述

BUDDY 是 Claude Code 内置的一个 **Tamagotchi 风格电子宠物系统**，它是一个完整的伴侣系统，会在用户终端输入框旁边显示一个 ASCII 艺术风格的小动物。该系统具有以下特点：

- **18个独特物种**，分为 5 个稀有度等级
- **确定性生成**：基于用户 ID 使用 PRNG 算法确保每个用户获得固定伴侣
- **1% 闪率**：独立计算的闪光 (Shiny) 变体系统
- **AI 生成灵魂**：名字和性格由 Claude 在用户首次孵化时生成
- **动画系统**：三帧循环动画，500ms 切换

---

## 二、代码结构

### 2.1 模块组成

BUDDY 系统实现为单一文件库 (`lib.rs`)，约 **1,100+ 行代码**，包含以下主要组件：

```
buddy/
├── lib.rs
│   ├── Mulberry32 PRNG 实现
│   ├── 枚举定义 (Species, Rarity, Eye, Hat)
│   ├── CompanionStats 结构体
│   ├── CompanionBones 结构体 (确定性部分)
│   ├── CompanionSoul 结构体 (AI 生成部分)
│   ├── Companion 主结构体
│   ├── SpriteFrame 精灵系统
│   ├── 18 个物种的 ASCII 艺术精灵
│   └── 配置持久化功能
```

### 2.2 核心数据结构

```rust
// 确定性部分（从 user_id 重新派生）
pub struct CompanionBones {
    pub rarity: Rarity,        // 稀有度
    pub species: Species,      // 物种
    pub eye: Eye,             // 眼睛样式
    pub hat: Hat,             // 帽子装饰
    pub shiny: bool,          // 是否闪光
    pub stats: CompanionStats, // 五项属性
}

// AI 生成部分（持久化存储）
pub struct CompanionSoul {
    pub name: String,         // 名字
    pub personality: String,  // 性格描述
    pub hatched_at: DateTime<Utc>, // 孵化时间
}

// 完整伴侣
pub struct Companion {
    pub bones: CompanionBones,
    pub soul: Option<CompanionSoul>, // None 表示未孵化
}
```

---

## 三、核心机制：Mulberry32 PRNG

### 3.1 算法选择

BUDDY 使用 **Mulberry32** 算法，这是一个：
- **快速** 的 32 位伪随机数生成器
- **轻量级**，仅需一个 `u32` 状态
- **高质量**，通过 PractRand 测试
- **确定性**，相同种子产生相同序列

### 3.2 Rust 实现

```rust
pub struct Mulberry32 {
    state: u32,
}

impl Mulberry32 {
    pub fn new(seed: u32) -> Self {
        Self { state: seed }
    }

    pub fn next_u32(&mut self) -> u32 {
        self.state = self.state.wrapping_add(0x6d2b_79f5);
        let mut t = (self.state ^ (self.state >> 15)).wrapping_mul(1 | self.state);
        t = t.wrapping_add((t ^ (t >> 7)).wrapping_mul(61 | t)) ^ t;
        t ^ (t >> 14)
    }

    pub fn next_f64(&mut self) -> f64 {
        self.next_u32() as f64 / 4_294_967_296.0
    }
}
```

### 3.3 种子生成

种子从用户 ID 确定性派生：

```rust
pub fn seed_from_user_id(user_id: &str) -> u32 {
    let salted = format!("{}friend-2026-401", user_id);
    let hash = Sha256::digest(salted.as_bytes());
    u32::from_le_bytes([hash[0], hash[1], hash[2], hash[3]])
}
```

**关键设计**：
- 使用 `SHA-256` 哈希用户 ID + 盐值 `"friend-2026-401"`
- 取哈希前 4 字节作为小端序 `u32` 种子
- **同一用户永远获得相同伴侣**（除非用户 ID 改变）

---

## 四、物种与稀有度系统

### 4.1 18 个物种

| 物种 | 英文名称 | ASCII 特征 |
|------|---------|-----------|
| 🦆 鸭子 | Duck | `<(· )___` |
| 🪿 鹅 | Goose | `(·)>` |
| 🟣 史莱姆 | Blob | 圆润双点眼 |
| 🐱 猫 | Cat | `/\_/\` |
| 🐉 龙 | Dragon | `/^\ /^\` |
| 🐙 章鱼 | Octopus | `\/\/\/\` 触手 |
| 🦉 猫头鹰 | Owl | `/\ /\` |
| 🐧 企鹅 | Penguin | `.---.` |
| 🐢 乌龟 | Turtle | `_,--._` |
| 🐌 蜗牛 | Snail | `.--.` 壳 |
| 👻 幽灵 | Ghost | `/ · · \` |
| 🦎 美西螈 | Axolotl | `}~(...)~{` |
| 🦫 水豚 | Capybara | `n______n` |
| 🌵 仙人掌 | Cactus | `|·  ·|` |
| 🤖 机器人 | Robot | `.[||].` 天线 |
| 🐰 兔子 | Rabbit | `(\__/)` |
| 🍄 蘑菇 | Mushroom | `.-o-OO-o-.` |
| 🐽 胖墩 | Chonk | ` /\    /\ ` |

### 4.2 五层稀有度

| 稀有度 | 概率 | 属性下限 | 帽子规则 |
|--------|------|---------|---------|
| **Common** (普通) | 60% | 5 | 无帽子 |
| **Uncommon** (罕见) | 25% | 15 | 可戴帽子 |
| **Rare** (稀有) | 10% | 25 | 可戴帽子 |
| **Epic** (史诗) | 4% | 35 | 可戴帽子 |
| **Legendary** (传说) | 1% | 50 | 可戴帽子 |

### 4.3 闪光系统 (Shiny)

```rust
// 1% 独立闪光概率
let shiny = rng.next_f64() < 0.01;
```

**概率计算**：
- 闪光传说级：1% × 1% = **0.01%** (万分之一的概率)
- 闪光独立于稀有度，任何稀有度都可能闪光

---

## 五、属性系统

### 5.1 五项属性

每个伴侣拥有 5 项属性，范围 1-100：

| 属性 | 含义 | 巅峰值加成 |
|------|------|-----------|
| `DEBUGGING` | 调试能力 | +50~+79 |
| `PATIENCE` | 耐心 | 基础值 |
| `CHAOS` | 混乱度 | 基础值 |
| `WISDOM` | 智慧 | 基础值 |
| `SNARK` | 讽刺值 | 基础值 |

### 5.2 属性生成算法

```rust
pub fn roll(rarity: &Rarity, rng: &mut Mulberry32) -> Self {
    let floor = rarity.stat_floor() as f64;
    
    // 随机选择巅峰属性和低谷属性（确保不同）
    let peak_idx = (rng.next_f64() * 5.0) as usize % 5;
    let mut dump_idx = (rng.next_f64() * 5.0) as usize % 5;
    if dump_idx == peak_idx {
        dump_idx = (dump_idx + 1) % 5;
    }

    // 每项属性计算
    for (i, v) in values.iter_mut().enumerate() {
        *v = if i == peak_idx {
            // 巅峰：基础 + 50-80
            ((floor + 50.0 + rng.next_f64() * 30.0) as u8).min(100)
        } else if i == dump_idx {
            // 低谷：略低于基础
            let raw = floor - 10.0 + rng.next_f64() * 15.0;
            if raw < 1.0 { 1 } else { raw as u8 }
        } else {
            // 普通：基础 + 0-40
            (floor + rng.next_f64() * 40.0) as u8
        };
    }
    // ...
}
```

**设计意图**：
- 每个伴侣有独特的"专长"（巅峰属性）
- 每个伴侣有"弱点"（低谷属性）
- 稀有度越高，整体属性越强

---

## 六、视觉系统

### 6.1 眼睛样式 (6种)

```rust
pub enum Eye {
    Dot,      // ·
    Star,     // ✦
    X,        // ×
    Circle,   // ◉
    At,       // @
    Degree,   // °
}
```

### 6.2 帽子装饰 (8种)

| 帽子 | 图案 | 稀有度要求 |
|------|------|-----------|
| None | (空) | Common 强制 |
| Crown | `\^^^/` | Uncommon+ |
| Tophat | `[___]` | Uncommon+ |
| Propeller | `-+-` | Uncommon+ |
| Halo | `(   )` | Uncommon+ |
| Wizard | `/^\` | Uncommon+ |
| Beanie | `(___)` | Uncommon+ |
| TinyDuck | `,>` | Uncommon+ |

### 6.3 ASCII 精灵系统

每个物种有 **3 帧动画**，每帧 5 行 × 12 字符：

```rust
pub struct SpriteFrame(pub [&'static str; 5]);

// 鸭子示例
Species::Duck => [
    SpriteFrame([
        "            ",  // 帽子槽
        "    __      ",
        "  <({E} )___  ", // {E} 替换为眼睛符号
        "   (  ._>   ",
        "    `--´    ",
    ]),
    // ... 第2帧
    // ... 第3帧
]
```

### 6.4 动画序列

```rust
const SEQ: [usize; 15] = [0, 0, 0, 0, 1, 0, 0, 0, 2, 0, 0, 2, 0, 0, 0];

pub fn animation_frame(tick: u64) -> usize {
    SEQ[(tick as usize) % SEQ.len()]
}
```

- 每 500ms 一个 tick
- 15 步循环，帧分布: 0(8次), 1(1次), 2(2次)
- 产生自然的"偶尔动一下"效果

### 6.5 渲染流程

```rust
pub fn render(companion: &Companion, tick: u64) -> String {
    1. 获取当前物种的 3 帧精灵
    2. 根据 tick 选择当前帧
    3. 用眼睛符号替换 {E} 占位符
    4. 如果第 0 行空白，注入帽子图案
    5. 如果所有帧第 0 行都空白，删除第 0 行（节省空间）
    6. 返回拼接的多行字符串
}
```

---

## 七、系统设计亮点

### 7.1 分离式架构

| 部分 | 存储方式 | 说明 |
|------|---------|------|
| **Bones** (骨骼) | 不存储，重新派生 | 确定性，防止作弊 |
| **Soul** (灵魂) | `companion.json` | AI 生成，持久化 |

```rust
pub fn get_companion(user_id: &str, config_dir: &Path) -> Companion {
    let soul = load_companion_soul(config_dir);  // 从文件加载
    Companion::new(user_id, soul)  // bones 重新计算
}
```

**优势**：
- 用户无法通过编辑文件来"伪造"稀有度
- 灵魂数据（名字、性格）可以被安全修改

### 7.2 AI 集成

```rust
pub fn companion_intro_text(name: &str, species: &str) -> String {
    format!(
        "A small {species} named {name} sits beside the user's input box \
         and occasionally comments in a speech bubble. \
         You're not {name} — it's a separate watcher."
    )
}
```

- 系统提示词告知 Claude 伴侣的存在
- 用户可以直接对伴侣说话（通过名字）
- 伴侣会在气泡中回应

### 7.3 命名彩蛋

- 物种中包含 **Capybara**（水豚）—— 对应内部代号 "Capybara" = Sonnet
- 盐值 `"friend-2026-401"` 暗示 2026 年 4 月 1 日（发布日期？）

---

## 八、技术评估

### 8.1 设计优点

1. **确定性生成**：同一用户始终获得相同伴侣，建立情感连接
2. **反作弊设计**：Bones 不存储，无法通过修改文件获得稀有伴侣
3. **丰富的视觉**：18 物种 × 6 眼睛 × 8 帽子 × 2 闪光 = 1,728 种视觉组合
4. **轻量级**：纯 ASCII，无图像依赖
5. **AI 增强**：灵魂生成让每只伴侣独一无二

### 8.2 潜在改进

1. **无进化系统**：Tamagotchi 经典玩法缺失
2. **无喂养机制**：没有传统电子宠物的照料玩法
3. **有限的互动**：目前仅显示和偶尔对话

---

## 九、总结

BUDDY 系统是一个**设计精巧、实现完整**的彩蛋功能，展示了 Claude Code 团队的工程实力和幽默感。它不是简单的装饰，而是一个：

- 使用密码学哈希确保公平性的**游戏化系统**
- 融合 ASCII 艺术的**复古终端美学**
- 与 AI 对话系统**深度集成**的伴侣

这个系统的存在，暗示了 Claude Code 未来可能向**更个性化、更有情感连接**的方向发展。

---

*分析完成于 2026年4月1日*
