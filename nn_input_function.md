## **最终架构设计文档 v2.0**

### **核心设计原则**
1. **对称性**：list1先和list2先的模式完全对称
2. **方向覆盖**：四个基本方向（l2r, r2l, t2b, b2t）
3. **可扩展性**：支持任意N×N矩阵（不只是3×3）
4. **代码复用**：避免冗余，核心逻辑模块化

### **1. 模块化架构**

```
project/
├── config.py          # 配置定义
├── output_engine.py   # 输出逻辑引擎
├── main.py           # 主程序调用
└── dispatcher.py     # 函数调度器（可选）
```

### **2. 配置文件 (config.py)**

#### **2.1 矩阵定义**
```python
MATRIX1 = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]

MATRIX2 = [
    [10, 11, 12],
    [13, 14, 15],
    [16, 17, 18]
]
```

#### **2.2 输出模式配置**
定义模式字典，便于主程序调用：
```python
OUTPUT_MODES = {
    # 类别A: 单个矩阵
    'single_list1_col_l2r': '单个矩阵list1, 从左到右按列',
    'single_list1_col_r2l': '单个矩阵list1, 从右到左按列',
    # ... 其他模式定义
}
```

### **3. 核心引擎 (output_engine.py)**

#### **3.1 基础工具函数**
```python
def print_column(matrix, col_index, direction='down'):
    """按方向输出一列元素"""
    # direction: 'down' 从上到下, 'up' 从下到上

def print_row(matrix, row_index, direction='left'):
    """按方向输出一行元素"""
    # direction: 'left' 从左到右, 'right' 从右到左
```

#### **3.2 通用错位输出函数**
```python
def staggered_columns(matrix1, matrix2, direction='l2r', first='matrix1'):
    """
    通用错位列输出
  
    参数:
    - direction: 'l2r' 或 'r2l'
    - first: 'matrix1' 或 'matrix2' 哪个矩阵先开始
    """
    # 动态计算波次数: 2N-1 (N为矩阵大小)
    # 核心算法:
    #   波次i (0 <= i < 2N-1)
    #   输出: matrix1的列j + matrix2的列k
    #   其中j,k根据i,direction,first动态计算
```

#### **3.3 通用错位行输出函数**
```python
def staggered_rows(matrix1, matrix2, direction='t2b', first='matrix1'):
    """
    通用错位行输出
    """
    # 类似列输出的逻辑
```

### **4. 函数实现策略**

#### **4.1 类别A：单个矩阵**
```python
# 用参数化函数实现，而非16个独立函数
def single_matrix(matrix, axis='col', direction='l2r'):
    """
    单矩阵输出
  
    参数:
    - axis: 'col' 或 'row' (按列/按行)
    - direction: 'l2r', 'r2l', 't2b', 'b2t'
    """
```

#### **4.2 类别B/C：双矩阵错位**
```python
# 用两个参数化的主函数代替8个独立函数
def staggered_two_matrices(matrix1, matrix2, axis='col', direction='l2r', first='matrix1'):
    """
    双矩阵错位输出（核心函数）
  
    参数:
    - axis: 'col' (列) 或 'row' (行)
    - direction: 'l2r', 'r2l', 't2b', 'b2t'
    - first: 'matrix1' 或 'matrix2'
    """
```

#### **4.3 类别D：顺序输出**
```python
def sequential_matrices(matrix1, matrix2, axis='col', order='matrix1_first'):
    """
    顺序输出两个矩阵
  
    参数:
    - axis: 'col' 或 'row'
    - order: 'matrix1_first' 或 'matrix2_first'
    """
```

### **5. 主程序调用接口 (main.py)**

#### **5.1 用户友好调用**
```python
# 使用模式名称直接调用
output_engine.run_mode('single_list1_col_l2r', MATRIX1, MATRIX2)
output_engine.run_mode('staggered_list1_first_col_l2r', MATRIX1, MATRIX2)

# 或使用参数化调用
output_engine.single_matrix(MATRIX1, axis='col', direction='l2r')
```

#### **5.2 批量执行**
```python
# 按类别执行所有模式
CATEGORIES = {
    'A': ['single_list1_col_l2r', 'single_list1_col_r2l', ...],
    'B': ['staggered_list1_first_col_l2r', ...],
    # ...
}

def run_category(category_name):
    for mode in CATEGORIES[category_name]:
        print(f"\n=== 模式: {mode} ===")
        output_engine.run_mode(mode, MATRIX1, MATRIX2)
```

### **6. 扩展功能建议**

#### **6.1 输出格式控制**
```python
def set_output_format(format_type='elements'):
    """
    控制输出格式
  
    format_type:
    - 'elements': 每个元素单独一行
    - 'columns': 每列显示为一行 [x, y, z]
    - 'matrix': 保持矩阵格式
    """
```

#### **6.2 动态矩阵大小支持**
```python
# 所有函数内部使用len(matrix)而不是固定3
n = len(MATRIX1)  # 动态获取矩阵大小
```

#### **6.3 错误处理和验证**
```python
def validate_matrices(matrix1, matrix2):
    """验证两个矩阵维度一致"""
    if len(matrix1) != len(matrix2):
        raise ValueError("矩阵大小不一致")
    # 检查是否为方阵
```

### **7. 优化建议**

1. **字典映射代替多个if-elif**：将模式名称映射到对应的函数或参数
2. **装饰器记录执行**：用装饰器记录每个函数的执行时间和输出次数
3. **结果缓存**：如果矩阵不变，可以缓存计算结果
4. **可选回调**：允许用户提供回调函数处理每个输出元素

### **8. 给Claude Code的指令要点**

基于这个架构，给Claude Code的指令应包括：
1. 实现参数化的核心函数，而不是16个独立函数
2. 确保支持任意N×N矩阵
3. 提供清晰的函数文档和类型提示
4. 添加示例调用和测试用例
5. 实现错误处理和输入验证

这个架构保持了你的所有需求，同时提供了更好的代码组织和可维护性。核心思想是**参数化**和**通用化**，而不是为每个变体写独立的函数。