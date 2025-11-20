# 交通分配系统 (Traffic Assignment System)

电子科技大学 - 交通域划原理课程报告 2025

## 项目简介

本项目实现了完整的交通分配系统，支持三种主流交通分配算法：

1. **全有全无分配** (All-or-Nothing Assignment)
2. **增量分配** (Incremental Assignment)
3. **Frank-Wolfe用户均衡分配** (User Equilibrium with Frank-Wolfe)

系统基于BPR (Bureau of Public Roads) 行程时间函数，能够对路网进行流量分配、性能评估和可视化分析。

## 功能特性

### 核心功能
- ✅ 路网数据加载与管理
- ✅ OD需求处理
- ✅ 基于Dijkstra的最短路径计算
- ✅ 三种交通分配算法
- ✅ BPR行程时间模型
- ✅ 路网性能评估指标
- ✅ 完整的可视化系统

### 技术特点
- 模块化设计，符合SOLID原则
- 完整的日志系统
- 详细的错误处理
- 单元测试和集成测试

## 项目结构

```
traffic_assignment/
├── data/                       # 数据文件
│   ├── network.json           # 路网数据
│   └── demand.json            # 需求数据
├── src/                       # 源代码
│   ├── models/                # 数据模型
│   │   ├── link.py           # 路段类（BPR函数）
│   │   ├── network.py        # 路网类
│   │   └── demand.py         # 需求类
│   ├── algorithms/            # 算法实现
│   │   ├── dijkstra.py       # 最短路径
│   │   ├── all_or_nothing.py # 全有全无
│   │   ├── incremental.py    # 增量分配
│   │   └── frank_wolfe.py    # Frank-Wolfe
│   ├── evaluation/            # 评估指标
│   │   └── metrics.py
│   ├── visualization/         # 可视化
│   │   └── plotter.py
│   └── utils/                 # 工具函数
│       └── logger.py
├── tests/                     # 测试文件
│   ├── test_models.py
│   ├── test_algorithms.py
│   ├── test_evaluation.py
│   └── test_integration.py
├── output/                    # 输出目录
├── main.py                    # 主程序
├── requirements.txt           # 依赖管理
└── README.md
```

## 安装与使用

### 环境要求
- Python 3.8+
- pip

### 安装依赖

```bash
cd traffic_assignment
pip install -r requirements.txt
```

### 运行主程序

```bash
python main.py
```

程序将自动执行以下步骤：
1. 加载路网和需求数据
2. 执行三种分配算法
3. 计算性能指标
4. 生成可视化图表
5. 输出对比结果

所有结果保存在 `output/` 目录下。

### 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_models.py -v
pytest tests/test_algorithms.py -v
pytest tests/test_integration.py -v
```

## 算法说明

### 1. 全有全无分配 (All-or-Nothing)

**原理**：基于当前路网状态，为每个OD对计算最短路径，将全部需求分配到最短路径上。

**特点**：
- 计算速度快
- 不考虑拥堵效应
- 适合初始分配

### 2. 增量分配 (Incremental)

**原理**：将总需求分成多份（如40%、30%、20%、10%），逐步分配，每次分配后更新路段行程时间。

**特点**：
- 部分考虑拥堵效应
- 计算效率较高
- 结果介于全有全无和用户均衡之间

### 3. Frank-Wolfe用户均衡 (User Equilibrium)

**原理**：迭代寻找用户均衡状态，使用Frank-Wolfe算法求解。

**迭代步骤**：
1. 全有全无分配得到辅助流量
2. 计算相对间隙判断收敛
3. 线搜索确定最优步长
4. 更新流量并重复

**特点**：
- 达到用户均衡（Wardrop第一原则）
- 收敛性保证
- 计算时间较长但结果最优

## BPR行程时间函数

```
t(q) = t₀ × (1 + q/cap)²
```

其中：
- `t(q)`: 实际行程时间
- `t₀`: 自由流行程时间 = 路段长度 / 最大速度
- `q`: 路段流量
- `cap`: 路段容量

## 数据格式

### network.json
```json
{
    "nodes": {
        "name": ["A", "B", "C", ...],
        "x": [0, 10, 20, ...],
        "y": [0, 0, 0, ...]
    },
    "links": {
        "between": ["AB", "BC", ...],
        "capacity": [1800, 3600, ...],
        "speedmax": [30, 60, ...]
    }
}
```

### demand.json
```json
{
    "from": ["A", "F", ...],
    "to": ["F", "A", ...],
    "amount": [2000, 1000, ...]
}
```

## 输出结果

程序会生成以下文件：

1. `01_network.png` - 路网结构图
2. `02_all_or_nothing.png` - 全有全无分配结果
3. `03_incremental.png` - 增量分配结果
4. `04_frank_wolfe.png` - Frank-Wolfe分配结果
5. `05_convergence.png` - Frank-Wolfe收敛曲线
6. `06_comparison.png` - 算法对比图

## 性能指标

系统计算以下指标：

- **总出行时间**: Σ(flow × travel_time)
- **相对间隙**: Frank-Wolfe收敛指标
- **流量/容量比**: 各路段拥堵程度
- **路段行程时间**: 基于BPR函数

## 可视化说明

### 路网结构图
- 节点：圆形，标注节点名称
- 边：箭头，标注容量和速度

### 流量分配图
- 边宽度：表示流量大小
- 边颜色：
  - 绿色：畅通 (ratio < 0.5)
  - 橙色：拥挤 (0.5 ≤ ratio < 0.8)
  - 红色：拥堵 (ratio ≥ 0.8)

### 收敛曲线
- 左图：相对间隙随迭代变化
- 右图：总出行时间随迭代变化

## 开发规范

### 代码风格
- 遵循PEP 8规范
- 函数单一职责，长度≤30行
- 见名知意的变量命名

### 日志级别
- `INFO`: 关键业务事件
- `DEBUG`: 详细流程追踪
- `WARNING`: 潜在问题
- `ERROR`: 系统错误

### 测试覆盖
- 核心算法单元测试覆盖率 ≥ 90%
- 整体项目测试覆盖率 ≥ 70%

## 作者

电子科技大学学生
课程：交通域划原理
时间：2025年

## 许可证

本项目仅用于课程学习，禁止商业使用。

