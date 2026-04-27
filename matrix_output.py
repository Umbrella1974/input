"""
矩阵输出引擎 - 支持多种矩阵输出模式

主要功能：
1. 单个矩阵输出（按列/行，四个方向）
2. 双矩阵错位输出（按列/行，四个方向，可选择哪个矩阵先开始）
3. 双矩阵顺序输出（按列/行，可选择顺序）

支持任意N×N方阵，两个矩阵维度必须一致。
"""

from typing import List, Union, Any, Generator
import time


def get_column(matrix: List[List[Any]], col_idx: int, reverse: bool = False) -> List[Any]:
    """提取矩阵的指定列

    Args:
        matrix: 二维矩阵
        col_idx: 列索引（0-based）
        reverse: 是否反转列元素顺序

    Returns:
        列元素列表
    """
    if not matrix or col_idx < 0 or col_idx >= len(matrix[0]):
        return []

    column = [row[col_idx] for row in matrix]
    if reverse:
        column = column[::-1]
    return column


def get_row(matrix: List[List[Any]], row_idx: int, reverse: bool = False) -> List[Any]:
    """提取矩阵的指定行

    Args:
        matrix: 二维矩阵
        row_idx: 行索引（0-based）
        reverse: 是否反转行元素顺序

    Returns:
        行元素列表
    """
    if not matrix or row_idx < 0 or row_idx >= len(matrix):
        return []

    row = matrix[row_idx][:]
    if reverse:
        row = row[::-1]
    return row


def single_matrix(matrix: List[List[Any]], axis: str = 'col', direction: str = 'l2r') -> List[List[Any]]:
    """单矩阵输出

    Args:
        matrix: 二维矩阵
        axis: 'col'按列输出，'row'按行输出
        direction: 'l2r'从左到右，'r2l'从右到左，
                   't2b'从上到下，'b2t'从下到上

    Returns:
        列表的列表，每个子列表是一个步骤的输出
    """
    if not matrix:
        return []

    n = len(matrix)  # 假设是方阵

    steps = []

    if axis == 'col':
        # 按列输出
        if direction == 'l2r':
            # 从左到右
            for col_idx in range(n):
                steps.append(get_column(matrix, col_idx))
        elif direction == 'r2l':
            # 从右到左
            for col_idx in range(n-1, -1, -1):
                steps.append(get_column(matrix, col_idx))
        elif direction == 't2b':
            # 从上到下（列元素顺序）
            for col_idx in range(n):
                steps.append(get_column(matrix, col_idx, reverse=False))
        elif direction == 'b2t':
            # 从下到上（列元素反转）
            for col_idx in range(n):
                steps.append(get_column(matrix, col_idx, reverse=True))

    elif axis == 'row':
        # 按行输出
        if direction == 'l2r':
            # 从左到右（行元素顺序）
            for row_idx in range(n):
                steps.append(get_row(matrix, row_idx, reverse=False))
        elif direction == 'r2l':
            # 从右到左（行元素反转）
            for row_idx in range(n):
                steps.append(get_row(matrix, row_idx, reverse=True))
        elif direction == 't2b':
            # 从上到下
            for row_idx in range(n):
                steps.append(get_row(matrix, row_idx))
        elif direction == 'b2t':
            # 从下到上
            for row_idx in range(n-1, -1, -1):
                steps.append(get_row(matrix, row_idx))

    return steps


def staggered_matrices(matrix1: List[List[Any]], matrix2: List[List[Any]],
                       axis: str = 'col', direction: str = 'l2r',
                       first: str = 'matrix1') -> List[List[Any]]:
    """双矩阵错位输出

    Args:
        matrix1: 第一个矩阵
        matrix2: 第二个矩阵
        axis: 'col'按列错位，'row'按行错位
        direction: 'l2r'从左到右，'r2l'从右到左，
                   't2b'从上到下，'b2t'从下到上
        first: 'matrix1'或'matrix2'，指定哪个矩阵先开始

    Returns:
        列表的列表，每个子列表是一个步骤的输出
    """
    # 验证矩阵维度
    if not matrix1 or not matrix2:
        return []

    n1, n2 = len(matrix1), len(matrix2)
    if n1 != n2:
        raise ValueError(f"矩阵维度不一致: matrix1 {n1}×{len(matrix1[0])}, matrix2 {n2}×{len(matrix2[0])}")

    # 假设是方阵，检查是否为方阵
    for i in range(n1):
        if len(matrix1[i]) != n1:
            raise ValueError(f"matrix1 不是方阵: 行{i}有{len(matrix1[i])}列，期望{n1}列")
        if len(matrix2[i]) != n1:
            raise ValueError(f"matrix2 不是方阵: 行{i}有{len(matrix2[i])}列，期望{n1}列")

    n = n1  # 矩阵大小
    steps = []

    # 确定索引序列（根据方向）
    if direction in ['l2r', 't2b']:
        # 正向顺序: 0, 1, 2, ..., n-1
        indices = list(range(n))
    else:  # 'r2l', 'b2t'
        # 反向顺序: n-1, n-2, ..., 0
        indices = list(range(n-1, -1, -1))

    # 确定哪个矩阵是first，哪个是second
    if first == 'matrix1':
        first_matrix, second_matrix = matrix1, matrix2
    else:
        first_matrix, second_matrix = matrix2, matrix1

    # 总步骤数: n+1
    for step in range(n + 1):
        step_output = []

        # 确定first_matrix的索引
        first_idx = None
        if step < n:  # 步骤0到n-1：first_matrix有输出
            first_idx = indices[step]

        # 确定second_matrix的索引
        second_idx = None
        if step > 0:  # 步骤1到n：second_matrix有输出
            second_idx = indices[step - 1]

        # 根据axis提取数据
        if axis == 'col':
            # 按列错位
            if first_idx is not None:
                step_output.extend(get_column(first_matrix, first_idx))
            if second_idx is not None:
                step_output.extend(get_column(second_matrix, second_idx))
        else:  # axis == 'row'
            # 按行错位
            if first_idx is not None:
                step_output.extend(get_row(first_matrix, first_idx))
            if second_idx is not None:
                step_output.extend(get_row(second_matrix, second_idx))

        steps.append(step_output)

    return steps


def sequential_matrices(matrix1: List[List[Any]], matrix2: List[List[Any]],
                       axis: str = 'col', order: str = 'matrix1_first') -> List[List[Any]]:
    """双矩阵顺序输出（无交叉）

    Args:
        matrix1: 第一个矩阵
        matrix2: 第二个矩阵
        axis: 'col'按列输出，'row'按行输出
        order: 'matrix1_first'先输出matrix1再输出matrix2，
               'matrix2_first'先输出matrix2再输出matrix1

    Returns:
        列表的列表，每个子列表是一个步骤的输出
    """
    steps = []

    # 确定输出顺序
    if order == 'matrix1_first':
        first, second = matrix1, matrix2
    else:
        first, second = matrix2, matrix1

    # 输出第一个矩阵
    if axis == 'col':
        n = len(first)
        for col_idx in range(n):
            steps.append(get_column(first, col_idx))
        for col_idx in range(n):
            steps.append(get_column(second, col_idx))
    else:  # axis == 'row'
        n = len(first)
        for row_idx in range(n):
            steps.append(get_row(first, row_idx))
        for row_idx in range(n):
            steps.append(get_row(second, row_idx))

    return steps


def validate_matrices(matrix1: List[List[Any]], matrix2: List[List[Any]]) -> bool:
    """验证两个矩阵是否为相同大小的方阵

    Args:
        matrix1: 第一个矩阵
        matrix2: 第二个矩阵

    Returns:
        如果验证通过返回True，否则抛出异常
    """
    if not matrix1 or not matrix2:
        raise ValueError("矩阵不能为空")

    n1 = len(matrix1)
    n2 = len(matrix2)

    if n1 != n2:
        raise ValueError(f"矩阵行数不一致: matrix1有{n1}行, matrix2有{n2}行")

    # 检查matrix1是否为方阵
    for i, row in enumerate(matrix1):
        if len(row) != n1:
            raise ValueError(f"matrix1不是方阵: 行{i}有{len(row)}列，期望{n1}列")

    # 检查matrix2是否为方阵
    for i, row in enumerate(matrix2):
        if len(row) != n1:
            raise ValueError(f"matrix2不是方阵: 行{i}有{len(row)}列，期望{n1}列")

    return True