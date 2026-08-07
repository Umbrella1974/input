#!/usr/bin/env python3
"""
随机实验入口（HV507 gate发送 + 受试者作答 + 反应时间记录）。

核心流程：
1. 从 experiment_pool_config.py 读取实验池和每个模式出现次数
2. 展开并随机打乱 trial 顺序
3. 每个 trial 按 HV507 gate 协议发送到 ESP32
4. 受试者从代称选项中作答，或请求重播
5. 记录真实模式、答案、正确性、反应时间和重播次数
"""

import csv
import os
import random
import time
from datetime import datetime

import experiment_pool_config as exp_config
import interactive_send_to_esp32_hv507_gate_with_scoring as gate


RESULT_FIELDS = [
    "timestamp",
    "session_id",
    "run_mode",
    "trial_index",
    "true_mode",
    "true_label",
    "answer_mode",
    "answer_label",
    "is_correct",
    "reaction_time_sec",
    "replay_count",
    "status",
]

SEQUENCE_FIELDS = ["session_id", "trial_index", "mode", "label"]


def sanitize_session_id(session_id: str) -> str:
    """生成适合文件名使用的session_id。"""
    allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
    cleaned = "".join(ch if ch in allowed else "_" for ch in session_id.strip())
    return cleaned or datetime.now().strftime("session_%Y%m%d_%H%M%S")


def get_session_id() -> str:
    """获取session_id；直接回车则自动生成。"""
    user_input = input("请输入 session_id（直接回车自动生成）: ").strip()
    if user_input:
        return sanitize_session_id(user_input)
    return datetime.now().strftime("session_%Y%m%d_%H%M%S")


def choose_run_mode() -> str:
    """选择训练模式或受试模式。"""
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


def choose_show_frames(run_mode: str) -> bool:
    """选择是否在屏幕上显示每个trial的帧内容。"""
    if run_mode == "test":
        return False

    default = run_mode == "train"
    return gate.base.get_yes_no("是否显示本次trial帧内容？", default=default)


def active_pool_modes():
    """返回出现次数大于0的实验池模式。"""
    return [mode for mode, count in exp_config.TRIAL_POOL.items() if count > 0]


def validate_experiment_config():
    """验证实验池配置和选项标签是否可用。"""
    if not exp_config.TRIAL_POOL:
        raise ValueError("TRIAL_POOL 不能为空")

    total_trials = 0
    labels = []

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

        labels.append(label)
        total_trials += count

    if total_trials == 0:
        raise ValueError("TRIAL_POOL 中所有模式出现次数都是0")

    if len(labels) != len(set(labels)):
        raise ValueError("实验池内的 CHOICE_LABELS 必须一一对应，不能重复")

    if not isinstance(exp_config.MAX_REPLAYS, int) or exp_config.MAX_REPLAYS < 0:
        raise ValueError("MAX_REPLAYS 必须是非负整数")


def build_trial_sequence():
    """根据TRIAL_POOL展开并随机打乱trial顺序。"""
    sequence = []
    for mode, count in exp_config.TRIAL_POOL.items():
        sequence.extend([mode] * count)

    rng = random.Random(exp_config.RANDOM_SEED)
    rng.shuffle(sequence)
    return sequence


def get_label(mode: str) -> str:
    """获取模式对应的受试者显示标签。"""
    return exp_config.CHOICE_LABELS[mode]


def get_sequence_path(session_id: str) -> str:
    """生成随机顺序记录文件名。"""
    return exp_config.SEQUENCE_CSV_TEMPLATE.format(session_id=session_id)


def write_csv_header_if_needed(path: str, fields):
    """如果CSV文件不存在，先写入表头。"""
    file_exists = os.path.exists(path)
    if file_exists:
        return

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()


def save_sequence(session_id: str, sequence):
    """保存本轮完整随机顺序。"""
    path = get_sequence_path(session_id)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=SEQUENCE_FIELDS)
        writer.writeheader()
        for trial_index, mode in enumerate(sequence, start=1):
            writer.writerow(
                {
                    "session_id": session_id,
                    "trial_index": trial_index,
                    "mode": mode,
                    "label": get_label(mode),
                }
            )

    print(f"随机顺序已保存到 {path}")


def append_result(row):
    """追加写入单个trial结果。"""
    write_csv_header_if_needed(exp_config.RESULTS_CSV, RESULT_FIELDS)
    with open(exp_config.RESULTS_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=RESULT_FIELDS)
        writer.writerow(row)


def format_reaction_time(start_time):
    """将反应时间格式化为秒；未作答时返回空字符串。"""
    if start_time is None:
        return ""
    return f"{time.perf_counter() - start_time:.6f}"


def send_steps_once(sock, steps, delay: float, dry_run: bool, show_frames: bool):
    """发送或dry-run展示一次trial刺激，并返回计时起点。"""
    first_send_time = None

    if dry_run:
        if show_frames:
            print("\n=== dry-run: 模拟发送本次trial刺激 ===")
        for i, step in enumerate(steps, start=1):
            frame = gate.build_frame(step)
            if first_send_time is None:
                first_send_time = time.perf_counter()
            if show_frames:
                print(f"  步骤 {i}: channels={step}")
                print(f"          frame={gate.base.frame_to_hex(frame)}")
        return first_send_time

    for i, step in enumerate(steps, start=1):
        frame = gate.build_frame(step)
        sock.sendall(frame)
        if first_send_time is None:
            first_send_time = time.perf_counter()
        if show_frames:
            print(f"  已发送步骤 {i}/{len(steps)}: {step}")
            print(f"          frame={gate.base.frame_to_hex(frame)}")
        if i < len(steps):
            time.sleep(delay)

    return first_send_time


def wait_for_trial_start(trial_index: int) -> bool:
    """等待用户按回车开始本trial；返回False表示退出实验。"""
    while True:
        choice = input(f"\nTrial {trial_index}: 按 Enter 开始本试次（输入 q 退出实验）: ").strip().lower()
        if not choice:
            return True
        if choice in ("q", "x", "quit", "exit"):
            return False
        print("  错误: 请按 Enter 开始，或输入 q 退出")


def print_answer_options(choice_modes):
    """显示受试者可选答案。"""
    print("\n请选择你感受到的选项：")
    for i, mode in enumerate(choice_modes, start=1):
        print(f"  {i}. {get_label(mode)}")
    print("  r. 再播放一次")
    print("  q. 退出实验")


def parse_answer(choice: str, choice_modes):
    """解析受试者输入。"""
    normalized = choice.strip()
    if normalized.lower() in ("r", "replay"):
        return "replay", None
    if normalized.lower() in ("q", "x", "quit", "exit"):
        return "quit", None

    if normalized.isdigit():
        idx = int(normalized) - 1
        if 0 <= idx < len(choice_modes):
            return "answer", choice_modes[idx]
        raise ValueError("选项编号超出范围")

    label_to_mode = {get_label(mode): mode for mode in choice_modes}
    if normalized in label_to_mode:
        return "answer", label_to_mode[normalized]

    raise ValueError("未知输入，请输入选项编号、标签、r 或 q")


def make_result_row(
    session_id: str,
    run_mode: str,
    trial_index: int,
    true_mode: str,
    answer_mode: str,
    reaction_time_sec,
    replay_count: int,
    status: str,
):
    """构造结果CSV的一行。"""
    true_label = get_label(true_mode)
    answer_label = get_label(answer_mode) if answer_mode else ""
    is_correct = bool(answer_mode and answer_mode == true_mode)

    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "session_id": session_id,
        "run_mode": run_mode,
        "trial_index": trial_index,
        "true_mode": true_mode,
        "true_label": true_label,
        "answer_mode": answer_mode or "",
        "answer_label": answer_label,
        "is_correct": is_correct,
        "reaction_time_sec": reaction_time_sec,
        "replay_count": replay_count,
        "status": status,
    }


def run_trial(
    session_id: str,
    run_mode: str,
    trial_index: int,
    true_mode: str,
    choice_modes,
    sock,
    dry_run: bool,
    show_frames: bool,
):
    """运行单个trial，返回'exit'表示中止实验。"""
    delay = gate.base.get_mode_delay(true_mode)
    replay_count = 0

    try:
        steps = gate.base.compute_mode_steps(true_mode, gate.base.MATRIX1, gate.base.MATRIX2)
        gate.validate_steps(steps)
        if run_mode == "train":
            print(f"\nTrial {trial_index}: 准备发送刺激，共 {len(steps)} 个步骤，delay={delay:.2f}秒")
            print(f"训练提示: 本次信号 = {get_label(true_mode)}")
        if not wait_for_trial_start(trial_index):
            return "exit"
        start_time = send_steps_once(sock, steps, delay, dry_run, show_frames)
    except Exception as e:
        print(f"  发送失败: {e}")
        if not dry_run:
            append_result(
                make_result_row(
                    session_id=session_id,
                    run_mode=run_mode,
                    trial_index=trial_index,
                    true_mode=true_mode,
                    answer_mode="",
                    reaction_time_sec="",
                    replay_count=replay_count,
                    status="send_failed",
                )
            )
        return "exit"

    while True:
        print_answer_options(choice_modes)
        choice = input("请输入答案: ").strip()

        try:
            action, answer_mode = parse_answer(choice, choice_modes)
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
                            true_mode=true_mode,
                            answer_mode="",
                            reaction_time_sec="",
                            replay_count=replay_count,
                            status="exceeded_replay",
                        )
                    )
                return "continue"

            replay_count += 1
            print(f"重播本题刺激 ({replay_count}/{exp_config.MAX_REPLAYS})")
            if run_mode == "train":
                print(f"训练提示: 本次信号 = {get_label(true_mode)}")
            try:
                start_time = send_steps_once(sock, steps, delay, dry_run, show_frames)
            except Exception as e:
                print(f"  重播发送失败: {e}")
                if not dry_run:
                    append_result(
                        make_result_row(
                            session_id=session_id,
                            run_mode=run_mode,
                            trial_index=trial_index,
                            true_mode=true_mode,
                            answer_mode="",
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
            true_mode=true_mode,
            answer_mode=answer_mode,
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
    """主函数。"""
    print("矩阵随机实验 - ESP32 HV507 gate发送版")

    try:
        validate_experiment_config()
        gate.base.validate_matrices(gate.base.MATRIX1, gate.base.MATRIX2)
    except Exception as e:
        print(f"配置或矩阵验证失败: {e}")
        return

    session_id = get_session_id()
    run_mode = choose_run_mode()
    show_frames = choose_show_frames(run_mode)
    dry_run, host, port = gate.base.get_connection_settings()
    sequence = build_trial_sequence()
    choice_modes = active_pool_modes()

    print(f"\nsession_id: {session_id}")
    print(f"运行模式: {run_mode}")
    print(f"显示trial帧内容: {show_frames}")
    print(f"trial总数: {len(sequence)}")
    print(f"最大重播次数: {exp_config.MAX_REPLAYS}")
    print("实验选项:")
    for mode in choice_modes:
        print(f"  {get_label(mode)}")

    sock = None
    if not dry_run:
        try:
            sock = gate.base.connect_esp32(host, port)
        except Exception as e:
            print(f"连接ESP32失败: {e}")
            return

    if dry_run:
        print("\ndry-run模式：不写入CSV")
        if run_mode == "train":
            print("训练模式随机顺序:")
            for trial_index, mode in enumerate(sequence, start=1):
                print(f"  {trial_index}. {get_label(mode)}")
        else:
            print("受试模式：随机顺序已生成，但不在屏幕显示正确标签")
    else:
        save_sequence(session_id, sequence)

    try:
        for trial_index, true_mode in enumerate(sequence, start=1):
            result = run_trial(
                session_id,
                run_mode,
                trial_index,
                true_mode,
                choice_modes,
                sock,
                dry_run,
                show_frames,
            )
            if result == "exit":
                print("实验已中止")
                break
    finally:
        if not dry_run:
            gate.send_gate_off(sock)
        gate.base.close_esp32(sock)

    print("实验结束")


if __name__ == "__main__":
    main()
