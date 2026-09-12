#!/usr/bin/env python3
"""
手动输入单个 channel 并发送到 ESP32 HV507 gate auto-off 版。

发送协议复用 interactive_send_to_esp32_hv507_gate_autoff_with_scoring.py：
    MAGIC(4B) + length(1B) + payload(N) + checksum(1B)

每次键盘输入一个数字 channel，例如 82，实际发送：
    payload = [control_byte, 82]

其中 control_byte 包含 HV507 gate open、channel update/latch 和 auto-off 时间码。
退出时会尽量发送 gate-off：
    payload = [0x80]
"""

import interactive_send_to_esp32_hv507_gate_autoff_with_scoring as gate


DEFAULT_DELAY = 0.3


def get_delay() -> float:
    """获取本脚本固定使用的 auto-off/delay 时间。"""
    while True:
        try:
            text = input(f"请输入 auto-off/delay 时间（秒，默认: {DEFAULT_DELAY}）: ").strip()
            if not text:
                return DEFAULT_DELAY

            delay = float(text)
            if delay < 0:
                print("  错误: 请输入非负数")
                continue
            return delay
        except ValueError:
            print("  错误: 请输入有效数字，例如 0.3")


def parse_channel(text: str) -> int:
    """解析单个 HV507 channel，范围沿用现有 ESP32 解析器的 0-127。"""
    try:
        channel = int(text)
    except ValueError:
        raise ValueError("请输入整数 channel，例如 82")

    if not 0 <= channel < 128:
        raise ValueError("channel 必须在 0-127 范围内")

    return channel


def print_frame(channel: int, delay: float):
    """打印本次将发送的 payload 和 frame。"""
    payload = gate.build_payload([channel], delay)
    frame = gate.build_frame([channel], delay)
    print(f"  channel payload: [{channel}]")
    print(f"  full payload: {list(payload)}")
    print(f"  frame: {gate.base.frame_to_hex(frame)}")


def send_single_channel(sock, channel: int, delay: float, dry_run: bool):
    """发送或 dry-run 单个 channel。"""
    print_frame(channel, delay)

    if dry_run:
        print("  dry-run: 未发送到 ESP32")
        return

    frame = gate.build_frame([channel], delay)
    sock.sendall(frame)
    print(f"  已发送 channel {channel}，ESP32 将按 auto-off 时间关闭输出")


def interactive_single_channel_sender():
    """交互式输入 channel 并发送。"""
    print("ESP32 HV507 gate auto-off 单 channel 手动发送")
    print(f"协议 auto-off 单位: {gate.HV507_DURATION_UNIT_MS}ms/code")
    print(f"最大 auto-off 时间: {gate.duration_code_to_ms(gate.HV507_MAX_DURATION_CODE)}ms")

    dry_run, host, port = gate.base.get_connection_settings()
    delay = get_delay()
    control_byte = gate.build_output_control_byte(delay)
    sock = None

    print(f"正常输出控制: {gate.describe_control_byte(control_byte)}")
    print(f"auto-off 换算: {gate.describe_delay_autoff(delay)}")
    print(f"退出关闭控制: {gate.describe_control_byte(gate.CONTROL_GATE_OFF)}")

    if not dry_run:
        try:
            sock = gate.base.connect_esp32(host, port)
        except Exception as e:
            print(f"连接 ESP32 失败: {e}")
            return

    try:
        while True:
            print("\n可用输入:")
            print("  0-127 - 发送这个单个 channel")
            print("  q     - 退出程序")
            print("  x     - 发送 gate-off 并退出")
            print("  off   - 立即发送一次 gate-off，继续保持连接")

            choice = input("请输入 channel 或命令: ").strip().lower()

            if choice == "q":
                print("退出程序")
                break

            if choice == "x":
                print("准备发送 gate-off 并退出")
                break

            if choice == "off":
                if dry_run:
                    frame = gate.build_control_frame(gate.CONTROL_GATE_OFF)
                    print(f"  dry-run gate-off frame: {gate.base.frame_to_hex(frame)}")
                else:
                    gate.send_gate_off(sock)
                continue

            try:
                channel = parse_channel(choice)
                send_single_channel(sock, channel, delay, dry_run)
            except Exception as e:
                print(f"  错误: {e}")
                continue
    finally:
        if not dry_run:
            gate.send_gate_off(sock)
        gate.base.close_esp32(sock)


def main():
    interactive_single_channel_sender()


if __name__ == "__main__":
    main()
