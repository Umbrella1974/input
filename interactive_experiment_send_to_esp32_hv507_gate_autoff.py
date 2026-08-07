#!/usr/bin/env python3
"""
随机实验入口（HV507 gate auto-off发送 + 受试者作答 + 反应时间记录）。

核心流程沿用 interactive_experiment_send_to_esp32_hv507_gate.py：
1. 从 experiment_pool_config.py 读取实验池和每个模式出现次数
2. 展开并随机打乱 trial 顺序
3. 每个 trial 按 HV507 gate auto-off 协议发送到 ESP32
4. 受试者从代称选项中作答，或请求重播
5. 记录真实模式、答案、正确性、反应时间和重播次数

本文件只适配新版esp32_fast_main_hv507_gate_autoff.py的control byte：
    control_byte = 0xE0 | duration_code
    duration_code = ceil(delay_ms / 50ms)，范围限制在1..31
"""

import time

import interactive_experiment_send_to_esp32_hv507_gate as experiment
import interactive_send_to_esp32_hv507_gate_autoff_with_scoring as gate


def send_steps_once(sock, steps, delay: float, dry_run: bool, show_frames: bool):
    """发送或dry-run展示一次trial刺激，并返回计时起点。"""
    first_send_time = None
    control_byte = gate.build_output_control_byte(delay)

    if dry_run:
        if show_frames:
            print("\n=== dry-run: 模拟发送本次trial刺激 ===")
            print(f"auto-off换算: {gate.describe_delay_autoff(delay)}")
            print(f"正常输出控制: {gate.describe_control_byte(control_byte)}")

        for i, step in enumerate(steps, start=1):
            frame = gate.build_frame(step, delay)
            if first_send_time is None:
                first_send_time = time.perf_counter()
            if show_frames:
                print(f"  步骤 {i}: channels={step}")
                print(f"          frame={gate.base.frame_to_hex(frame)}")
        return first_send_time

    if show_frames:
        print(f"auto-off换算: {gate.describe_delay_autoff(delay)}")
        print(f"正常输出控制: {gate.describe_control_byte(control_byte)}")

    for i, step in enumerate(steps, start=1):
        frame = gate.build_frame(step, delay)
        sock.sendall(frame)
        if first_send_time is None:
            first_send_time = time.perf_counter()
        if show_frames:
            print(f"  已发送步骤 {i}/{len(steps)}: {step}")
            print(f"          frame={gate.base.frame_to_hex(frame)}")
        if i < len(steps):
            time.sleep(delay)

    return first_send_time


def patch_experiment_module():
    """让原实验流程使用新版auto-off发送器。"""
    experiment.gate = gate
    experiment.send_steps_once = send_steps_once


def main():
    """主函数。"""
    patch_experiment_module()
    print("矩阵随机实验 - ESP32 HV507 gate auto-off发送版")

    try:
        experiment.validate_experiment_config()
        gate.base.validate_matrices(gate.base.MATRIX1, gate.base.MATRIX2)
    except Exception as e:
        print(f"配置或矩阵验证失败: {e}")
        return

    session_id = experiment.get_session_id()
    run_mode = experiment.choose_run_mode()
    show_frames = experiment.choose_show_frames(run_mode)
    dry_run, host, port = gate.base.get_connection_settings()
    sequence = experiment.build_trial_sequence()
    choice_modes = experiment.active_pool_modes()

    print(f"\nsession_id: {session_id}")
    print(f"运行模式: {run_mode}")
    print(f"显示trial帧内容: {show_frames}")
    print(f"trial总数: {len(sequence)}")
    print(f"最大重播次数: {experiment.exp_config.MAX_REPLAYS}")
    print(f"协议auto-off单位: {gate.HV507_DURATION_UNIT_MS}ms/code")
    print(f"最大auto-off时间: {gate.duration_code_to_ms(gate.HV507_MAX_DURATION_CODE)}ms")
    print("实验选项:")
    for mode in choice_modes:
        print(f"  {experiment.get_label(mode)}")

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
                print(f"  {trial_index}. {experiment.get_label(mode)}")
        else:
            print("受试模式：随机顺序已生成，但不在屏幕显示正确标签")
    else:
        experiment.save_sequence(session_id, sequence)

    try:
        for trial_index, true_mode in enumerate(sequence, start=1):
            result = experiment.run_trial(
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
