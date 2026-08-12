"""
配置文件 - 定义矩阵和输出模式映射
"""

# 示例矩阵定义 (3×3)
MATRIX1 = [
    [82, 84, 87],
    [81, 85, 88],
    [83, 86, 89]
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

    # 类别E: 单矩阵边缘行/列输出
    'edge_single_list1_row_top': ('edge_single_matrix', {'matrix': 'matrix1', 'edge': 'top'}),
    'edge_single_list1_row_bottom': ('edge_single_matrix', {'matrix': 'matrix1', 'edge': 'bottom'}),
    'edge_single_list1_col_left': ('edge_single_matrix', {'matrix': 'matrix1', 'edge': 'left'}),
    'edge_single_list1_col_right': ('edge_single_matrix', {'matrix': 'matrix1', 'edge': 'right'}),
    'edge_single_list2_row_top': ('edge_single_matrix', {'matrix': 'matrix2', 'edge': 'top'}),
    'edge_single_list2_row_bottom': ('edge_single_matrix', {'matrix': 'matrix2', 'edge': 'bottom'}),
    'edge_single_list2_col_left': ('edge_single_matrix', {'matrix': 'matrix2', 'edge': 'left'}),
    'edge_single_list2_col_right': ('edge_single_matrix', {'matrix': 'matrix2', 'edge': 'right'}),

    # 类别F: 双矩阵边缘输出，matrix1先
    'edge_pair_list1_then_list2_row_top': ('edge_pair_matrices', {'edge': 'top', 'order': 'matrix1_first'}),
    'edge_pair_list1_then_list2_row_bottom': ('edge_pair_matrices', {'edge': 'bottom', 'order': 'matrix1_first'}),
    'edge_pair_list1_then_list2_col_left': ('edge_pair_matrices', {'edge': 'left', 'order': 'matrix1_first'}),
    'edge_pair_list1_then_list2_col_right': ('edge_pair_matrices', {'edge': 'right', 'order': 'matrix1_first'}),

    # 类别G: 双矩阵边缘输出，matrix2先
    'edge_pair_list2_then_list1_row_top': ('edge_pair_matrices', {'edge': 'top', 'order': 'matrix2_first'}),
    'edge_pair_list2_then_list1_row_bottom': ('edge_pair_matrices', {'edge': 'bottom', 'order': 'matrix2_first'}),
    'edge_pair_list2_then_list1_col_left': ('edge_pair_matrices', {'edge': 'left', 'order': 'matrix2_first'}),
    'edge_pair_list2_then_list1_col_right': ('edge_pair_matrices', {'edge': 'right', 'order': 'matrix2_first'}),

    # Category H: explicit MATRIX1 center/outer two-step modes
    'custom_list1_center_col_then_outer': ('custom_steps', {'steps': [[84, 85, 86], [82, 81, 83, 87, 88, 89]]}),
    'custom_list1_outer_then_center_col': ('custom_steps', {'steps': [[82, 81, 83, 87, 88, 89], [84, 85, 86]]}),
    'custom_list1_center_then_outer': ('custom_steps', {'steps': [[85], [81, 82, 83, 84, 86, 87, 88, 89]]}),
    'custom_list1_outer_then_center': ('custom_steps', {'steps': [[81, 82, 83, 84, 86, 87, 88, 89], [85]]}),
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
    ],
    'E': [
        'edge_single_list1_row_top',
        'edge_single_list1_row_bottom',
        'edge_single_list1_col_left',
        'edge_single_list1_col_right',
        'edge_single_list2_row_top',
        'edge_single_list2_row_bottom',
        'edge_single_list2_col_left',
        'edge_single_list2_col_right',
    ],
    'F': [
        'edge_pair_list1_then_list2_row_top',
        'edge_pair_list1_then_list2_row_bottom',
        'edge_pair_list1_then_list2_col_left',
        'edge_pair_list1_then_list2_col_right',
    ],
    'G': [
        'edge_pair_list2_then_list1_row_top',
        'edge_pair_list2_then_list1_row_bottom',
        'edge_pair_list2_then_list1_col_left',
        'edge_pair_list2_then_list1_col_right',
    ],
    'H': [
        'custom_list1_center_col_then_outer',
        'custom_list1_outer_then_center_col',
        'custom_list1_center_then_outer',
        'custom_list1_outer_then_center',
    ],
}
