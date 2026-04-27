# 矩阵输出系统

这是一个灵活的矩阵输出系统，支持多种输出模式，包括单个矩阵输出、双矩阵错位输出和顺序输出。系统采用参数化设计，支持任意N×N方阵。

## 项目概述

系统基于用户的需求开发：实现3×3矩阵（可扩展为4×4）的多种输出模式。输出为列表形式，每个步骤的输出作为一个子列表，系统支持逐步输出（带时间延迟）。

### 核心功能
- 单个矩阵输出（按列/行，四个方向）
- 双矩阵错位输出（按列/行，四个方向，可选择哪个矩阵先开始）
- 双矩阵顺序输出（按列/行，可选择顺序）
- 支持任意N×N方阵（两个矩阵维度必须一致）
- 交互式模式选择和评分
- 配置化的延迟设置

## 文件结构

```
D:\research_history\first_one\research_code\input\input_function\
├── matrix_output.py          # 核心输出引擎
├── config.py                # 矩阵定义和模式映射配置
├── mode_delays_config.py    # 模式延迟配置文件
├── demo.py                  # 演示脚本（基础交互）
├── interactive_with_scoring.py      # 交互式评分版本（带CSV记录）
├── interactive_with_config_delay.py # 配置延迟交互版本
├── test.py                  # 单元测试
├── quick_test.py            # 快速验证脚本
├── 33input_function.md      # 原始需求文档
└── nn_input_function.md     # 架构设计文档
```

## 核心模块说明

### 1. matrix_output.py
核心输出引擎，包含以下主要函数：

```python
# 基础工具函数
get_column(matrix, col_idx, reverse=False)  # 提取矩阵列
get_row(matrix, row_idx, reverse=False)     # 提取矩阵行

# 主要输出函数
single_matrix(matrix, axis='col', direction='l2r')  # 单矩阵输出
staggered_matrices(matrix1, matrix2, axis='col', direction='l2r', first='matrix1')  # 双矩阵错位输出
sequential_matrices(matrix1, matrix2, axis='col', order='matrix1_first')  # 双矩阵顺序输出

# 验证函数
validate_matrices(matrix1, matrix2)  # 验证矩阵是否为相同大小的方阵
```

**参数说明：**
- `axis`: 'col'（按列）或 'row'（按行）
- `direction`: 'l2r'（左到右）、'r2l'（右到左）、't2b'（上到下）、'b2t'（下到上）
- `first`: 'matrix1' 或 'matrix2'（指定哪个矩阵先开始）
- `order`: 'matrix1_first' 或 'matrix2_first'（顺序输出的顺序）

### 2. config.py
定义示例矩阵和输出模式映射：

```python
# 示例3×3矩阵
MATRIX1 = [[1,2,3],[4,5,6],[7,8,9]]
MATRIX2 = [[10,11,12],[13,14,15],[16,17,18]]

# 16种输出模式映射
OUTPUT_MODES = {
    'single_list1_col_l2r': ('single_matrix', {'axis': 'col', 'direction': 'l2r'}),
    'staggered_list1_first_col_l2r': ('staggered_matrices', {'axis': 'col', 'direction': 'l2r', 'first': 'matrix1'}),
    # ... 其他模式
}

# 模式分类
CATEGORIES = {
    'A': ['single_list1_col_l2r', ...],  # 单个矩阵
    'B': ['staggered_list1_first_col_l2r', ...],  # list1先错位
    'C': ['staggered_list2_first_col_l2r', ...],  # list2先错位
    'D': ['sequential_list1_then_list2_col', ...]  # 顺序输出
}
```

### 3. mode_delays_config.py
为每个输出模式配置默认延迟时间：

```python
MODE_DELAYS = {
    'single_list1_col_l2r': 0.3,
    'staggered_list1_first_col_l2r': 0.5,
    'staggered_list1_first_row_l2r': 0.6,
    # ... 其他模式
}
DEFAULT_DELAY = 0.5
```

## 输出模式分类

系统支持4大类共16种输出模式：

### 类别A：单个矩阵输出（4种方向×2种轴=8种）
- `single_list1_col_l2r` - list1从左到右按列
- `single_list1_col_r2l` - list1从右到左按列
- `single_list1_row_l2r` - list1从左到右按行
- `single_list1_row_b2t` - list1从下到上按行
- ... 其他组合

### 类别B：双矩阵错位输出，list1先（4种方向×2种轴=8种）
- `staggered_list1_first_col_l2r` - list1先，从左到右错位列
- `staggered_list1_first_col_r2l` - list1先，从右到左错位列
- `staggered_list1_first_row_l2r` - list1先，从左到右错位行
- ... 其他组合

### 类别C：双矩阵错位输出，list2先（4种方向×2种轴=8种）
- `staggered_list2_first_col_l2r` - list2先，从左到右错位列
- `staggered_list2_first_row_l2r` - list2先，从左到右错位行
- ... 其他组合

### 类别D：双矩阵顺序输出（2种顺序×2种轴=4种）
- `sequential_list1_then_list2_col` - 先list1后list2按列
- `sequential_list2_then_list1_row` - 先list2后list1按行
- ... 其他组合

## 使用方式

### 1. 直接调用核心函数
```python
from matrix_output import single_matrix, staggered_matrices
from config import MATRIX1, MATRIX2

# 单个矩阵输出
steps = single_matrix(MATRIX1, axis='col', direction='l2r')

# 双矩阵错位输出（list1先，从左到右按列）
steps = staggered_matrices(MATRIX1, MATRIX2, axis='col', direction='l2r', first='matrix1')
```

### 2. 使用演示脚本
```bash
# 基础演示（包含交互式选择）
python demo.py

# 快速验证所有模式
python quick_test.py

# 运行单元测试
python test.py
```

### 3. 交互式评分版本
```bash
# 运行交互式评分版本
python interactive_with_scoring.py

# 功能特点：
# - 选择模式后输入自定义delay值
# - 运行模式输出矩阵
# - 完成后输入score（非负整数，包含0）
# - 自动保存结果到output_scores.csv
# - 支持查看历史记录（命令 's'）
```

### 4. 配置延迟交互版本
```bash
# 运行配置延迟交互版本
python interactive_with_config_delay.py

# 功能特点：
# - 从mode_delays_config.py读取每个模式的默认延迟
# - 可选择使用配置延迟或输入自定义延迟
# - 支持查看所有模式延迟配置（命令 'd'）
```

## 输出示例

### 错位输出示例（list1先，从左到右按列）：
```
步骤1: [1, 4, 7]                    # L1列1
步骤2: [2, 5, 8, 10, 13, 16]        # L1列2 + L2列1
步骤3: [3, 6, 9, 11, 14, 17]        # L1列3 + L2列2  
步骤4: [12, 15, 18]                 # L2列3
```

**注意**：输出是列表的拼接（append），不是数值相加。

### 单个矩阵输出示例（从左到右按行）：
```
步骤1: [1, 2, 3]                    # L1行1
步骤2: [4, 5, 6]                    # L1行2
步骤3: [7, 8, 9]                    # L1行3
```

## 扩展和定制

### 1. 修改矩阵数据
编辑 `config.py` 中的 `MATRIX1` 和 `MATRIX2` 定义。

### 2. 添加新的输出模式
在 `config.py` 的 `OUTPUT_MODES` 字典中添加新的模式映射。

### 3. 调整延迟配置
编辑 `mode_delays_config.py` 中的 `MODE_DELAYS` 字典。

### 4. 支持非方阵
当前系统要求输入为相同大小的方阵。要支持矩形矩阵，需要修改 `validate_matrices()` 函数和相关逻辑。

## 设计原则

1. **参数化设计**：使用参数化函数代替多个独立函数，提高代码复用性
2. **可扩展性**：支持任意N×N矩阵，不仅仅是3×3
3. **模块化架构**：核心逻辑、配置、演示脚本分离
4. **交互友好**：提供多种交互方式，支持配置和评分

## 测试验证

系统包含完整的测试用例：

```bash
# 运行所有测试
python test.py

# 测试输出：
# 基础函数测试通过
# 单矩阵输出测试通过
# 错位输出测试通过
# 顺序输出测试通过
# 矩阵验证测试通过
```

## 注意事项

1. **矩阵验证**：系统要求两个矩阵为相同大小的方阵，否则会抛出异常
2. **输出格式**：每个步骤的输出是一个列表，多列/行输出时是列表的拼接
3. **延迟控制**：演示脚本中的延迟是模拟逐步输出效果，实际函数调用立即返回所有步骤
4. **CSV文件**：评分版本的结果保存在 `output_scores.csv`，包含时间戳、模式名称、延迟和评分

## 依赖要求

- Python 3.6+
- 仅使用标准库，无需额外安装包

## 未来扩展建议

1. **可视化输出**：添加图形化界面显示矩阵和输出过程
2. **性能优化**：对于大型矩阵优化输出算法
3. **更多输出模式**：添加旋转、对角线等输出方式
4. **批处理支持**：支持批量处理多个矩阵对
5. **数据分析**：对评分结果进行统计分析