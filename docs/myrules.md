# CLI 声明式参数架构协议 (Vibe Coding Edition v2.0)

## 一、 核心准则 (Core Principles)

* **全局唯一性 (Global Uniqueness):** 所有叶子属性（Property）名在整个程序中具有唯一性，严禁使用层级前缀（如禁止使用 `--user-name`，直接使用 `--name`）。
* **隐式初始化 (Implicit Initialization):** 只要检测到从属属性，系统必须自动激活其所属的实体节点（Entity），并应用默认上下文。
* **读向性语义 (Read-Oriented):** 默认配置旨在提供最大的数据覆盖面，减少显式声明。
* **协作优先 (Collaboration First):** 当新的设计需求与本规则发生冲突时，AI 应**主动向用户反映**，共同讨论是调整需求方案还是修订规则本身，而非单方面做出决策。

---

## 二、 实体与参数分类 (Classification Codes)

我们将参数逻辑拆解为以下四个专业维度，指挥时直接调用编号：

### **E (Entity): 实体节点**

* **定义：** 逻辑上的对象容器或功能命名空间。
* **特性：** 不一定直接在 CLI 中表现为参数，但它是逻辑组织的单元。
* **指挥示例：** `Define Entity E101: Network-Stack`

### **A (Attribute): 独立属性**

* **定义：** 全局唯一的叶子参数，直接承载值。
* **依赖：** 每个 **A** 必须且只能映射到一个 **E**。
* **敏捷逻辑：** 触发 `A` 则自动推导出对应的 `E`。
* **指挥示例：** `Assign Attribute A201 (--port) to E101`

### **X (Exclusion): 互斥约束**

* **定义：** 属性或实体之间的硬性冲突规则。
* **逻辑：** ，集合内仅允许单一成员存在。
* **指挥示例：** `Set Exclusion X301 on [A205, A208]`

### **D (Derivation): 推导规则**

* **定义：** 当实体被隐式初始化时，其父级或关联实体的默认状态。
* **逻辑：** 。
* **指挥示例：** `Set Derivation D401: If any A of E102 exists, set E102.mode = "readonly"`

---

## 三、 指挥用例（Vibe Coding Instructions）

当你指挥 AI 编写代码或增加参数时，请使用以下标准化指令格式：

> **指令：[操作类型] [编号]**
> * **ADD E101:** 声明新实体 `Storage`。
> * **BIND A501 (--path) TO E101:** 绑定唯一属性至实体。
> * **ASSERT X601 OVER [A501, A502]:** 声明两个属性为互斥关系。
> * **ENABLE IMPLICIT-INIT FOR E101:** 开启该实体的敏捷模式，允许属性反向推导实体。
> 
> 

---

## 四、 内部解析逻辑状态机

1. **Flattened Capture:** 捕获所有 `argv` 中的唯一标识符。
2. **Entity Mapping:** 检索 **A -> E** 映射表，标记所有活跃实体。
3. **X-Constraint Check:** 遍历所有 **X** 集合，检测活跃属性是否违反互斥逻辑。
4. **Context Synthesis:** 触发 **D** 规则，补全所有未显式指定的父辈上下文参数。
5. **Object Tree Assembly:** 将扁平参数组装成结构化对象（JSON/Object），传递给业务逻辑层。

---

## 五、 错误处理规范 (Exception Standards)

* **Conflict Error:** "Invalid Argument Combination: [A_i] and [A_j] are mutually exclusive."
* **Ambiguity Error:** (仅在违反全局唯一性时触发) "Ambiguous Property: [A_n] matches multiple Entities."

