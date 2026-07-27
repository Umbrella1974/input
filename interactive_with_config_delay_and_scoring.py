#!/usr/bin/env python3
"""
交互式模式选择（配置延迟 + 评分保存）

功能：
1. 从mode_delays_config.py读取每个模式的默认延迟配置
2. 交互式选择输出模式
3. 使用配置延迟或允许用户覆盖
4. 运行选定的模式
5. 输入评分（非负整数）
6. 将结果保存到CSV文件
"""

import csv
import os
import time
from datetime import datetime

from config import MATRIX1, MATRIX2, OUTPUT_MODES
from matrix_output import (
    single_matrix,
    staggered_matrices,
    sequential_matrices,
    validate_matrices,
)
from mode_delays_config import MODE_DELAYS, get_mode_delay


CSV_FILE = "output_scores.csv"


def print_step_by_step(steps: list, delay: float = 0.5, show_step_info: bool = True):
    """逐步输出步骤结果"""
    if not steps:
        print("  无输出")
        return

    for i, step in enumerate(steps):
        if show_step_info:
            print(f"  步骤 {i + 1}: {step}")
        else:
            print(f"  {step}")
        time.sleep(delay)


def run_mode(mode_name: str, matrix1, matrix2, delay: float = 0.5):
    """运行单个输出模式，返回步骤列表；如果出错返回None。"""
    print(f"\n=== 运行模式: {mode_name} ===")

    if mode_name not in OUTPUT_MODES:
        print(f"  错误: 未知模式 '{mode_name}'")
        return None

    func_name, params = OUTPUT_MODES[mode_name]

    try:
        if func_name == "single_matrix":
            steps = single_matrix(matrix1, **params)
        elif func_name == "staggered_matrices":
            steps = staggered_matrices(matrix1, matrix2, **params)
        elif func_name == "sequential_matrices":
            steps = sequential_matrices(matrix1, matrix2, **params)
        else:
            print(f"  错误: 未知函数 '{func_name}'")
            return None

        print_step_by_step(steps, delay=delay)
        return steps

    except Exception as e:
        print(f"  错误: {e}")
        return None


def get_float(prompt: str, default: float) -> float:
    """获取非负浮点数输入，支持默认值。"""
    while True:
        try:
            user_input = input(f"{prompt} (默认: {default}): ").strip()
            if not user_input:
                return default

            value = float(user_input)
            if value < 0:
                print("  错误: 请输入非负数")
                continue
            return value
        except ValueError:
            print("  错误: 请输入有效的数字")


def get_nonnegative_int(prompt: str, default: int = None) -> int:
    """获取非负整数输入，支持默认值。"""
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
                print("  错误: 请输入非负整数（>=0）")
                continue
            return value
        except ValueError:
            print("  错误: 请输入有效的整数")


def save_to_csv(mode_name: str, delay: float, score: int):
    """将本次运行结果保存到CSV文件。"""
    file_exists = os.path.exists(CSV_FILE)

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(["timestamp", "mode_name", "delay", "score"])

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        writer.writerow([timestamp, mode_name, delay, score])

    print(f"  结果已保存到 {CSV_FILE}")


def show_csv_contents():
    """显示CSV文件内容。"""
    if not os.path.exists(CSV_FILE):
        print(f"  {CSV_FILE} 文件不存在")
        return

    print(f"\n=== {CSV_FILE} 内容 ===")
    with open(CSV_FILE, "r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i == 0:
                print(f"  表头: {row}")
            else:
                print(f"  行{i}: {row}")


def show_mode_delays():
    """按类别显示所有模式及其默认延迟配置。"""
    print("\n=== 模式延迟配置 ===")
    print(f"{'模式名称':<35} {'延迟(秒)':<10}")
    print("-" * 50)

    categories = {
        "A": [],
        "B": [],
        "C": [],
        "D": [],
    }

    for mode, delay in MODE_DELAYS.items():
        if mode.startswith("single_"):
            categories["A"].append((mode, delay))
        elif mode.startswith("staggered_list1_"):
            categories["B"].append((mode, delay))
        elif mode.startswith("staggered_list2_"):
            categories["C"].append((mode, delay))
        elif mode.startswith("sequential_"):
            categories["D"].append((mode, delay))

    category_titles = {
        "A": "类别A: 单个矩阵",
        "B": "类别B: 双矩阵错位 (list1先)",
        "C": "类别C: 双矩阵错位 (list2先)",
        "D": "类别D: 顺序输出",
    }

    for category_name, modes in categories.items():
        if not modes:
            continue

        print(f"\n{category_titles[category_name]}")
        for mode, delay in sorted(modes):
            print(f"  {mode:<35} {delay:<10.2f}")


def choose_delay(mode_name: str) -> float:
    """基于模式默认延迟，让用户选择使用默认值或覆盖。"""
    config_delay = get_mode_delay(mode_name)

    print(f"\n已选择模式: {mode_name}")
    print(f"配置延迟: {config_delay:.2f}秒")

    use_config = input("使用配置延迟？(y/n, 默认y): ").strip().lower()
    if use_config in ("", "y", "yes"):
        print(f"使用配置延迟: {config_delay:.2f}秒")
        return config_delay

    custom_delay = get_float("请输入自定义延迟（秒）", default=config_delay)
    print(f"使用自定义延迟: {custom_delay:.2f}秒")
    return custom_delay


def interactive_mode_selection():
    """交互式模式选择主函数（配置延迟 + 评分保存）。"""
    print("矩阵输出系统 - 配置延迟 + 评分版")
    print(f"矩阵1: {MATRIX1}")
    print(f"矩阵2: {MATRIX2}")

    try:
        validate_matrices(MATRIX1, MATRIX2)
        print("矩阵验证通过")
    except Exception as e:
        print(f"矩阵验证失败: {e}")
        return

    print("\n" + "=" * 60)
    print("交互式模式选择（配置延迟 + 评分保存）")
    print("=" * 60)

    while True:
        print("\n可用命令:")
        print("  'q' - 退出程序")
        print("  'd' - 显示所有模式延迟配置")
        print("  's' - 查看已保存的评分结果")
        print("  'm' - 显示模式列表")
        print("  输入模式名称或编号选择模式")

        print("\n模式列表:")
        modes = sorted(OUTPUT_MODES.keys())
        for i, mode in enumerate(modes):
            delay = get_mode_delay(mode)
            print(f"  {i + 1:3d}. {mode:<35} [延迟: {delay:.2f}秒]")

        choice = input("\n请输入命令或选择模式: ").strip()

        if choice.lower() == "q":
            print("退出程序")
            break
        elif choice.lower() == "d":
            show_mode_delays()
            continue
        elif choice.lower() == "s":
            show_csv_contents()
            continue
        elif choice.lower() == "m":
            continue

        mode_name = None
        if choice.isdigit():
            idx = int(choice) - 1
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

        delay = choose_delay(mode_name)
        steps = run_mode(mode_name, MATRIX1, MATRIX2, delay=delay)

        if steps is None:
            print("  模式运行失败，跳过评分")
            continue

        print(f"\n模式运行完成，共 {len(steps)} 个步骤")
        score = get_nonnegative_int("请为本次运行评分（非负整数）", default=5)
        save_to_csv(mode_name, delay, score)

        print("\n" + "-" * 60)


def main():
    """主函数。"""
    interactive_mode_selection()


if __name__ == "__main__":
    main()
