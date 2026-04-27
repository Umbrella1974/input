"""
配置文件 - 定义矩阵和输出模式映射
"""

# 示例矩阵定义 (3×3)
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

# 输出模式配置
# 格式: 模式名称: (函数名, 参数字典)
OUTPUT_MODES = {
    # 类别A: 单个矩阵
    'single_list1_col_l2r': ('single_matrix', {'axis': 'col', 'direction': 'l2r'}),
    'single_list1_col_r2l': ('single_matrix', {'axis': 'col', 'direction': 'r2l'}),
    'single_list1_col_t2b': ('single_matrix', {'axis': 'col', 'direction': 't2b'}),
    'single_list1_col_b2t': ('single_matrix', {'axis': 'col', 'direction': 'b2t'}),

    'single_list1_row_l2r': ('single_matrix', {'axis': 'row', 'direction': 'l2r'}),
    'single_list1_row_r2l': ('single_matrix', {'axis': 'row', 'direction': 'r2l'}),
    'single_list1_row_t2b': ('single_matrix', {'axis': 'row', 'direction': 't2b'}),
    'single_list1_row_b2t': ('single_matrix', {'axis': 'row', 'direction': 'b2t'}),

    # 类别B: 双矩阵错位，matrix1先
    'staggered_list1_first_col_l2r': ('staggered_matrices', {'axis': 'col', 'direction': 'l2r', 'first': 'matrix1'}),
    'staggered_list1_first_col_r2l': ('staggered_matrices', {'axis': 'col', 'direction': 'r2l', 'first': 'matrix1'}),
    'staggered_list1_first_col_t2b': ('staggered_matrices', {'axis': 'col', 'direction': 't2b', 'first': 'matrix1'}),
    'staggered_list1_first_col_b2t': ('staggered_matrices', {'axis': 'col', 'direction': 'b2t', 'first': 'matrix1'}),

    'staggered_list1_first_row_l2r': ('staggered_matrices', {'axis': 'row', 'direction': 'l2r', 'first': 'matrix1'}),
    'staggered_list1_first_row_r2l': ('staggered_matrices', {'axis': 'row', 'direction': 'r2l', 'first': 'matrix1'}),
    'staggered_list1_first_row_t2b': ('staggered_matrices', {'axis': 'row', 'direction': 't2b', 'first': 'matrix1'}),
    'staggered_list1_first_row_b2t': ('staggered_matrices', {'axis': 'row', 'direction': 'b2t', 'first': 'matrix1'}),

    # 类别C: 双矩阵错位，matrix2先
    'staggered_list2_first_col_l2r': ('staggered_matrices', {'axis': 'col', 'direction': 'l2r', 'first': 'matrix2'}),
    'staggered_list2_first_col_r2l': ('staggered_matrices', {'axis': 'col', 'direction': 'r2l', 'first': 'matrix2'}),
    'staggered_list2_first_col_t2b': ('staggered_matrices', {'axis': 'col', 'direction': 't2b', 'first': 'matrix2'}),
    'staggered_list2_first_col_b2t': ('staggered_matrices', {'axis': 'col', 'direction': 'b2t', 'first': 'matrix2'}),

    'staggered_list2_first_row_l2r': ('staggered_matrices', {'axis': 'row', 'direction': 'l2r', 'first': 'matrix2'}),
    'staggered_list2_first_row_r2l': ('staggered_matrices', {'axis': 'row', 'direction': 'r2l', 'first': 'matrix2'}),
    'staggered_list2_first_row_t2b': ('staggered_matrices', {'axis': 'row', 'direction': 't2b', 'first': 'matrix2'}),
    'staggered_list2_first_row_b2t': ('staggered_matrices', {'axis': 'row', 'direction': 'b2t', 'first': 'matrix2'}),

    # 类别D: 双矩阵顺序输出
    'sequential_list1_then_list2_col': ('sequential_matrices', {'axis': 'col', 'order': 'matrix1_first'}),
    'sequential_list1_then_list2_row': ('sequential_matrices', {'axis': 'row', 'order': 'matrix1_first'}),
    'sequential_list2_then_list1_col': ('sequential_matrices', {'axis': 'col', 'order': 'matrix2_first'}),
    'sequential_list2_then_list1_row': ('sequential_matrices', {'axis': 'row', 'order': 'matrix2_first'}),
}

# 模式分类
CATEGORIES = {
    'A': [
        'single_list1_col_l2r',
        'single_list1_col_r2l',
        'single_list1_col_t2b',
        'single_list1_col_b2t',
        'single_list1_row_l2r',
        'single_list1_row_r2l',
        'single_list1_row_t2b',
        'single_list1_row_b2t',
    ],
    'B': [
        'staggered_list1_first_col_l2r',
        'staggered_list1_first_col_r2l',
        'staggered_list1_first_col_t2b',
        'staggered_list1_first_col_b2t',
        'staggered_list1_first_row_l2r',
        'staggered_list1_first_row_r2l',
        'staggered_list1_first_row_t2b',
        'staggered_list1_first_row_b2t',
    ],
    'C': [
        'staggered_list2_first_col_l2r',
        'staggered_list2_first_col_r2l',
        'staggered_list2_first_col_t2b',
        'staggered_list2_first_col_b2t',
        'staggered_list2_first_row_l2r',
        'staggered_list2_first_row_r2l',
        'staggered_list2_first_row_t2b',
        'staggered_list2_first_row_b2t',
    ],
    'D': [
        'sequential_list1_then_list2_col',
        'sequential_list1_then_list2_row',
        'sequential_list2_then_list1_col',
        'sequential_list2_then_list1_row',
    ]
}