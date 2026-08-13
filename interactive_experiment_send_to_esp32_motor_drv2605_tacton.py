#!/usr/bin/env python3
"""
Random test entry for ESP32 DRV2605 motor tactons.

Core flow:
1. Read tacton pool and counts from motor_tacton_experiment_config.py
2. Expand and shuffle trials
3. Send one PLAY command to ESP32 per trial
4. Let the participant answer from labels or request replay
5. Record true tacton, answer, correctness, reaction time, replay count, and status
"""

import csv
import os
import random
import time
from datetime import datetime

import motor_tacton_experiment_config as exp_config
import interactive_send_to_esp32_motor_drv2605_tacton as motor


RESULT_FIELDS = [
    "timestamp",
    "session_id",
    "run_mode",
    "trial_index",
    "true_tacton_id",
    "true_label",
    "answer_tacton_id",
    "answer_label",
    "is_correct",
    "reaction_time_sec",
    "replay_count",
    "rough_slip_duration_ms",
    "status",
]

SEQUENCE_FIELDS = ["session_id", "trial_index", "tacton_id", "label"]


def sanitize_session_id(session_id: str) -> str:
    """Generate a filesystem-safe session id."""
    allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
    cleaned = "".join(ch if ch in allowed else "_" for ch in session_id.strip())
    return cleaned or datetime.now().strftime("motor_session_%Y%m%d_%H%M%S")


def get_session_id() -> str:
    """Read session id; empty input generates one."""
    user_input = input("请输入 motor session_id（直接回车自动生成）: ").strip()
    if user_input:
        return sanitize_session_id(user_input)
    return datetime.now().strftime("motor_session_%Y%m%d_%H%M%S")


def choose_run_mode() -> str:
    """Choose train or test mode."""
    while True:
        print("\n请选择运行模式:")
        print("  1. train 训练模式")
        print("  2. test  受试模式")
        choice = input("请输入运行模式 (默认: test): ").strip().lower()

        if not choice:
            return "test"
        if choice in ("1", "train", "training", "训练", "训练模式"):
            return "train"
        if choice in ("2", "test", "subject", "受试", "受试模式"):
            return "test"

        print("  错误: 请输入 1/train 或 2/test")


def choose_show_commands(run_mode: str) -> bool:
    """Choose whether to show ESP32 commands."""
    if run_mode == "test":
        return False

    default = run_mode == "train"
    return motor.get_yes_no("是否显示本次trial发送命令？", default=default)


def active_pool_tactons():
    """Return active tactons in config order."""
    return [tacton_id for tacton_id, count in exp_config.TACTON_POOL.items() if count > 0]


def validate_experiment_config():
    """Validate tacton pool and participant labels."""
    if not exp_config.TACTON_POOL:
        raise ValueError("TACTON_POOL 不能为空")

    total_trials = 0
    labels = []

    motor.validate_rough_duration_ms(exp_config.ROUGH_SLIP_DURATION_MS)

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

        labels.append(label)
        total_trials += count

    if total_trials == 0:
        raise ValueError("TACTON_POOL 中所有tacton出现次数都是0")

    if len(labels) != len(set(labels)):
        raise ValueError("实验池内的 CHOICE_LABELS 必须一一对应，不能重复")

    if not isinstance(exp_config.MAX_REPLAYS, int) or exp_config.MAX_REPLAYS < 0:
        raise ValueError("MAX_REPLAYS 必须是非负整数")


def build_trial_sequence():
    """Expand TACTON_POOL and shuffle trial order."""
    sequence = []
    for tacton_id, count in exp_config.TACTON_POOL.items():
        sequence.extend([tacton_id] * count)

    rng = random.Random(exp_config.RANDOM_SEED)
    rng.shuffle(sequence)
    return sequence


def get_label(tacton_id: int) -> str:
    """Return participant-visible label."""
    return exp_config.CHOICE_LABELS[tacton_id]


def get_sequence_path(session_id: str) -> str:
    """Build random sequence CSV path."""
    return exp_config.SEQUENCE_CSV_TEMPLATE.format(session_id=session_id)


def write_csv_header_if_needed(path: str, fields):
    """Write CSV header if the file does not exist."""
    if os.path.exists(path):
        return

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()


def save_sequence(session_id: str, sequence):
    """Save full randomized sequence."""
    path = get_sequence_path(session_id)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=SEQUENCE_FIELDS)
        writer.writeheader()
        for trial_index, tacton_id in enumerate(sequence, start=1):
            writer.writerow(
                {
                    "session_id": session_id,
                    "trial_index": trial_index,
                    "tacton_id": tacton_id,
                    "label": get_label(tacton_id),
                }
            )

    print(f"随机顺序已保存到 {path}")


def append_result(row):
    """Append one trial result."""
    write_csv_header_if_needed(exp_config.RESULTS_CSV, RESULT_FIELDS)
    with open(exp_config.RESULTS_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=RESULT_FIELDS)
        writer.writerow(row)


def format_reaction_time(start_time):
    """Format reaction time in seconds; unanswered trials return empty string."""
    if start_time is None:
        return ""
    return f"{time.perf_counter() - start_time:.6f}"


def send_tacton_once(sock, tacton_id: int, dry_run: bool, show_commands: bool):
    """Send or dry-run one trial stimulus and return the timing start."""
    command = motor.build_play_command(tacton_id, exp_config.ROUGH_SLIP_DURATION_MS)

    if dry_run:
        start_time = time.perf_counter()
        if show_commands:
            print("\n=== dry-run: 模拟发送本次trial刺激 ===")
            print(f"  command={command.strip()}")
        return start_time

    response = motor.tcp_send_command(sock, command)
    start_time = time.perf_counter()
    if show_commands:
        print(f"  已发送: {command.strip()} ({response})")
    return start_time


def wait_for_trial_start(trial_index: int) -> bool:
    """Wait for Enter to start one trial; False means exit."""
    while True:
        choice = input(f"\nTrial {trial_index}: 按 Enter 开始本试次（输入 q 退出实验）: ").strip().lower()
        if not choice:
            return True
        if choice in ("q", "x", "quit", "exit"):
            return False
        print("  错误: 请按 Enter 开始，或输入 q 退出")


def print_answer_options(choice_tactons):
    """Print participant answer options without true tacton ids."""
    print("\n请选择你感受到的选项：")
    for i, tacton_id in enumerate(choice_tactons, start=1):
        print(f"  {i}. {get_label(tacton_id)}")
    print("  r. 再播放一次")
    print("  q. 退出实验")


def parse_answer(choice: str, choice_tactons):
    """Parse answer input."""
    normalized = choice.strip()
    if normalized.lower() in ("r", "replay"):
        return "replay", None
    if normalized.lower() in ("q", "x", "quit", "exit"):
        return "quit", None

    if normalized.isdigit():
        idx = int(normalized) - 1
        if 0 <= idx < len(choice_tactons):
            return "answer", choice_tactons[idx]
        raise ValueError("选项编号超出范围")

    label_to_tacton = {get_label(tacton_id): tacton_id for tacton_id in choice_tactons}
    if normalized in label_to_tacton:
        return "answer", label_to_tacton[normalized]

    raise ValueError("未知输入，请输入选项编号、标签、r 或 q")


def make_result_row(
    session_id: str,
    run_mode: str,
    trial_index: int,
    true_tacton_id: int,
    answer_tacton_id,
    reaction_time_sec,
    replay_count: int,
    status: str,
):
    """Build one result CSV row."""
    true_label = get_label(true_tacton_id)
    answer_label = get_label(answer_tacton_id) if answer_tacton_id else ""
    is_correct = bool(answer_tacton_id and answer_tacton_id == true_tacton_id)

    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "session_id": session_id,
        "run_mode": run_mode,
        "trial_index": trial_index,
        "true_tacton_id": true_tacton_id,
        "true_label": true_label,
        "answer_tacton_id": answer_tacton_id or "",
        "answer_label": answer_label,
        "is_correct": is_correct,
        "reaction_time_sec": reaction_time_sec,
        "replay_count": replay_count,
        "rough_slip_duration_ms": exp_config.ROUGH_SLIP_DURATION_MS,
        "status": status,
    }


def run_trial(
    session_id: str,
    run_mode: str,
    trial_index: int,
    true_tacton_id: int,
    choice_tactons,
    sock,
    dry_run: bool,
    show_commands: bool,
):
    """Run one trial; return 'exit' or 'continue'."""
    replay_count = 0

    try:
        if run_mode == "train":
            print(f"\nTrial {trial_index}: 准备发送刺激")
            print(f"训练提示: 本次信号 = {get_label(true_tacton_id)}")
        if not wait_for_trial_start(trial_index):
            return "exit"
        start_time = send_tacton_once(sock, true_tacton_id, dry_run, show_commands)
    except Exception as e:
        print(f"  发送失败: {e}")
        if not dry_run:
            append_result(
                make_result_row(
                    session_id=session_id,
                    run_mode=run_mode,
                    trial_index=trial_index,
                    true_tacton_id=true_tacton_id,
                    answer_tacton_id="",
                    reaction_time_sec="",
                    replay_count=replay_count,
                    status="send_failed",
                )
            )
        return "exit"

    while True:
        print_answer_options(choice_tactons)
        choice = input("请输入答案: ").strip()

        try:
            action, answer_tacton_id = parse_answer(choice, choice_tactons)
        except ValueError as e:
            print(f"  错误: {e}")
            continue

        if action == "quit":
            return "exit"

        if action == "replay":
            if replay_count >= exp_config.MAX_REPLAYS:
                print("已超过最大重播次数，本题记为未作答，进入下一题")
                if not dry_run:
                    append_result(
                        make_result_row(
                            session_id=session_id,
                            run_mode=run_mode,
                            trial_index=trial_index,
                            true_tacton_id=true_tacton_id,
                            answer_tacton_id="",
                            reaction_time_sec="",
                            replay_count=replay_count,
                            status="exceeded_replay",
                        )
                    )
                return "continue"

            replay_count += 1
            print(f"重播本题刺激 ({replay_count}/{exp_config.MAX_REPLAYS})")
            if run_mode == "train":
                print(f"训练提示: 本次信号 = {get_label(true_tacton_id)}")
            try:
                start_time = send_tacton_once(sock, true_tacton_id, dry_run, show_commands)
            except Exception as e:
                print(f"  重播发送失败: {e}")
                if not dry_run:
                    append_result(
                        make_result_row(
                            session_id=session_id,
                            run_mode=run_mode,
                            trial_index=trial_index,
                            true_tacton_id=true_tacton_id,
                            answer_tacton_id="",
                            reaction_time_sec="",
                            replay_count=replay_count,
                            status="send_failed",
                        )
                    )
                return "exit"
            continue

        reaction_time_sec = format_reaction_time(start_time)
        row = make_result_row(
            session_id=session_id,
            run_mode=run_mode,
            trial_index=trial_index,
            true_tacton_id=true_tacton_id,
            answer_tacton_id=answer_tacton_id,
            reaction_time_sec=reaction_time_sec,
            replay_count=replay_count,
            status="answered",
        )

        print(
            f"已记录答案: {row['answer_label']}，"
            f"正确={row['is_correct']}，RT={row['reaction_time_sec']}秒，"
            f"重播={replay_count}"
        )

        if not dry_run:
            append_result(row)
        else:
            print("dry-run模式：未写入实验结果CSV")

        return "continue"


def main():
    """Main entry."""
    print("DRV2605 Motor Tacton 随机实验 - ESP32 TCP发送版")

    try:
        validate_experiment_config()
    except Exception as e:
        print(f"配置验证失败: {e}")
        return

    session_id = get_session_id()
    run_mode = choose_run_mode()
    show_commands = choose_show_commands(run_mode)
    dry_run, host, port = motor.get_connection_settings()
    sequence = build_trial_sequence()
    choice_tactons = active_pool_tactons()

    print(f"\nsession_id: {session_id}")
    print(f"运行模式: {run_mode}")
    print(f"显示trial发送命令: {show_commands}")
    print(f"trial总数: {len(sequence)}")
    print(f"最大重播次数: {exp_config.MAX_REPLAYS}")
    print(f"Rough Slip时长: {exp_config.ROUGH_SLIP_DURATION_MS} ms")
    print("实验选项:")
    for tacton_id in choice_tactons:
        print(f"  {get_label(tacton_id)}")

    sock = None
    if not dry_run:
        try:
            sock = motor.connect_esp32(host, port)
        except Exception as e:
            print(f"连接ESP32失败: {e}")
            return

    if dry_run:
        print("\ndry-run模式：不写入CSV")
        if run_mode == "train":
            print("训练模式随机顺序:")
            for trial_index, tacton_id in enumerate(sequence, start=1):
                print(f"  {trial_index}. {get_label(tacton_id)}")
        else:
            print("受试模式：随机顺序已生成，但不在屏幕显示正确标签")
    else:
        save_sequence(session_id, sequence)

    try:
        for trial_index, true_tacton_id in enumerate(sequence, start=1):
            result = run_trial(
                session_id,
                run_mode,
                trial_index,
                true_tacton_id,
                choice_tactons,
                sock,
                dry_run,
                show_commands,
            )
            if result == "exit":
                print("实验已中止")
                break
    finally:
        if not dry_run:
            motor.send_stop(sock)
        motor.close_esp32(sock)

    print("实验结束")


if __name__ == "__main__":
    main()
