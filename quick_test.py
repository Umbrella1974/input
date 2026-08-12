#!/usr/bin/env python3
"""
快速验证 - 检查所有输出模式
"""

import sys
sys.path.insert(0, '.')

from matrix_output import single_matrix, staggered_matrices, sequential_matrices, edge_single_matrix, edge_pair_matrices, custom_steps
from config import MATRIX1, MATRIX2, OUTPUT_MODES

def quick_test():
    """快速测试所有模式"""
    print("快速验证所有输出模式...\n")

    # 测试每个类别的一些关键模式
    test_modes = [
        # 类别A: 单个矩阵
        ('single_list1_col_l2r', '单个矩阵list1, 从左到右按列'),
        ('single_list1_col_r2l', '单个矩阵list1, 从右到左按列'),
        ('single_list1_row_l2r', '单个矩阵list1, 从左到右按行'),
        ('single_list1_row_b2t', '单个矩阵list1, 从下到上按行'),

        # 类别B: list1先错位
        ('staggered_list1_first_col_l2r', 'list1先, 从左到右错位列'),
        ('staggered_list1_first_col_r2l', 'list1先, 从右到左错位列'),
        ('staggered_list1_first_row_l2r', 'list1先, 从左到右错位行'),
        ('staggered_list1_first_row_r2l', 'list1先, 从右到左错位行'),

        # 类别C: list2先错位
        ('staggered_list2_first_col_l2r', 'list2先, 从左到右错位列'),
        ('staggered_list2_first_row_l2r', 'list2先, 从左到右错位行'),

        # 类别D: 顺序输出
        ('sequential_list1_then_list2_col', '先list1后list2按列'),
        ('sequential_list2_then_list1_row', '先list2后list1按行'),
    ]

    for mode_name, description in test_modes:
        print(f"\n=== {mode_name} ===")
        print(f"描述: {description}")

        if mode_name not in OUTPUT_MODES:
            print(f"  错误: 模式未定义")
            continue

        func_name, params = OUTPUT_MODES[mode_name]

        try:
            if func_name == 'single_matrix':
                steps = single_matrix(MATRIX1, **params)
            elif func_name == 'staggered_matrices':
                steps = staggered_matrices(MATRIX1, MATRIX2, **params)
            elif func_name == 'sequential_matrices':
                steps = sequential_matrices(MATRIX1, MATRIX2, **params)
            elif func_name == 'edge_single_matrix':
                steps = edge_single_matrix(MATRIX1, MATRIX2, **params)
            elif func_name == 'edge_pair_matrices':
                steps = edge_pair_matrices(MATRIX1, MATRIX2, **params)
            elif func_name == 'custom_steps':
                steps = custom_steps(MATRIX1, MATRIX2, **params)
            else:
                print(f"  错误: 未知函数 {func_name}")
                continue

            print(f"  步骤数: {len(steps)}")
            for i, step in enumerate(steps):
                print(f"    步骤{i}: {step}")

        except Exception as e:
            print(f"  错误: {e}")

    # 特别验证用户描述的核心模式
    print("\n" + "="*60)
    print("用户描述的核心模式验证")
    print("="*60)

    # 模式1: list1先，从左到右错位列
    print("\n1. list1先，从左到右错位列:")
    steps = staggered_matrices(MATRIX1, MATRIX2, axis='col', direction='l2r', first='matrix1')
    for i, step in enumerate(steps):
        print(f"  步骤{i}: {step}")

    # 模式2: list1先，从右到左错位列
    print("\n2. list1先，从右到左错位列:")
    steps = staggered_matrices(MATRIX1, MATRIX2, axis='col', direction='r2l', first='matrix1')
    for i, step in enumerate(steps):
        print(f"  步骤{i}: {step}")

    # 模式3: list1先，从左到右错位行
    print("\n3. list1先，从左到右错位行:")
    steps = staggered_matrices(MATRIX1, MATRIX2, axis='row', direction='l2r', first='matrix1')
    for i, step in enumerate(steps):
        print(f"  步骤{i}: {step}")

    # 模式4: 单个矩阵按行输出
    print("\n4. 单个矩阵按行输出:")
    steps = single_matrix(MATRIX1, axis='row', direction='l2r')
    for i, step in enumerate(steps):
        print(f"  步骤{i}: {step}")

if __name__ == "__main__":
    quick_test()
