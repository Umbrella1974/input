#!/usr/bin/env python3
"""
交互式发送到ESP32 PWM版（配置延迟 + TCP发送 + 评分保存）

功能：
1. 复用现有矩阵输出、配置延迟、TCP连接和CSV评分逻辑
2. 支持发送传统payload: [channel_data...]
3. 可选发送PWM payload: [control_byte][channel_data...]
4. 真实发送模式下启动时连接一次ESP32，后续多个模式复用同一个TCP连接

ESP32 PWM协议：
    MAGIC(4B) + length(1B) + payload(N<=128B) + checksum(1B)

payload格式：
    传统模式: [channel1, channel2, ...]
    PWM模式: [control_byte, channel1, channel2, ...]
"""

import time

import interactive_send_to_esp32_with_scoring as base


PWM_MODE_DESCRIPTIONS = {
    0: "关闭",
    1: "开启，100%，1kHz",
    2: "1kHz，50%",
    3: "500Hz，75%",
    4: "2kHz，25%",
}

PWM_DURATION_DESCRIPTIONS = {
    0: "持续",
    1: "100ms",
    2: "500ms",
    3: "1000ms",
}


def get_choice(prompt: str, default: int, valid_values) -> int:
    """获取限定范围内的整数选择。"""
    valid_set = set(valid_values)

    while True:
        value = base.get_int(prompt, default=default)
        if value in valid_set:
            return value
        print(f"  错误: 请输入以下值之一: {sorted(valid_set)}")


def choose_pwm_settings():
    """选择PWM配置；返回None表示传统模式。"""
    enable_pwm = base.get_yes_no("是否启用PWM控制？", default=False)
    if not enable_pwm:
        print("使用传统模式payload，不附加PWM控制字节")
        return None

    print("\nPWM模式:")
    for mode, description in PWM_MODE_DESCRIPTIONS.items():
        print(f"  {mode}. {description}")
    pwm_mode = get_choice("请选择PWM模式", default=1, valid_values=PWM_MODE_DESCRIPTIONS.keys())

    print("\nPWM持续时间:")
    for code, description in PWM_DURATION_DESCRIPTIONS.items():
        print(f"  {code}. {description}")
    duration_code = get_choice(
        "请选择PWM持续时间代码",
        default=0,
        valid_values=PWM_DURATION_DESCRIPTIONS.keys(),
    )

    control_byte = 0x80 | (pwm_mode << 2) | duration_code
    print(
        f"启用PWM: mode={pwm_mode} ({PWM_MODE_DESCRIPTIONS[pwm_mode]}), "
        f"duration={duration_code} ({PWM_DURATION_DESCRIPTIONS[duration_code]}), "
        f"control_byte=0x{control_byte:02X}"
    )

    return {
        "mode": pwm_mode,
        "duration_code": duration_code,
        "control_byte": control_byte,
    }


def describe_pwm_settings(pwm_settings):
    """返回当前PWM配置的简短说明。"""
    if pwm_settings is None:
        return "传统模式，无PWM控制字节"

    mode = pwm_settings["mode"]
    duration_code = pwm_settings["duration_code"]
    control_byte = pwm_settings["control_byte"]

    return (
        f"PWM mode={mode} ({PWM_MODE_DESCRIPTIONS[mode]}), "
        f"duration={duration_code} ({PWM_DURATION_DESCRIPTIONS[duration_code]}), "
        f"control_byte=0x{control_byte:02X}"
    )


def build_payload(channels, pwm_settings) -> bytes:
    """构造传统或PWM payload。"""
    channel_payload = base.validate_channels(channels)

    if pwm_settings is None:
        return channel_payload

    if len(channel_payload) > 127:
        raise ValueError("PWM模式下每帧最多支持127个通道，因为需要1字节control_byte")

    control_byte = pwm_settings["control_byte"]
    if not 0x80 <= control_byte <= 0x9F:
        raise ValueError(f"非法PWM控制字节: 0x{control_byte:02X}")

    return bytes([control_byte]) + channel_payload


def build_frame(channels, pwm_settings) -> bytes:
    """将一个输出步骤打包成ESP32 PWM版协议帧。"""
    payload = build_payload(channels, pwm_settings)
    return base.MAGIC + bytes([len(payload)]) + payload + bytes([base.quick_checksum(payload)])


def validate_steps(steps, pwm_settings):
    """提前验证所有步骤，避免发送到一半才发现非法payload。"""
    if not steps:
        raise ValueError("模式没有生成任何输出步骤")

    for step in steps:
        build_payload(step, pwm_settings)


def dry_run_send_steps(steps, pwm_settings):
    """只打印将要发送的PWM版帧，不连接ESP32。"""
    print("\n=== dry-run: 只打印帧，不连接ESP32 ===")
    print(f"PWM设置: {describe_pwm_settings(pwm_settings)}")

    for i, step in enumerate(steps, start=1):
        payload = build_payload(step, pwm_settings)
        frame = build_frame(step, pwm_settings)
        print(f"  步骤 {i}: channels={step}")
        print(f"          payload={list(payload)}")
        print(f"          frame={base.frame_to_hex(frame)}")

    print("dry-run完成，未发送硬件，也未写入评分CSV")


def tcp_send_steps(sock, steps, delay: float, pwm_settings):
    """使用已经建立的TCP连接，按步骤逐帧发送PWM版协议帧。"""
    print(f"PWM设置: {describe_pwm_settings(pwm_settings)}")

    for i, step in enumerate(steps, start=1):
        frame = build_frame(step, pwm_settings)
        sock.sendall(frame)
        print(f"  已发送步骤 {i}/{len(steps)}: {step}")

        if i < len(steps):
            time.sleep(delay)

    print("本次模式发送完成，TCP连接保持打开")


def interactive_mode_selection():
    """交互式模式选择主函数。"""
    print("矩阵输出系统 - ESP32 PWM发送 + 配置延迟 + 评分版")
    print(f"矩阵1: {base.MATRIX1}")
    print(f"矩阵2: {base.MATRIX2}")

    try:
        base.validate_matrices(base.MATRIX1, base.MATRIX2)
        print("矩阵验证通过")
    except Exception as e:
        print(f"矩阵验证失败: {e}")
        return

    dry_run, host, port = base.get_connection_settings()
    pwm_settings = choose_pwm_settings()
    sock = None

    if not dry_run:
        try:
            sock = base.connect_esp32(host, port)
        except Exception as e:
            print(f"连接ESP32失败: {e}")
            return

    try:
        print("\n" + "=" * 60)
        print("交互式模式选择（ESP32 PWM发送）")
        print("=" * 60)
        print(f"当前PWM设置: {describe_pwm_settings(pwm_settings)}")

        while True:
            print("\n可用命令:")
            print("  'q' - 退出程序")
            print("  'x' - 断开ESP32连接并退出")
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
                    print("准备断开ESP32连接并退出程序")
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
                validate_steps(steps, pwm_settings)
            except Exception as e:
                print(f"  错误: {e}")
                continue

            print(f"\n模式生成完成，共 {len(steps)} 个步骤")

            try:
                if dry_run:
                    dry_run_send_steps(steps, pwm_settings)
                    continue

                tcp_send_steps(sock, steps, delay, pwm_settings)
            except Exception as e:
                print(f"  发送失败: {e}")
                break

            score = base.get_nonnegative_int("请为本次真实发送评分（非负整数）", default=5)
            base.save_to_csv(mode_name, delay, score)

            print("\n" + "-" * 60)
    finally:
        base.close_esp32(sock)


def main():
    """主函数。"""
    interactive_mode_selection()


if __name__ == "__main__":
    main()
