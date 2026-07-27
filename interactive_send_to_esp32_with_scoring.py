#!/usr/bin/env python3
"""
交互式发送到ESP32（配置延迟 + TCP发送 + 评分保存）

功能：
1. 从mode_delays_config.py读取每个模式的默认延迟配置
2. 交互式选择输出模式
3. 生成完整输出步骤后，按步骤逐帧发送到ESP32
4. 真实发送模式下启动时连接一次ESP32，后续多个模式复用同一个TCP连接
5. 真实发送完成后输入评分，并保存到CSV文件

ESP32协议：
    MAGIC(4B) + length(1B) + payload(N<=128B) + checksum(1B)
"""

import csv
import os
import socket
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


MAGIC = b"\xAA\x55\xAA\x55"
DEFAULT_PORT = 12345
DEFAULT_CONNECT_TIMEOUT = 5.0
ESP32_READY_DELAY = 7.5
CSV_FILE = "output_scores.csv"


def quick_checksum(data: bytes) -> int:
    """计算ESP32端使用的8位校验和。"""
    return sum(data) & 0xFF


def validate_channels(channels) -> bytes:
    """检查通道列表并转换为payload。"""
    if not channels:
        raise ValueError("输出步骤为空，当前ESP32解析器不会处理空payload")

    if len(channels) > 128:
        raise ValueError(f"payload过长: {len(channels)}，最大支持128")

    payload = bytearray()
    for value in channels:
        if not isinstance(value, int):
            raise ValueError(f"通道值必须是整数: {value!r}")
        if not 0 <= value < 128:
            raise ValueError(f"通道值超出ESP32支持范围0-127: {value}")
        payload.append(value)

    return bytes(payload)


def build_frame(channels) -> bytes:
    """将一个输出步骤打包成ESP32协议帧。"""
    payload = validate_channels(channels)
    return MAGIC + bytes([len(payload)]) + payload + bytes([quick_checksum(payload)])


def frame_to_hex(frame: bytes) -> str:
    """将二进制帧格式化为十六进制字符串，便于dry-run检查。"""
    return " ".join(f"{byte:02X}" for byte in frame)


def compute_mode_steps(mode_name: str, matrix1, matrix2):
    """根据模式名称生成完整输出步骤。"""
    if mode_name not in OUTPUT_MODES:
        raise ValueError(f"未知模式: {mode_name}")

    func_name, params = OUTPUT_MODES[mode_name]

    if func_name == "single_matrix":
        return single_matrix(matrix1, **params)
    if func_name == "staggered_matrices":
        return staggered_matrices(matrix1, matrix2, **params)
    if func_name == "sequential_matrices":
        return sequential_matrices(matrix1, matrix2, **params)

    raise ValueError(f"未知函数: {func_name}")


def validate_steps(steps):
    """提前验证所有步骤，避免发送到一半才发现非法通道。"""
    if not steps:
        raise ValueError("模式没有生成任何输出步骤")

    for i, step in enumerate(steps, start=1):
        validate_channels(step)


def get_yes_no(prompt: str, default: bool = True) -> bool:
    """获取y/n输入。"""
    default_text = "y" if default else "n"
    while True:
        user_input = input(f"{prompt} (默认: {default_text}): ").strip().lower()
        if not user_input:
            return default
        if user_input in ("y", "yes"):
            return True
        if user_input in ("n", "no"):
            return False
        print("  错误: 请输入 y 或 n")


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


def get_int(prompt: str, default: int) -> int:
    """获取非负整数输入，支持默认值。"""
    while True:
        try:
            user_input = input(f"{prompt} (默认: {default}): ").strip()
            if not user_input:
                return default

            value = int(user_input)
            if value < 0:
                print("  错误: 请输入非负整数")
                continue
            return value
        except ValueError:
            print("  错误: 请输入有效的整数")


def get_nonnegative_int(prompt: str, default: int = None) -> int:
    """获取非负整数评分，支持默认值。"""
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


def choose_delay(mode_name: str) -> float:
    """基于模式默认延迟，让用户选择使用默认值或覆盖。"""
    config_delay = get_mode_delay(mode_name)

    print(f"\n已选择模式: {mode_name}")
    print(f"配置延迟: {config_delay:.2f}秒")

    use_config = get_yes_no("使用配置延迟？", default=True)
    if use_config:
        print(f"使用配置延迟: {config_delay:.2f}秒")
        return config_delay

    custom_delay = get_float("请输入自定义延迟（秒）", default=config_delay)
    print(f"使用自定义延迟: {custom_delay:.2f}秒")
    return custom_delay


def save_to_csv(mode_name: str, delay: float, score: int):
    """将真实发送后的评分保存到CSV文件。"""
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


def print_mode_list(modes):
    """显示可选模式及其默认延迟。"""
    print("\n模式列表:")
    for i, mode in enumerate(modes):
        delay = get_mode_delay(mode)
        print(f"  {i + 1:3d}. {mode:<35} [延迟: {delay:.2f}秒]")


def select_mode(modes, choice: str):
    """根据编号或模式名解析用户选择。"""
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(modes):
            return modes[idx]
        raise ValueError("编号超出范围")

    if choice in OUTPUT_MODES:
        return choice

    raise ValueError(f"未知模式 '{choice}'")


def dry_run_send_steps(steps):
    """只打印将要发送的帧，不连接ESP32。"""
    print("\n=== dry-run: 只打印帧，不连接ESP32 ===")
    for i, step in enumerate(steps, start=1):
        frame = build_frame(step)
        print(f"  步骤 {i}: payload={step}")
        print(f"          frame={frame_to_hex(frame)}")
    print("dry-run完成，未发送硬件，也未写入评分CSV")


def connect_esp32(host: str, port: int):
    """连接ESP32并等待首次连接后的硬件准备时间。"""
    print(f"\n正在连接ESP32: {host}:{port}")

    sock = socket.create_connection((host, port), timeout=DEFAULT_CONNECT_TIMEOUT)
    print("连接成功")
    print(f"等待ESP32上电准备: {ESP32_READY_DELAY:.1f}秒")
    time.sleep(ESP32_READY_DELAY)
    return sock


def close_esp32(sock):
    """关闭ESP32 TCP连接。"""
    if sock is None:
        return

    try:
        sock.close()
        print("ESP32 TCP连接已断开")
    except Exception as e:
        print(f"关闭ESP32连接时出错: {e}")


def tcp_send_steps(sock, steps, delay: float):
    """使用已经建立的TCP连接，按步骤逐帧发送。"""
    for i, step in enumerate(steps, start=1):
        frame = build_frame(step)
        sock.sendall(frame)
        print(f"  已发送步骤 {i}/{len(steps)}: {step}")

        if i < len(steps):
            time.sleep(delay)

    print("本次模式发送完成，TCP连接保持打开")


def get_connection_settings():
    """获取发送方式和ESP32连接配置。"""
    dry_run = get_yes_no("是否dry-run（只打印帧，不连接ESP32）？", default=True)
    if dry_run:
        return True, None, DEFAULT_PORT

    while True:
        host = input("请输入ESP32 IP地址: ").strip()
        if host:
            break
        print("  错误: IP地址不能为空")

    port = get_int("请输入ESP32 TCP端口", default=DEFAULT_PORT)
    return False, host, port


def interactive_mode_selection():
    """交互式模式选择主函数。"""
    print("矩阵输出系统 - ESP32发送 + 配置延迟 + 评分版")
    print(f"矩阵1: {MATRIX1}")
    print(f"矩阵2: {MATRIX2}")

    try:
        validate_matrices(MATRIX1, MATRIX2)
        print("矩阵验证通过")
    except Exception as e:
        print(f"矩阵验证失败: {e}")
        return

    dry_run, host, port = get_connection_settings()
    sock = None

    if not dry_run:
        try:
            sock = connect_esp32(host, port)
        except Exception as e:
            print(f"连接ESP32失败: {e}")
            return

    try:
        print("\n" + "=" * 60)
        print("交互式模式选择（ESP32发送）")
        print("=" * 60)

        while True:
            print("\n可用命令:")
            print("  'q' - 退出程序")
            print("  'x' - 断开ESP32连接并退出")
            print("  'd' - 显示所有模式延迟配置")
            print("  's' - 查看已保存的评分结果")
            print("  'm' - 显示模式列表")
            print("  输入模式名称或编号选择模式")

            modes = sorted(OUTPUT_MODES.keys())
            print_mode_list(modes)

            choice = input("\n请输入命令或选择模式: ").strip()

            if choice.lower() == "q":
                print("退出程序")
                break
            if choice.lower() == "x":
                if dry_run:
                    print("dry-run模式下无需断开ESP32，退出程序")
                else:
                    print("准备断开ESP32连接并退出程序")
                break
            if choice.lower() == "d":
                show_mode_delays()
                continue
            if choice.lower() == "s":
                show_csv_contents()
                continue
            if choice.lower() == "m":
                continue

            try:
                mode_name = select_mode(modes, choice)
                delay = choose_delay(mode_name)
                steps = compute_mode_steps(mode_name, MATRIX1, MATRIX2)
                validate_steps(steps)
            except Exception as e:
                print(f"  错误: {e}")
                continue

            print(f"\n模式生成完成，共 {len(steps)} 个步骤")

            try:
                if dry_run:
                    dry_run_send_steps(steps)
                    continue

                tcp_send_steps(sock, steps, delay)
            except Exception as e:
                print(f"  发送失败: {e}")
                break

            score = get_nonnegative_int("请为本次真实发送评分（非负整数）", default=5)
            save_to_csv(mode_name, delay, score)

            print("\n" + "-" * 60)
    finally:
        close_esp32(sock)


def main():
    """主函数。"""
    interactive_mode_selection()


if __name__ == "__main__":
    main()
