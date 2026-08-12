#!/usr/bin/env python3
"""
交互式模式选择并评分 - 扩展demo.py的交互功能

功能：
1. 交互式选择输出模式
2. 输入自定义delay值
3. 运行选定的模式
4. 输入评分（正整数）
5. 将结果保存到CSV文件
"""

import time
import csv
import os
from datetime import datetime
from matrix_output import single_matrix, staggered_matrices, sequential_matrices, edge_single_matrix, edge_pair_matrices, custom_steps, validate_matrices
from config import MATRIX1, MATRIX2, OUTPUT_MODES

CSV_FILE = "output_scores.csv"


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

    Returns:
        步骤列表，如果出错返回None
    """
    print(f"\n=== 运行模式: {mode_name} ===")

    if mode_name not in OUTPUT_MODES:
        print(f"  错误: 未知模式 '{mode_name}'")
        return None

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
        elif func_name == 'edge_single_matrix':
            steps = edge_single_matrix(matrix1, matrix2, **params)
        elif func_name == 'edge_pair_matrices':
            steps = edge_pair_matrices(matrix1, matrix2, **params)
        elif func_name == 'custom_steps':
            steps = custom_steps(matrix1, matrix2, **params)
        else:
            print(f"  错误: 未知函数 '{func_name}'")
            return None

        # 逐步输出
        print_step_by_step(steps, delay=delay)
        return steps

    except Exception as e:
        print(f"  错误: {e}")
        return None


def get_nonnegative_int(prompt: str, default: int = None) -> int:
    """获取非负整数输入（包含0）

    Args:
        prompt: 提示信息
        default: 默认值（可选）

    Returns:
        非负整数
    """
    while True:
        try:
            if default is not None:
                user_input = input(f"{prompt} (默认: {default}): ").strip()
                if not user_input:
                    return default
            else:
                user_input = input(f"{prompt}: ").strip()

            value = int(user_input)
            if value < 0:
                print("  错误: 请输入非负整数（≥0）")
                continue
            return value
        except ValueError:
            print("  错误: 请输入有效的整数")


def get_float(prompt: str, default: float = None) -> float:
    """获取浮点数输入

    Args:
        prompt: 提示信息
        default: 默认值（可选）

    Returns:
        浮点数
    """
    while True:
        try:
            if default is not None:
                user_input = input(f"{prompt} (默认: {default}): ").strip()
                if not user_input:
                    return default
            else:
                user_input = input(f"{prompt}: ").strip()

            value = float(user_input)
            if value < 0:
                print("  错误: 请输入非负数")
                continue
            return value
        except ValueError:
            print("  错误: 请输入有效的数字")


def save_to_csv(mode_name: str, delay: float, score: int):
    """将结果保存到CSV文件

    Args:
        mode_name: 模式名称
        delay: 延迟时间（秒）
        score: 评分（非负整数）
    """
    # 检查文件是否存在，如果不存在则创建并写入表头
    file_exists = os.path.exists(CSV_FILE)

    with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # 如果文件不存在，写入表头
        if not file_exists:
            writer.writerow(['timestamp', 'mode_name', 'delay', 'score'])

        # 写入数据行
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        writer.writerow([timestamp, mode_name, delay, score])

    print(f"  结果已保存到 {CSV_FILE}")


def show_csv_contents():
    """显示CSV文件内容"""
    if not os.path.exists(CSV_FILE):
        print(f"  {CSV_FILE} 文件不存在")
        return

    print(f"\n=== {CSV_FILE} 内容 ===")
    with open(CSV_FILE, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i == 0:
                print(f"  表头: {row}")
            else:
                print(f"  行{i}: {row}")


def interactive_mode_selection():
    """交互式模式选择主函数"""
    print("矩阵输出系统 - 交互式评分版")
    print(f"矩阵1: {MATRIX1}")
    print(f"矩阵2: {MATRIX2}")

    try:
        # 验证矩阵
        validate_matrices(MATRIX1, MATRIX2)
        print("矩阵验证通过")
    except Exception as e:
        print(f"矩阵验证失败: {e}")
        return

    print("\n" + "="*60)
    print("交互式模式选择与评分")
    print("="*60)

    while True:
        print("\n可用模式:")
        for i, mode in enumerate(sorted(OUTPUT_MODES.keys())):
            print(f"  {i+1:3d}. {mode}")

        print("\n命令:")
        print("  'q' - 退出程序")
        print("  's' - 查看已保存的结果")
        print("  'm' - 显示模式列表")
        print("  输入模式名称或编号选择模式")

        choice = input("\n请输入命令或选择模式: ").strip()

        if choice.lower() == 'q':
            print("退出程序")
            break
        elif choice.lower() == 's':
            show_csv_contents()
            continue
        elif choice.lower() == 'm':
            # 重新显示模式列表
            continue

        # 解析模式选择
        mode_name = None
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

        # 获取delay值
        print(f"\n已选择模式: {mode_name}")
        delay = get_float("请输入输出延迟（秒）", default=0.5)

        # 运行模式
        steps = run_mode(mode_name, MATRIX1, MATRIX2, delay=delay)

        if steps is None:
            print("  模式运行失败，跳过评分")
            continue

        # 获取评分
        print(f"\n模式运行完成，共 {len(steps)} 个步骤")
        score = get_nonnegative_int("请为本次运行评分（非负整数，0-10）", default=5)

        # 保存结果
        save_to_csv(mode_name, delay, score)

        print("\n" + "-"*40)


def main():
    """主函数"""
    interactive_mode_selection()


if __name__ == "__main__":
    main()
