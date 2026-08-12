#!/usr/bin/env python3
"""
交互式模式选择（带配置延迟） - 使用配置文件设置每个模式的默认延迟

功能：
1. 从mode_delays_config.py读取每个模式的默认延迟配置
2. 交互式选择输出模式
3. 使用配置的延迟或允许用户覆盖
4. 运行选定的模式
"""

import time
from matrix_output import single_matrix, staggered_matrices, sequential_matrices, edge_single_matrix, edge_pair_matrices, custom_steps, validate_matrices
from config import MATRIX1, MATRIX2, OUTPUT_MODES
from mode_delays_config import get_mode_delay


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


def get_float(prompt: str, default: float) -> float:
    """获取浮点数输入，支持默认值

    Args:
        prompt: 提示信息
        default: 默认值

    Returns:
        浮点数
    """
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


def show_mode_delays():
    """显示所有模式及其延迟配置"""
    from mode_delays_config import MODE_DELAYS

    print("\n=== 模式延迟配置 ===")
    print(f"{'模式名称':<35} {'延迟(秒)':<10}")
    print("-" * 50)

    # 按类别显示
    categories = {
        'A': [],
        'B': [],
        'C': [],
        'D': [],
        'E': [],
        'F': [],
        'G': [],
        'H': []
    }

    # 分类模式
    for mode, delay in MODE_DELAYS.items():
        if mode.startswith('single_'):
            categories['A'].append((mode, delay))
        elif mode.startswith('staggered_list1_'):
            categories['B'].append((mode, delay))
        elif mode.startswith('staggered_list2_'):
            categories['C'].append((mode, delay))
        elif mode.startswith('sequential_'):
            categories['D'].append((mode, delay))
        elif mode.startswith('edge_single_'):
            categories['E'].append((mode, delay))
        elif mode.startswith('edge_pair_list1_'):
            categories['F'].append((mode, delay))
        elif mode.startswith('edge_pair_list2_'):
            categories['G'].append((mode, delay))
        elif mode.startswith('custom_'):
            categories['H'].append((mode, delay))

    # 显示每个类别
    for cat_name, cat_modes in categories.items():
        if cat_modes:
            if cat_name == 'A':
                print("\n类别A: 单个矩阵")
            elif cat_name == 'B':
                print("\n类别B: 双矩阵错位 (list1先)")
            elif cat_name == 'C':
                print("\n类别C: 双矩阵错位 (list2先)")
            elif cat_name == 'D':
                print("\n类别D: 顺序输出")
            elif cat_name == 'E':
                print("\n类别E: 单矩阵边缘输出")
            elif cat_name == 'F':
                print("\n类别F: 双矩阵边缘输出 (list1先)")
            elif cat_name == 'G':
                print("\n类别G: 双矩阵边缘输出 (list2先)")
            elif cat_name == 'H':
                print("\n类别H: 自定义MATRIX1两步输出")

            for mode, delay in sorted(cat_modes):
                print(f"  {mode:<35} {delay:<10.2f}")


def interactive_mode_selection():
    """交互式模式选择主函数（带配置延迟）"""
    print("矩阵输出系统 - 配置延迟版")
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
    print("交互式模式选择（使用配置延迟）")
    print("="*60)

    while True:
        print("\n可用命令:")
        print("  'q' - 退出程序")
        print("  'd' - 显示所有模式延迟配置")
        print("  'm' - 显示模式列表")
        print("  输入模式名称或编号选择模式")

        print("\n模式列表:")
        modes = sorted(OUTPUT_MODES.keys())
        for i, mode in enumerate(modes):
            delay = get_mode_delay(mode)
            print(f"  {i+1:3d}. {mode:<35} [延迟: {delay:.2f}秒]")

        choice = input("\n请输入命令或选择模式: ").strip()

        if choice.lower() == 'q':
            print("退出程序")
            break
        elif choice.lower() == 'd':
            show_mode_delays()
            continue
        elif choice.lower() == 'm':
            # 重新显示模式列表
            continue

        # 解析模式选择
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

        # 获取该模式的配置延迟
        config_delay = get_mode_delay(mode_name)
        print(f"\n已选择模式: {mode_name}")
        print(f"配置延迟: {config_delay:.2f}秒")

        # 询问用户是否使用配置延迟
        use_config = input("使用配置延迟？(y/n, 默认y): ").strip().lower()
        if use_config in ('', 'y', 'yes'):
            delay = config_delay
            print(f"使用配置延迟: {delay:.2f}秒")
        else:
            # 获取自定义延迟
            delay = get_float("请输入自定义延迟（秒）", default=config_delay)
            print(f"使用自定义延迟: {delay:.2f}秒")

        # 运行模式
        steps = run_mode(mode_name, MATRIX1, MATRIX2, delay=delay)

        if steps is not None:
            print(f"\n模式运行完成，共 {len(steps)} 个步骤")

        print("\n" + "-"*60)


def main():
    """主函数"""
    interactive_mode_selection()


if __name__ == "__main__":
    main()
