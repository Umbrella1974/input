#!/usr/bin/env python3
"""
学习入口（HV507 gate auto-off发送 + 标签提示 + 学习次数记录）。

用途：
1. 从 experiment_pool_config.py 的 TRIAL_POOL 读取所有 count > 0 的有效模式
2. 按 TRIAL_POOL 配置顺序逐个学习，不随机、不按 count 展开
3. 每个模式先显示受试者可见标签，再由受试者按键播放信号
4. 每个模式最多播放 LEARNING_MAX_PLAYS 次，默认5次
5. 真实发送模式下记录每个模式最终播放次数到 LEARNING_CSV

学习阶段不答题、不记录反应时间；TRIAL_POOL 中的 count 只用于决定该模式是否进入
学习池，不决定学习阶段重复次数。
"""

import csv
import os
import time
from datetime import datetime

import experiment_pool_config as exp_config
import interactive_send_to_esp32_hv507_gate_autoff_with_scoring as gate


LEARNING_FIELDS = [
    "timestamp",
    "session_id",
    "learning_index",
    "mode",
    "label",
    "play_count",
    "max_plays",
    "status",
]


def sanitize_session_id(session_id: str) -> str:
    """生成适合文件名使用的session_id。"""
    allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
    cleaned = "".join(ch if ch in allowed else "_" for ch in session_id.strip())
    return cleaned or datetime.now().strftime("learning_%Y%m%d_%H%M%S")


def get_session_id() -> str:
    """获取session_id；直接回车则自动生成。"""
    user_input = input("请输入 learning session_id（直接回车自动生成）: ").strip()
    if user_input:
        return sanitize_session_id(user_input)
    return datetime.now().strftime("learning_%Y%m%d_%H%M%S")


def active_learning_modes():
    """返回学习阶段要覆盖的模式：TRIAL_POOL中count > 0的模式，按配置顺序。"""
    return [mode for mode, count in exp_config.TRIAL_POOL.items() if count > 0]


def get_label(mode: str) -> str:
    """获取模式对应的受试者显示标签。"""
    return exp_config.CHOICE_LABELS[mode]


def validate_learning_config():
    """验证学习池配置、标签和学习次数上限。"""
    if not exp_config.TRIAL_POOL:
        raise ValueError("TRIAL_POOL 不能为空")

    if not isinstance(exp_config.LEARNING_MAX_PLAYS, int) or exp_config.LEARNING_MAX_PLAYS <= 0:
        raise ValueError("LEARNING_MAX_PLAYS 必须是正整数")

    if not str(exp_config.LEARNING_CSV).strip():
        raise ValueError("LEARNING_CSV 不能为空")

    labels = []
    active_modes = []

    for mode, count in exp_config.TRIAL_POOL.items():
        if mode not in gate.base.OUTPUT_MODES:
            raise ValueError(f"TRIAL_POOL 中存在未知模式: {mode}")
        if not isinstance(count, int) or count < 0:
            raise ValueError(f"模式 {mode} 的出现次数必须是非负整数")
        if count == 0:
            continue
        if mode not in exp_config.CHOICE_LABELS:
            raise ValueError(f"CHOICE_LABELS 缺少模式标签: {mode}")

        label = exp_config.CHOICE_LABELS[mode]
        if not str(label).strip():
            raise ValueError(f"模式 {mode} 的标签不能为空")
        if label == mode:
            raise ValueError(f"模式 {mode} 的标签不能直接等于真实模式名")

        active_modes.append(mode)
        labels.append(label)

    if not active_modes:
        raise ValueError("TRIAL_POOL 中所有模式出现次数都是0")

    if len(labels) != len(set(labels)):
        raise ValueError("学习池内的 CHOICE_LABELS 必须一一对应，不能重复")


def write_csv_header_if_needed(path: str):
    """如果CSV文件不存在，先写入表头。"""
    if os.path.exists(path):
        return

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LEARNING_FIELDS)
        writer.writeheader()


def append_learning_result(session_id: str, learning_index: int, mode: str, play_count: int, status: str):
    """追加写入单个模式的学习记录。"""
    write_csv_header_if_needed(exp_config.LEARNING_CSV)
    with open(exp_config.LEARNING_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LEARNING_FIELDS)
        writer.writerow(
            {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "session_id": session_id,
                "learning_index": learning_index,
                "mode": mode,
                "label": get_label(mode),
                "play_count": play_count,
                "max_plays": exp_config.LEARNING_MAX_PLAYS,
                "status": status,
            }
        )


def send_or_dry_run_once(sock, steps, delay: float, dry_run: bool):
    """播放一次当前学习信号。"""
    if dry_run:
        gate.dry_run_send_steps(steps, delay)
        return

    gate.tcp_send_steps(sock, steps, delay)


def run_learning_item(session_id: str, learning_index: int, total: int, mode: str, sock, dry_run: bool):
    """运行单个模式的学习流程；返回'exit'或'continue'。"""
    label = get_label(mode)
    delay = gate.base.get_mode_delay(mode)
    steps = gate.base.compute_mode_steps(mode, gate.base.MATRIX1, gate.base.MATRIX2)
    gate.validate_steps(steps, delay)

    play_count = 0

    print("\n" + "=" * 60)
    print(f"学习 {learning_index}/{total}")
    print(f"标签: {label}")
    print(f"模式: {mode}")
    print(f"步骤数: {len(steps)}，delay={delay:.2f}秒")
    print(f"最多播放: {exp_config.LEARNING_MAX_PLAYS} 次")

    while True:
        if play_count >= exp_config.LEARNING_MAX_PLAYS:
            print("已达到本信号最大学习次数，进入下一个信号")
            if not dry_run:
                append_learning_result(session_id, learning_index, mode, play_count, "max_reached")
            else:
                print("dry-run模式：未写入学习CSV")
            return "continue"

        print("\n可用命令:")
        print("  Enter / p - 播放一次当前信号")
        print("  n         - 已学会，进入下一个信号")
        print("  q         - 退出学习")
        print(f"当前已播放: {play_count}/{exp_config.LEARNING_MAX_PLAYS}")

        choice = input("请输入命令: ").strip().lower()

        if choice in ("q", "x", "quit", "exit"):
            print("退出学习")
            if not dry_run:
                append_learning_result(session_id, learning_index, mode, play_count, "interrupted")
            else:
                print("dry-run模式：未写入学习CSV")
            return "exit"

        if choice in ("n", "next", "下一题", "下一个"):
            if play_count == 0:
                print("  当前信号还没有播放过。请至少播放一次后再进入下一个信号。")
                continue

            print("进入下一个信号")
            if not dry_run:
                append_learning_result(session_id, learning_index, mode, play_count, "learned")
            else:
                print("dry-run模式：未写入学习CSV")
            return "continue"

        if choice in ("", "p", "play", "播放"):
            play_count += 1
            print(f"\n播放当前信号: {label} ({play_count}/{exp_config.LEARNING_MAX_PLAYS})")
            send_or_dry_run_once(sock, steps, delay, dry_run)
            continue

        print("  错误: 请输入 Enter、p、n 或 q")


def main():
    """主函数。"""
    print("矩阵学习入口 - ESP32 HV507 gate auto-off发送版")

    try:
        validate_learning_config()
        gate.base.validate_matrices(gate.base.MATRIX1, gate.base.MATRIX2)
    except Exception as e:
        print(f"配置或矩阵验证失败: {e}")
        return

    session_id = get_session_id()
    dry_run, host, port = gate.base.get_connection_settings()
    modes = active_learning_modes()

    print(f"\nsession_id: {session_id}")
    print(f"学习模式总数: {len(modes)}")
    print(f"每个模式最大学习次数: {exp_config.LEARNING_MAX_PLAYS}")
    print("学习顺序:")
    for i, mode in enumerate(modes, start=1):
        print(f"  {i}. {get_label(mode)}")

    if dry_run:
        print("\ndry-run模式：不连接ESP32，不写入学习CSV")

    sock = None
    if not dry_run:
        try:
            sock = gate.base.connect_esp32(host, port)
        except Exception as e:
            print(f"连接ESP32失败: {e}")
            return

    try:
        for learning_index, mode in enumerate(modes, start=1):
            result = run_learning_item(session_id, learning_index, len(modes), mode, sock, dry_run)
            if result == "exit":
                break
    finally:
        if not dry_run:
            gate.send_gate_off(sock)
        gate.base.close_esp32(sock)

    print("学习结束")


if __name__ == "__main__":
    main()
