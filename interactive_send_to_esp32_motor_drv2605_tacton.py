#!/usr/bin/env python3
"""
Interactive sender for ESP32 DRV2605 motor tactons.

ESP32 side:
    esp32_motor_drv2605_tacton_server.py

Text protocol over TCP, newline separated:
    PLAY <tacton_id> [rough_duration_ms]
    STOP
    PING

Enabled tacton ids:
    1, 4, 5, 8, 9, 10, 11
"""

import socket
import time


DEFAULT_PORT = 12346
DEFAULT_CONNECT_TIMEOUT = 5.0
ESP32_READY_DELAY = 0.2

ROUGH_SLIP_TACTON_ID = 11
VALID_TACTON_IDS = (1, 4, 5, 8, 9, 10, ROUGH_SLIP_TACTON_ID)
DEFAULT_ROUGH_SLIP_DURATION_MS = 2000


def validate_tacton_id(tacton_id: int) -> int:
    """Validate and normalize a tacton id."""
    if not isinstance(tacton_id, int):
        raise ValueError(f"tacton_id must be int: {tacton_id!r}")
    if tacton_id not in VALID_TACTON_IDS:
        raise ValueError(f"unknown tacton_id: {tacton_id}; valid ids: {VALID_TACTON_IDS}")
    return tacton_id


def validate_rough_duration_ms(duration_ms: int) -> int:
    """Validate and normalize Rough Slip duration."""
    try:
        value = int(duration_ms)
    except (TypeError, ValueError):
        raise ValueError(f"invalid Rough Slip duration: {duration_ms!r}")

    if value <= 0:
        raise ValueError(f"Rough Slip duration must be positive: {value}")

    return value


def build_play_command(tacton_id: int, rough_duration_ms: int = DEFAULT_ROUGH_SLIP_DURATION_MS) -> str:
    """Build one ESP32 text command."""
    tacton_id = validate_tacton_id(tacton_id)

    if tacton_id == ROUGH_SLIP_TACTON_ID:
        duration_ms = validate_rough_duration_ms(rough_duration_ms)
        return f"PLAY {tacton_id} {duration_ms}\n"

    return f"PLAY {tacton_id}\n"


def build_stop_command() -> str:
    """Build a STOP command."""
    return "STOP\n"


def get_yes_no(prompt: str, default: bool = True) -> bool:
    """Read a y/n answer with a default."""
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


def get_int(prompt: str, default: int) -> int:
    """Read a non-negative integer with a default."""
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


def get_connection_settings():
    """Read dry-run and ESP32 TCP connection settings."""
    dry_run = get_yes_no("是否dry-run（只打印命令，不连接ESP32）？", default=True)
    if dry_run:
        return True, None, DEFAULT_PORT

    while True:
        host = input("请输入ESP32 IP地址: ").strip()
        if host:
            break
        print("  错误: IP地址不能为空")

    port = get_int("请输入ESP32 TCP端口", default=DEFAULT_PORT)
    return False, host, port


def connect_esp32(host: str, port: int):
    """Open one persistent TCP connection to ESP32."""
    print(f"\n正在连接ESP32 DRV2605 tacton server: {host}:{port}")
    sock = socket.create_connection((host, port), timeout=DEFAULT_CONNECT_TIMEOUT)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    sock.settimeout(DEFAULT_CONNECT_TIMEOUT)
    print("连接成功")

    if ESP32_READY_DELAY > 0:
        time.sleep(ESP32_READY_DELAY)

    return sock


def close_esp32(sock):
    """Close ESP32 TCP connection."""
    if sock is None:
        return

    try:
        sock.close()
        print("ESP32 TCP连接已断开")
    except Exception as e:
        print(f"关闭ESP32连接时出错: {e}")


def read_response(sock) -> str:
    """Read one newline-terminated ESP32 response."""
    chunks = []

    while True:
        data = sock.recv(64)
        if not data:
            raise ConnectionError("ESP32 closed connection while waiting for response")

        chunks.append(data)
        if b"\n" in data:
            break

    response = b"".join(chunks).split(b"\n", 1)[0].decode("utf-8", errors="replace").strip()
    if response.startswith("ERR"):
        raise RuntimeError(f"ESP32返回错误: {response}")
    return response


def tcp_send_command(sock, command: str, wait_response: bool = True):
    """Send one newline-terminated text command."""
    if sock is None:
        raise ValueError("sock is None")
    sock.sendall(command.encode("ascii"))
    if wait_response:
        return read_response(sock)
    return ""


def tcp_play_tacton(sock, tacton_id: int, rough_duration_ms: int = DEFAULT_ROUGH_SLIP_DURATION_MS):
    """Send one tacton play command."""
    command = build_play_command(tacton_id, rough_duration_ms)
    response = tcp_send_command(sock, command)
    print(f"  已发送: {command.strip()} ({response})")


def dry_run_play_tacton(tacton_id: int, rough_duration_ms: int = DEFAULT_ROUGH_SLIP_DURATION_MS):
    """Print the command that would be sent."""
    command = build_play_command(tacton_id, rough_duration_ms)
    print("\n=== dry-run: 只打印命令，不连接ESP32 ===")
    print(f"  command={command.strip()}")


def send_stop(sock):
    """Best-effort STOP command before closing."""
    if sock is None:
        return

    try:
        command = build_stop_command()
        response = tcp_send_command(sock, command)
        print(f"已发送STOP ({response})")
    except Exception as e:
        print(f"发送STOP失败，将继续关闭TCP连接: {e}")


def select_tacton(choice: str) -> int:
    """Parse user tacton selection."""
    try:
        tacton_id = int(choice.strip())
    except ValueError:
        raise ValueError("请输入tacton编号")

    return validate_tacton_id(tacton_id)


def print_tacton_list():
    """Print enabled tactons."""
    print("\n可用tacton:")
    for tacton_id in VALID_TACTON_IDS:
        if tacton_id == ROUGH_SLIP_TACTON_ID:
            print(f"  {tacton_id:2d}. Rough Slip")
        else:
            print(f"  {tacton_id:2d}. Haptic Icon {tacton_id}")


def interactive_mode_selection():
    """Interactive tacton sender."""
    print("DRV2605 Motor Tacton - ESP32 TCP发送")

    dry_run, host, port = get_connection_settings()
    rough_duration_ms = get_int(
        "请输入Rough Slip播放时长ms",
        default=DEFAULT_ROUGH_SLIP_DURATION_MS,
    )
    validate_rough_duration_ms(rough_duration_ms)

    sock = None
    if not dry_run:
        try:
            sock = connect_esp32(host, port)
        except Exception as e:
            print(f"连接ESP32失败: {e}")
            return

    try:
        while True:
            print_tacton_list()
            print("\n可用命令:")
            print("  q - 退出")
            print("  x - 发送STOP并退出")
            print("  输入tacton编号播放")

            choice = input("\n请输入命令或tacton编号: ").strip().lower()

            if choice in ("q", "quit", "exit"):
                print("退出程序")
                break
            if choice == "x":
                print("准备STOP并退出")
                break

            try:
                tacton_id = select_tacton(choice)
                if dry_run:
                    dry_run_play_tacton(tacton_id, rough_duration_ms)
                else:
                    tcp_play_tacton(sock, tacton_id, rough_duration_ms)
            except Exception as e:
                print(f"  错误: {e}")
                continue
    finally:
        if not dry_run:
            send_stop(sock)
        close_esp32(sock)


def main():
    interactive_mode_selection()


if __name__ == "__main__":
    main()
