#!/usr/bin/env python3
"""
演示脚本 - 展示所有矩阵输出模式
"""

import time
from matrix_output import single_matrix, staggered_matrices, sequential_matrices, validate_matrices
from config import MATRIX1, MATRIX2, OUTPUT_MODES, CATEGORIES


def print_step_by_step(steps: list, delay: float = 0.5, show_step_info: bool = True):
    """逐步输出步骤结果

    Args:
        steps: 步骤列表，每个步骤是一个子列表
        delay: 每一步之间的延迟（秒）
        show_step_info: 是否显示步骤信息
    """
    if not steps:
        print("  无输出")
        return

    for i, step in enumerate(steps):
        if show_step_info:
            print(f"  步骤 {i+1}: {step}")
        else:
            print(f"  {step}")
        time.sleep(delay)


def run_mode(mode_name: str, matrix1, matrix2, delay: float = 0.5):
    """运行单个输出模式

    Args:
        mode_name: 模式名称（来自OUTPUT_MODES）
        matrix1: 第一个矩阵
        matrix2: 第二个矩阵
        delay: 输出延迟
    """
    print(f"\n=== 模式: {mode_name} ===")

    if mode_name not in OUTPUT_MODES:
        print(f"  错误: 未知模式 '{mode_name}'")
        return

    func_name, params = OUTPUT_MODES[mode_name]

    try:
        # 根据函数名调用相应的函数
        if func_name == 'single_matrix':
            # 单矩阵模式只使用matrix1
            steps = single_matrix(matrix1, **params)
        elif func_name == 'staggered_matrices':
            steps = staggered_matrices(matrix1, matrix2, **params)
        elif func_name == 'sequential_matrices':
            steps = sequential_matrices(matrix1, matrix2, **params)
        else:
            print(f"  错误: 未知函数 '{func_name}'")
            return

        # 逐步输出
        print_step_by_step(steps, delay=delay)

    except Exception as e:
        print(f"  错误: {e}")


def run_category(category: str, matrix1, matrix2, delay: float = 0.3):
    """运行一个类别的所有模式

    Args:
        category: 类别名称 ('A', 'B', 'C', 'D')
        matrix1: 第一个矩阵
        matrix2: 第二个矩阵
        delay: 输出延迟
    """
    if category not in CATEGORIES:
        print(f"错误: 未知类别 '{category}'")
        return

    print(f"\n{'='*60}")
    print(f"运行类别 {category}")
    print(f"{'='*60}")

    mode_names = CATEGORIES[category]
    for mode_name in mode_names:
        run_mode(mode_name, matrix1, matrix2, delay=delay)


def main():
    """主函数"""
    print("矩阵输出系统演示")
    print(f"矩阵1: {MATRIX1}")
    print(f"矩阵2: {MATRIX2}")

    try:
        # 验证矩阵
        validate_matrices(MATRIX1, MATRIX2)
        print("矩阵验证通过")
    except Exception as e:
        print(f"矩阵验证失败: {e}")
        return

    # 示例1: 演示单个重要模式
    print("\n" + "="*60)
    print("示例1: 关键模式演示")
    print("="*60)

    # 用户描述的核心模式
    key_modes = [
        'staggered_list1_first_col_l2r',  # list1先，从左到右错位列
        'staggered_list1_first_col_r2l',  # list1先，从右到左错位列
        'staggered_list1_first_row_l2r',  # list1先，从左到右错位行
        'single_list1_row_l2r',           # 单个矩阵按行输出
    ]

    for mode in key_modes:
        run_mode(mode, MATRIX1, MATRIX2, delay=0.5)

    # 示例2: 按类别运行所有模式（快速演示）
    print("\n" + "="*60)
    print("示例2: 按类别快速演示（延迟0.2秒）")
    print("="*60)

    # 只运行类别A和B作为示例
    run_category('A', MATRIX1, MATRIX2, delay=0.2)
    run_category('B', MATRIX1, MATRIX2, delay=0.2)

    # 示例3: 交互式选择模式
    print("\n" + "="*60)
    print("示例3: 交互式模式选择")
    print("="*60)

    while True:
        print("\n可用模式:")
        for i, mode in enumerate(sorted(OUTPUT_MODES.keys())):
            print(f"  {i+1:3d}. {mode}")

        print("\n输入模式名称或编号（输入 'q' 退出）:")
        choice = input("> ").strip()

        if choice.lower() == 'q':
            break

        if choice.isdigit():
            idx = int(choice) - 1
            modes = sorted(OUTPUT_MODES.keys())
            if 0 <= idx < len(modes):
                mode_name = modes[idx]
            else:
                print("  错误: 编号超出范围")
                continue
        else:
            mode_name = choice

        if mode_name not in OUTPUT_MODES:
            print(f"  错误: 未知模式 '{mode_name}'")
            continue

        run_mode(mode_name, MATRIX1, MATRIX2, delay=1)


if __name__ == "__main__":
    main()