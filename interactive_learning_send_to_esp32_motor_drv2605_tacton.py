#!/usr/bin/env python3
"""
Learning entry for ESP32 DRV2605 motor tactons.

The learning phase reads active tactons from motor_tacton_experiment_config.py,
shows participant-visible labels, lets each tacton be replayed up to
LEARNING_MAX_PLAYS times, and records the final play count.
"""

import csv
import os
from datetime import datetime

import motor_tacton_experiment_config as exp_config
import interactive_send_to_esp32_motor_drv2605_tacton as motor


LEARNING_FIELDS = [
    "timestamp",
    "session_id",
    "learning_index",
    "tacton_id",
    "label",
    "play_count",
    "max_plays",
    "rough_slip_duration_ms",
    "status",
]


def sanitize_session_id(session_id: str) -> str:
    """Generate a filesystem-safe session id."""
    allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
    cleaned = "".join(ch if ch in allowed else "_" for ch in session_id.strip())
    return cleaned or datetime.now().strftime("motor_learning_%Y%m%d_%H%M%S")


def get_session_id() -> str:
    """Read session id; empty input generates one."""
    user_input = input("请输入 motor learning session_id（直接回车自动生成）: ").strip()
    if user_input:
        return sanitize_session_id(user_input)
    return datetime.now().strftime("motor_learning_%Y%m%d_%H%M%S")


def active_learning_tactons():
    """Return active tactons in config order."""
    return [tacton_id for tacton_id, count in exp_config.TACTON_POOL.items() if count > 0]


def get_label(tacton_id: int) -> str:
    """Return participant-visible label."""
    return exp_config.CHOICE_LABELS[tacton_id]


def validate_learning_config():
    """Validate tacton pool, labels, and learning parameters."""
    if not exp_config.TACTON_POOL:
        raise ValueError("TACTON_POOL 不能为空")

    if not isinstance(exp_config.LEARNING_MAX_PLAYS, int) or exp_config.LEARNING_MAX_PLAYS <= 0:
        raise ValueError("LEARNING_MAX_PLAYS 必须是正整数")

    if not str(exp_config.LEARNING_CSV).strip():
        raise ValueError("LEARNING_CSV 不能为空")

    motor.validate_rough_duration_ms(exp_config.ROUGH_SLIP_DURATION_MS)

    labels = []
    active_tactons = []

    for tacton_id, count in exp_config.TACTON_POOL.items():
        motor.validate_tacton_id(tacton_id)

        if not isinstance(count, int) or count < 0:
            raise ValueError(f"tacton {tacton_id} 的出现次数必须是非负整数")
        if count == 0:
            continue
        if tacton_id not in exp_config.CHOICE_LABELS:
            raise ValueError(f"CHOICE_LABELS 缺少tacton标签: {tacton_id}")

        label = exp_config.CHOICE_LABELS[tacton_id]
        if not str(label).strip():
            raise ValueError(f"tacton {tacton_id} 的标签不能为空")
        if str(label).strip() == str(tacton_id):
            raise ValueError(f"tacton {tacton_id} 的标签不能直接等于真实编号")

        active_tactons.append(tacton_id)
        labels.append(label)

    if not active_tactons:
        raise ValueError("TACTON_POOL 中所有tacton出现次数都是0")

    if len(labels) != len(set(labels)):
        raise ValueError("学习池内的 CHOICE_LABELS 必须一一对应，不能重复")


def write_csv_header_if_needed(path: str):
    """Write CSV header if the file does not exist."""
    if os.path.exists(path):
        return

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LEARNING_FIELDS)
        writer.writeheader()


def append_learning_result(session_id: str, learning_index: int, tacton_id: int, play_count: int, status: str):
    """Append one learning result row."""
    write_csv_header_if_needed(exp_config.LEARNING_CSV)
    with open(exp_config.LEARNING_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LEARNING_FIELDS)
        writer.writerow(
            {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "session_id": session_id,
                "learning_index": learning_index,
                "tacton_id": tacton_id,
                "label": get_label(tacton_id),
                "play_count": play_count,
                "max_plays": exp_config.LEARNING_MAX_PLAYS,
                "rough_slip_duration_ms": exp_config.ROUGH_SLIP_DURATION_MS,
                "status": status,
            }
        )


def send_or_dry_run_once(sock, tacton_id: int, dry_run: bool):
    """Play one learning stimulus."""
    if dry_run:
        motor.dry_run_play_tacton(tacton_id, exp_config.ROUGH_SLIP_DURATION_MS)
        return

    motor.tcp_play_tacton(sock, tacton_id, exp_config.ROUGH_SLIP_DURATION_MS)


def run_learning_item(session_id: str, learning_index: int, total: int, tacton_id: int, sock, dry_run: bool):
    """Run one learning item; return 'exit' or 'continue'."""
    label = get_label(tacton_id)
    play_count = 0

    print("\n" + "=" * 60)
    print(f"学习 {learning_index}/{total}")
    print(f"标签: {label}")
    print(f"最多播放: {exp_config.LEARNING_MAX_PLAYS} 次")

    while True:
        if play_count >= exp_config.LEARNING_MAX_PLAYS:
            print("已达到本信号最大学习次数，进入下一个信号")
            if not dry_run:
                append_learning_result(session_id, learning_index, tacton_id, play_count, "max_reached")
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
                append_learning_result(session_id, learning_index, tacton_id, play_count, "interrupted")
            else:
                print("dry-run模式：未写入学习CSV")
            return "exit"

        if choice in ("n", "next", "下一题", "下一个"):
            if play_count == 0:
                print("  当前信号还没有播放过。请至少播放一次后再进入下一个信号。")
                continue

            print("进入下一个信号")
            if not dry_run:
                append_learning_result(session_id, learning_index, tacton_id, play_count, "learned")
            else:
                print("dry-run模式：未写入学习CSV")
            return "continue"

        if choice in ("", "p", "play", "播放"):
            play_count += 1
            print(f"\n播放当前信号: {label} ({play_count}/{exp_config.LEARNING_MAX_PLAYS})")
            send_or_dry_run_once(sock, tacton_id, dry_run)
            continue

        print("  错误: 请输入 Enter、p、n 或 q")


def main():
    """Main entry."""
    print("DRV2605 Motor Tacton 学习入口 - ESP32 TCP发送版")

    try:
        validate_learning_config()
    except Exception as e:
        print(f"配置验证失败: {e}")
        return

    session_id = get_session_id()
    dry_run, host, port = motor.get_connection_settings()
    tactons = active_learning_tactons()

    print(f"\nsession_id: {session_id}")
    print(f"学习tacton总数: {len(tactons)}")
    print(f"每个tacton最大学习次数: {exp_config.LEARNING_MAX_PLAYS}")
    print(f"Rough Slip时长: {exp_config.ROUGH_SLIP_DURATION_MS} ms")
    print("学习顺序:")
    for i, tacton_id in enumerate(tactons, start=1):
        print(f"  {i}. {get_label(tacton_id)}")

    if dry_run:
        print("\ndry-run模式：不连接ESP32，不写入学习CSV")

    sock = None
    if not dry_run:
        try:
            sock = motor.connect_esp32(host, port)
        except Exception as e:
            print(f"连接ESP32失败: {e}")
            return

    try:
        for learning_index, tacton_id in enumerate(tactons, start=1):
            result = run_learning_item(session_id, learning_index, len(tactons), tacton_id, sock, dry_run)
            if result == "exit":
                break
    finally:
        if not dry_run:
            motor.send_stop(sock)
        motor.close_esp32(sock)

    print("学习结束")


if __name__ == "__main__":
    main()
