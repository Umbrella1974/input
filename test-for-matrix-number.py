import socket
import time
from datetime import datetime


# =========================
# 配置
# =========================

DEVICE_IP = "192.168.1.100"   # 改成你的设备实际IP
DEVICE_PORT = 12345

START_NUMBER = 64
END_NUMBER = 127

SEND_INTERVAL = 1.0           # 每个数据间隔 1 秒
CONNECT_WAIT = 8.0            # 设备连接后内部会等待7秒，这里等8秒


# =========================
# 协议
# =========================

MAGIC = b"\xAA\x55\xAA\x55"


def checksum(payload: bytes) -> int:
    """
    与设备端 quick_checksum() 完全一致：
    sum(payload) & 0xFF
    """
    return sum(payload) & 0xFF


def make_frame(value: int) -> bytes:
    """
    构造协议帧：

    [AA 55 AA 55]
    [payload长度]
    [payload]
    [checksum]
    """

    if not 0 <= value <= 255:
        raise ValueError("value 必须在 0~255 范围内")

    # 本例每次只发送一个数字
    payload = bytes([value])

    length = len(payload)

    frame = (
        MAGIC
        + bytes([length])
        + payload
        + bytes([checksum(payload)])
    )

    return frame


def print_frame(value: int, frame: bytes):
    """以16进制显示实际发送的数据"""
    hex_string = " ".join(f"{b:02X}" for b in frame)

    now = datetime.now().strftime("%H:%M:%S.%f")[:-3]

    print(
        f"[{now}] "
        f"发送数字={value:3d}  "
        f"HEX: {hex_string}"
    )


def main():

    print("====================================")
    print("HV507 PC TCP Sender")
    print("====================================")
    print(f"设备地址: {DEVICE_IP}:{DEVICE_PORT}")
    print(f"发送范围: {START_NUMBER} ~ {END_NUMBER}")
    print(f"发送间隔: {SEND_INTERVAL} 秒")
    print()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 尽量减少TCP小数据包延迟
    sock.setsockopt(
        socket.IPPROTO_TCP,
        socket.TCP_NODELAY,
        1
    )

    try:
        print(f"正在连接 {DEVICE_IP}:{DEVICE_PORT} ...")

        sock.connect((DEVICE_IP, DEVICE_PORT))

        print("TCP连接成功。")

        # --------------------------------------------------
        # 你的设备端 accept() 后存在 time.sleep(7)
        # 所以不要立即发送
        # --------------------------------------------------

        print(
            f"等待设备高压上电初始化 "
            f"{CONNECT_WAIT:.1f} 秒..."
        )

        time.sleep(CONNECT_WAIT)

        print()
        print("开始发送...")
        print()

        # Python range 的结束值不包含，
        # 因此 END_NUMBER + 1
        for value in range(
            START_NUMBER,
            END_NUMBER + 1
        ):

            frame = make_frame(value)

            # 发送完整协议帧
            sock.sendall(frame)

            print_frame(value, frame)

            # 最后一帧后不用再等待
            if value != END_NUMBER:
                time.sleep(SEND_INTERVAL)

        print()
        print("65~128 已全部发送完成。")

    except ConnectionRefusedError:
        print()
        print("连接被拒绝。")
        print("请检查：")
        print("1. DEVICE_IP 是否正确")
        print("2. PC 和设备是否在同一网络")
        print("3. 设备 TCP Server 是否已经启动")
        print("4. 端口是否为 12345")

    except TimeoutError:
        print("连接设备超时。")

    except KeyboardInterrupt:
        print()
        print("用户停止发送。")

    except OSError as e:
        print(f"Socket错误: {e}")

    finally:
        try:
            sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass

        sock.close()
        print("TCP连接已关闭。")


if __name__ == "__main__":
    main()