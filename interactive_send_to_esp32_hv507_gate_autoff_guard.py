#!/usr/bin/env python3
"""
HV507 gate auto-off + PC frame guard 测试入口。

这个文件不修改原来的 auto-off 发送器，只在运行时替换帧间等待策略：
1. control byte、payload、checksum 仍由 interactive_send_to_esp32_hv507_gate_autoff_with_scoring.py 构造
2. ESP32 的单帧 auto-off 时间仍由 delay 换算成 duration_code
3. PC 下一帧发送前额外等待 auto_off_time + INTER_FRAME_GUARD_SEC

目的：避免 PC 在 ESP32 当前帧 auto-off 前过早发来下一帧，导致 ESP32 处理新帧时先
_blank_outputs()，从而提前截断上一帧 BL 高电平。
"""

import time

import interactive_experiment_send_to_esp32_hv507_gate_autoff as experiment_autoff
import interactive_send_to_esp32_hv507_gate_autoff_with_scoring as autoff


INTER_FRAME_GUARD_SEC = 0.20


def get_auto_off_sec(delay: float) -> float:
    """返回当前 delay 实际对应的 ESP32 auto-off 秒数。"""
    duration_code = autoff.delay_to_duration_code(delay)
    return autoff.duration_code_to_ms(duration_code) / 1000.0


def get_inter_frame_wait_sec(delay: float) -> float:
    """返回 PC 在两帧之间等待的总秒数。"""
    return get_auto_off_sec(delay) + INTER_FRAME_GUARD_SEC


def describe_guard_timing(delay: float) -> str:
    """描述 PC 端帧间等待策略。"""
    auto_off_sec = get_auto_off_sec(delay)
    wait_sec = get_inter_frame_wait_sec(delay)
    return (
        f"PC帧间等待: auto_off={auto_off_sec:.3f}s "
        f"+ guard={INTER_FRAME_GUARD_SEC:.3f}s -> {wait_sec:.3f}s"
    )


def dry_run_send_steps(steps, delay: float):
    """只打印将要发送的帧和 guard 等待策略，不连接 ESP32。"""
    control_byte = autoff.build_output_control_byte(delay)
    wait_sec = get_inter_frame_wait_sec(delay)

    print("\n=== dry-run: 只打印帧，不连接ESP32 ===")
    print(f"正常输出控制: {autoff.describe_control_byte(control_byte)}")
    print(f"auto-off换算: {autoff.describe_delay_autoff(delay)}")
    print(describe_guard_timing(delay))

    for i, step in enumerate(steps, start=1):
        payload = autoff.build_payload(step, delay)
        frame = autoff.build_frame(step, delay)
        print(f"  步骤 {i}: channels={step}")
        print(f"          payload={list(payload)}")
        print(f"          frame={autoff.base.frame_to_hex(frame)}")
        if i < len(steps):
            print(f"          PC下一帧前等待: {wait_sec:.3f}s")

    gate_off_frame = autoff.build_control_frame(autoff.CONTROL_GATE_OFF)
    print(f"退出关闭控制: {autoff.describe_control_byte(autoff.CONTROL_GATE_OFF)}")
    print(f"          frame={autoff.base.frame_to_hex(gate_off_frame)}")
    print("dry-run完成，未发送硬件，也未写入评分CSV")


def tcp_send_steps(sock, steps, delay: float):
    """按步骤逐帧发送，并在下一帧前等待 auto-off + guard。"""
    control_byte = autoff.build_output_control_byte(delay)
    wait_sec = get_inter_frame_wait_sec(delay)

    print(f"正常输出控制: {autoff.describe_control_byte(control_byte)}")
    print(f"auto-off换算: {autoff.describe_delay_autoff(delay)}")
    print(describe_guard_timing(delay))

    for i, step in enumerate(steps, start=1):
        frame = autoff.build_frame(step, delay)
        sock.sendall(frame)
        print(f"  已发送步骤 {i}/{len(steps)}: {step}")

        if i < len(steps):
            print(f"  等待auto-off + guard后发送下一帧: {wait_sec:.3f}s")
            time.sleep(wait_sec)

    print("本次模式发送完成，TCP连接保持打开；最后一步会由ESP32按auto-off时间关闭输出")


def experiment_send_steps_once(sock, steps, delay: float, dry_run: bool, show_frames: bool):
    """随机实验版发送一次 trial，并在下一帧前等待 auto-off + guard。"""
    first_send_time = None
    control_byte = autoff.build_output_control_byte(delay)
    wait_sec = get_inter_frame_wait_sec(delay)

    if dry_run:
        if show_frames:
            print("\n=== dry-run: 模拟发送本次trial刺激 ===")
            print(f"auto-off换算: {autoff.describe_delay_autoff(delay)}")
            print(f"正常输出控制: {autoff.describe_control_byte(control_byte)}")
            print(describe_guard_timing(delay))

        for i, step in enumerate(steps, start=1):
            frame = autoff.build_frame(step, delay)
            if first_send_time is None:
                first_send_time = time.perf_counter()
            if show_frames:
                print(f"  步骤 {i}: channels={step}")
                print(f"          frame={autoff.base.frame_to_hex(frame)}")
            if show_frames and i < len(steps):
                print(f"          PC下一帧前等待: {wait_sec:.3f}s")
        return first_send_time

    if show_frames:
        print(f"auto-off换算: {autoff.describe_delay_autoff(delay)}")
        print(f"正常输出控制: {autoff.describe_control_byte(control_byte)}")
        print(describe_guard_timing(delay))

    for i, step in enumerate(steps, start=1):
        frame = autoff.build_frame(step, delay)
        sock.sendall(frame)
        if first_send_time is None:
            first_send_time = time.perf_counter()
        if show_frames:
            print(f"  已发送步骤 {i}/{len(steps)}: {step}")
            print(f"          frame={autoff.base.frame_to_hex(frame)}")
        if i < len(steps):
            if show_frames:
                print(f"  等待auto-off + guard后发送下一帧: {wait_sec:.3f}s")
            time.sleep(wait_sec)

    return first_send_time


def run_scoring_mode():
    """运行普通模式选择 + 评分版，并启用 guard 等待。"""
    autoff.dry_run_send_steps = dry_run_send_steps
    autoff.tcp_send_steps = tcp_send_steps
    autoff.interactive_mode_selection()


def run_experiment_mode():
    """运行随机实验版，并启用 guard 等待。"""
    experiment_autoff.send_steps_once = experiment_send_steps_once
    experiment_autoff.main()


def choose_entry_mode() -> str:
    """选择普通打分版或随机实验版。"""
    while True:
        print("\n请选择入口:")
        print("  1. 普通模式选择 + 评分")
        print("  2. 随机实验池")
        choice = input("请输入入口 (默认: 1): ").strip().lower()

        if not choice or choice in ("1", "score", "scoring", "普通", "评分"):
            return "scoring"
        if choice in ("2", "experiment", "exp", "实验", "随机"):
            return "experiment"

        print("  错误: 请输入 1 或 2")


def main():
    """主函数。"""
    print("ESP32 HV507 gate auto-off + PC frame guard 测试入口")
    print(f"默认PC帧间guard: {INTER_FRAME_GUARD_SEC:.3f}s")

    entry_mode = choose_entry_mode()
    if entry_mode == "experiment":
        run_experiment_mode()
    else:
        run_scoring_mode()


if __name__ == "__main__":
    main()
