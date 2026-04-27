#!/usr/bin/env python3
"""
测试脚本 - 验证矩阵输出功能
"""

import sys
sys.path.insert(0, '.')

from matrix_output import (
    get_column, get_row,
    single_matrix,
    staggered_matrices,
    sequential_matrices,
    validate_matrices
)

# 测试矩阵
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


def test_basic_functions():
    """测试基础函数"""
    print("测试基础函数...")

    # 测试get_column
    col0 = get_column(MATRIX1, 0)
    assert col0 == [1, 4, 7], f"get_column错误: {col0}"

    col1 = get_column(MATRIX1, 1)
    assert col1 == [2, 5, 8], f"get_column错误: {col1}"

    # 测试get_row
    row0 = get_row(MATRIX1, 0)
    assert row0 == [1, 2, 3], f"get_row错误: {row0}"

    row2 = get_row(MATRIX1, 2)
    assert row2 == [7, 8, 9], f"get_row错误: {row2}"

    print("  基础函数测试通过")


def test_single_matrix():
    """测试单矩阵输出"""
    print("\n测试单矩阵输出...")

    # 按列从左到右
    steps = single_matrix(MATRIX1, axis='col', direction='l2r')
    expected = [[1, 4, 7], [2, 5, 8], [3, 6, 9]]
    assert steps == expected, f"single_matrix(col, l2r)错误: {steps}"
    print("  single_matrix(col, l2r) 通过")

    # 按列从右到左
    steps = single_matrix(MATRIX1, axis='col', direction='r2l')
    expected = [[3, 6, 9], [2, 5, 8], [1, 4, 7]]
    assert steps == expected, f"single_matrix(col, r2l)错误: {steps}"
    print("  single_matrix(col, r2l) 通过")

    # 按行从上到下
    steps = single_matrix(MATRIX1, axis='row', direction='t2b')
    expected = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    assert steps == expected, f"single_matrix(row, t2b)错误: {steps}"
    print("  single_matrix(row, t2b) 通过")

    # 按行从下到上
    steps = single_matrix(MATRIX1, axis='row', direction='b2t')
    expected = [[7, 8, 9], [4, 5, 6], [1, 2, 3]]
    assert steps == expected, f"single_matrix(row, b2t)错误: {steps}"
    print("  single_matrix(row, b2t) 通过")


def test_staggered_matrices():
    """测试错位输出"""
    print("\n测试错位输出...")

    # list1先，从左到右按列
    steps = staggered_matrices(MATRIX1, MATRIX2, axis='col', direction='l2r', first='matrix1')
    print(f"  staggered(list1先, col, l2r): {steps}")

    # 验证步骤数应该是 n+1 = 4
    assert len(steps) == 4, f"步骤数错误: {len(steps)}"

    # 验证具体输出
    # 步骤0: L1列1 = [1,4,7]
    assert steps[0] == [1, 4, 7], f"步骤0错误: {steps[0]}"
    # 步骤1: L1列2+L2列1 = [2,5,8,10,13,16]
    assert steps[1] == [2, 5, 8, 10, 13, 16], f"步骤1错误: {steps[1]}"
    # 步骤2: L1列3+L2列2 = [3,6,9,11,14,17]
    assert steps[2] == [3, 6, 9, 11, 14, 17], f"步骤2错误: {steps[2]}"
    # 步骤3: L2列3 = [12,15,18]
    assert steps[3] == [12, 15, 18], f"步骤3错误: {steps[3]}"

    print("  staggered(list1先, col, l2r) 通过")

    # list1先，从右到左按列
    steps = staggered_matrices(MATRIX1, MATRIX2, axis='col', direction='r2l', first='matrix1')
    print(f"  staggered(list1先, col, r2l): {steps}")

    # 步骤0: L1列3 = [3,6,9]
    assert steps[0] == [3, 6, 9], f"步骤0错误: {steps[0]}"
    # 步骤1: L1列2+L2列3 = [2,5,8,12,15,18]
    assert steps[1] == [2, 5, 8, 12, 15, 18], f"步骤1错误: {steps[1]}"
    # 步骤2: L1列1+L2列2 = [1,4,7,11,14,17]
    assert steps[2] == [1, 4, 7, 11, 14, 17], f"步骤2错误: {steps[2]}"
    # 步骤3: L2列1 = [10,13,16]
    assert steps[3] == [10, 13, 16], f"步骤3错误: {steps[3]}"

    print("  staggered(list1先, col, r2l) 通过")

    # list2先，从左到右按列
    steps = staggered_matrices(MATRIX1, MATRIX2, axis='col', direction='l2r', first='matrix2')
    print(f"  staggered(list2先, col, l2r): {steps}")

    # 步骤0: L2列1 = [10,13,16]
    assert steps[0] == [10, 13, 16], f"步骤0错误: {steps[0]}"
    # 步骤1: L2列2+L1列1 = [11,14,17,1,4,7]
    assert steps[1] == [11, 14, 17, 1, 4, 7], f"步骤1错误: {steps[1]}"
    # 步骤2: L2列3+L1列2 = [12,15,18,2,5,8]
    assert steps[2] == [12, 15, 18, 2, 5, 8], f"步骤2错误: {steps[2]}"
    # 步骤3: L1列3 = [3,6,9]
    assert steps[3] == [3, 6, 9], f"步骤3错误: {steps[3]}"

    print("  staggered(list2先, col, l2r) 通过")


def test_sequential_matrices():
    """测试顺序输出"""
    print("\n测试顺序输出...")

    # list1先，按列
    steps = sequential_matrices(MATRIX1, MATRIX2, axis='col', order='matrix1_first')
    print(f"  sequential(list1先, col): {steps}")

    # 应该先输出list1的所有列，再输出list2的所有列
    assert len(steps) == 6, f"步骤数错误: {len(steps)}"
    assert steps[0] == [1, 4, 7], f"步骤0错误: {steps[0]}"
    assert steps[1] == [2, 5, 8], f"步骤1错误: {steps[1]}"
    assert steps[2] == [3, 6, 9], f"步骤2错误: {steps[2]}"
    assert steps[3] == [10, 13, 16], f"步骤3错误: {steps[3]}"
    assert steps[4] == [11, 14, 17], f"步骤4错误: {steps[4]}"
    assert steps[5] == [12, 15, 18], f"步骤5错误: {steps[5]}"

    print("  sequential(list1先, col) 通过")


def test_validation():
    """测试矩阵验证"""
    print("\n测试矩阵验证...")

    try:
        validate_matrices(MATRIX1, MATRIX2)
        print("  验证通过")
    except Exception as e:
        print(f"  验证失败: {e}")

    # 测试非方阵
    non_square = [[1, 2], [3, 4], [5, 6]]
    try:
        validate_matrices(MATRIX1, non_square)
        print("  错误: 应该检测到非方阵")
    except ValueError as e:
        print(f"  正确检测到非方阵: {e}")


def main():
    """运行所有测试"""
    print("开始矩阵输出测试...")

    test_basic_functions()
    test_single_matrix()
    test_staggered_matrices()
    test_sequential_matrices()
    test_validation()

    print("\n所有测试通过！")


if __name__ == "__main__":
    main()