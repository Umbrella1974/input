#!/usr/bin/env python3
"""
交互式发送到ESP32 HV507 gate版（配置延迟 + TCP发送 + 评分保存）

功能：
1. 复用现有矩阵输出、配置延迟、TCP连接和CSV评分逻辑
2. 面向esp32_fast_main_hv507_gate.py的控制帧协议
3. 每个输出步骤发送: [0xE0][channel_data...]
4. 退出或断开时尽力发送: [0x80]，请求ESP32关闭HV507输出gate
5. 真实发送模式下启动时连接一次ESP32，后续多个模式复用同一个TCP连接

ESP32 gate协议：
    MAGIC(4B) + length(1B) + payload(N<=128B) + checksum(1B)

payload格式：
    正常输出: [0xE0, channel1, channel2, ...]
    关闭gate: [0x80]
"""

import time

import interactive_send_to_esp32_with_scoring as base


CONTROL_FRAME_MASK = 0x80
HV507_OUTPUT_ENABLE_MASK = 0x40
HV507_UPDATE_CHANNELS_MASK = 0x20

CONTROL_UPDATE_AND_ENABLE = (
    CONTROL_FRAME_MASK | HV507_OUTPUT_ENABLE_MASK | HV507_UPDATE_CHANNELS_MASK
)
CONTROL_GATE_OFF = CONTROL_FRAME_MASK


def describe_control_byte(control_byte: int) -> str:
    """返回HV507 gate控制字节含义。"""
    is_control = bool(control_byte & CONTROL_FRAME_MASK)
    should_enable = bool(control_byte & HV507_OUTPUT_ENABLE_MASK)
    should_update = bool(control_byte & HV507_UPDATE_CHANNELS_MASK)

    return (
        f"control_byte=0x{control_byte:02X} "
        f"(control={is_control}, update={should_update}, enable={should_enable})"
    )


def build_payload(channels) -> bytes:
    """构造正常输出payload: [0xE0][channel_data...]。"""
    channel_payload = base.validate_channels(channels)

    if len(channel_payload) > 127:
        raise ValueError("HV507 gate模式下每帧最多支持127个通道，因为需要1字节control_byte")

    return bytes([CONTROL_UPDATE_AND_ENABLE]) + channel_payload


def build_frame(channels) -> bytes:
    """将一个输出步骤打包成ESP32 HV507 gate版协议帧。"""
    payload = build_payload(channels)
    return base.MAGIC + bytes([len(payload)]) + payload + bytes([base.quick_checksum(payload)])


def build_control_frame(control_byte: int) -> bytes:
    """构造只有control byte的控制帧。"""
    if not 0 <= control_byte <= 255:
        raise ValueError(f"非法控制字节: {control_byte}")

    payload = bytes([control_byte])
    return base.MAGIC + bytes([len(payload)]) + payload + bytes([base.quick_checksum(payload)])


def validate_steps(steps):
    """提前验证所有步骤，避免发送到一半才发现非法payload。"""
    if not steps:
        raise ValueError("模式没有生成任何输出步骤")

    for step in steps:
        build_payload(step)


def dry_run_send_steps(steps):
    """只打印将要发送的HV507 gate版帧，不连接ESP32。"""
    print("\n=== dry-run: 只打印帧，不连接ESP32 ===")
    print(f"正常输出控制: {describe_control_byte(CONTROL_UPDATE_AND_ENABLE)}")

    for i, step in enumerate(steps, start=1):
        payload = build_payload(step)
        frame = build_frame(step)
        print(f"  步骤 {i}: channels={step}")
        print(f"          payload={list(payload)}")
        print(f"          frame={base.frame_to_hex(frame)}")

    gate_off_frame = build_control_frame(CONTROL_GATE_OFF)
    print(f"退出关闭控制: {describe_control_byte(CONTROL_GATE_OFF)}")
    print(f"          frame={base.frame_to_hex(gate_off_frame)}")
    print("dry-run完成，未发送硬件，也未写入评分CSV")


def tcp_send_steps(sock, steps, delay: float):
    """使用已经建立的TCP连接，按步骤逐帧发送HV507 gate版协议帧。"""
    print(f"正常输出控制: {describe_control_byte(CONTROL_UPDATE_AND_ENABLE)}")

    for i, step in enumerate(steps, start=1):
        frame = build_frame(step)
        sock.sendall(frame)
        print(f"  已发送步骤 {i}/{len(steps)}: {step}")

        if i < len(steps):
            time.sleep(delay)

    print("本次模式发送完成，TCP连接保持打开")


def send_gate_off(sock):
    """退出前尽力发送gate-off控制帧。"""
    if sock is None:
        return

    try:
        frame = build_control_frame(CONTROL_GATE_OFF)
        sock.sendall(frame)
        print(f"已发送HV507 gate-off: {describe_control_byte(CONTROL_GATE_OFF)}")
    except Exception as e:
        print(f"发送HV507 gate-off失败，将继续关闭TCP连接: {e}")


def interactive_mode_selection():
    """交互式模式选择主函数。"""
    print("矩阵输出系统 - ESP32 HV507 gate发送 + 配置延迟 + 评分版")
    print(f"矩阵1: {base.MATRIX1}")
    print(f"矩阵2: {base.MATRIX2}")

    try:
        base.validate_matrices(base.MATRIX1, base.MATRIX2)
        print("矩阵验证通过")
    except Exception as e:
        print(f"矩阵验证失败: {e}")
        return

    dry_run, host, port = base.get_connection_settings()
    sock = None

    if not dry_run:
        try:
            sock = base.connect_esp32(host, port)
        except Exception as e:
            print(f"连接ESP32失败: {e}")
            return

    try:
        print("\n" + "=" * 60)
        print("交互式模式选择（ESP32 HV507 gate发送）")
        print("=" * 60)
        print(f"正常输出控制: {describe_control_byte(CONTROL_UPDATE_AND_ENABLE)}")
        print(f"退出关闭控制: {describe_control_byte(CONTROL_GATE_OFF)}")

        while True:
            print("\n可用命令:")
            print("  'q' - 退出程序")
            print("  'x' - 发送gate-off，断开ESP32连接并退出")
            print("  'd' - 显示所有模式延迟配置")
            print("  's' - 查看已保存的评分结果")
            print("  'm' - 显示模式列表")
            print("  输入模式名称或编号选择模式")

            modes = sorted(base.OUTPUT_MODES.keys())
            base.print_mode_list(modes)

            choice = input("\n请输入命令或选择模式: ").strip()

            if choice.lower() == "q":
                print("退出程序")
                break
            if choice.lower() == "x":
                if dry_run:
                    print("dry-run模式下无需断开ESP32，退出程序")
                else:
                    print("准备发送gate-off并断开ESP32连接")
                break
            if choice.lower() == "d":
                base.show_mode_delays()
                continue
            if choice.lower() == "s":
                base.show_csv_contents()
                continue
            if choice.lower() == "m":
                continue

            try:
                mode_name = base.select_mode(modes, choice)
                delay = base.choose_delay(mode_name)
                steps = base.compute_mode_steps(mode_name, base.MATRIX1, base.MATRIX2)
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

            score = base.get_nonnegative_int("请为本次真实发送评分（非负整数）", default=5)
            base.save_to_csv(mode_name, delay, score)

            print("\n" + "-" * 60)
    finally:
        if not dry_run:
            send_gate_off(sock)
        base.close_esp32(sock)


def main():
    """主函数。"""
    interactive_mode_selection()


if __name__ == "__main__":
    main()
