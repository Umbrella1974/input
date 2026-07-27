# input_function

这是一个用于生成矩阵逐步输出序列的 Python 小项目。它把一个或两个方阵按照指定方向、轴向和组合方式转换成一组步骤输出，每个步骤都是一个列表。

项目当前只依赖 Python 标准库，不需要安装第三方包。

## 已经实现的功能

### 1. 核心矩阵输出引擎

核心逻辑在 `matrix_output.py` 中，已经实现：

- `get_column(matrix, col_idx, reverse=False)`：提取指定列。
- `get_row(matrix, row_idx, reverse=False)`：提取指定行。
- `single_matrix(matrix, axis='col', direction='l2r')`：单矩阵输出。
- `staggered_matrices(matrix1, matrix2, axis='col', direction='l2r', first='matrix1')`：双矩阵错位输出。
- `sequential_matrices(matrix1, matrix2, axis='col', order='matrix1_first')`：双矩阵顺序输出。
- `validate_matrices(matrix1, matrix2)`：验证两个矩阵是否为相同大小的方阵。

这些函数返回的是 `List[List[Any]]`，也就是“步骤列表”。例如每一列或每一行会作为一个步骤输出；双矩阵错位时，同一步里的两个行/列会拼接到同一个列表里。

### 2. 输出模式配置

`config.py` 中已经定义了两个默认 3x3 矩阵：

```python
MATRIX1 = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9],
]

MATRIX2 = [
    [10, 11, 12],
    [13, 14, 15],
    [16, 17, 18],
]
```

`OUTPUT_MODES` 当前配置了 28 种模式：

- 类别 A：单矩阵输出，8 种。支持按列/按行，以及 `l2r`、`r2l`、`t2b`、`b2t` 四个方向。
- 类别 B：双矩阵错位输出，`matrix1` 先开始，8 种。
- 类别 C：双矩阵错位输出，`matrix2` 先开始，8 种。
- 类别 D：双矩阵顺序输出，4 种。支持先 `matrix1` 后 `matrix2`，或先 `matrix2` 后 `matrix1`，并支持按列或按行。

`CATEGORIES` 已经把这些模式按 A、B、C、D 四类整理好，方便批量运行或展示。

### 3. 延迟配置

`mode_delays_config.py` 已经为每个模式配置默认延迟：

- 单矩阵按列模式默认 `0.3` 秒。
- 单矩阵按行模式默认 `0.4` 秒。
- 双矩阵错位按列模式默认 `0.5` 秒。
- 双矩阵错位按行模式默认 `0.6` 秒。
- 顺序输出模式默认 `0.4` 秒。
- 未配置模式使用 `DEFAULT_DELAY = 0.5`。

可通过 `get_mode_delay(mode_name)` 获取某个模式的默认延迟。

### 4. 演示、交互与ESP32发送脚本

项目提供了多个可直接运行的脚本：

- `demo.py`：演示核心模式、按类别运行部分模式，并提供基础交互式模式选择。
- `interactive_with_config_delay.py`：交互式选择模式，并从 `mode_delays_config.py` 读取默认延迟；用户也可以覆盖延迟。
- `interactive_with_scoring.py`：交互式选择模式、输入延迟、运行输出、输入评分，并把结果保存到 `output_scores.csv`。
- `interactive_with_config_delay_and_scoring.py`：同时支持模式默认延迟、手动覆盖延迟、输出后评分和 CSV 保存。
- `interactive_send_to_esp32_with_scoring.py`：同时支持模式默认延迟、TCP 逐步发送到 ESP32、发送后评分和 CSV 保存。

`output_scores.csv` 当前已有示例评分记录，字段为：

```text
timestamp,mode_name,delay,score
```

### 5. 测试与快速验证

项目已经包含两个验证脚本：

- `test.py`：用断言验证基础函数、单矩阵输出、错位输出、顺序输出和矩阵验证逻辑。
- `quick_test.py`：快速打印多个代表性模式的输出结果，便于人工检查。

当前运行结果：`python test.py` 通过，`python quick_test.py` 可正常输出示例步骤。

## 如何运行

进入项目目录：

```bash
cd D:\research_history\first_one\research_code\input\input_function
```

运行测试：

```bash
python test.py
```

快速查看输出效果：

```bash
python quick_test.py
```

运行基础演示：

```bash
python demo.py
```

运行带默认延迟配置的交互版本：

```bash
python interactive_with_config_delay.py
```

运行带评分保存的交互版本：

```bash
python interactive_with_scoring.py
```

运行“默认延迟 + 评分保存”的综合交互版本：

```bash
python interactive_with_config_delay_and_scoring.py
```

运行 ESP32 发送版本：

```bash
python interactive_send_to_esp32_with_scoring.py
```

启动后会先询问是否 `dry-run`：

- 直接回车：使用默认 `dry-run = y`，只打印将要发送的二进制帧，不连接 ESP32，也不写评分 CSV。
- 输入 `n`：进入真实发送模式，需要输入 ESP32 的 IP 地址和 TCP 端口，端口默认 `12345`。

真实发送模式下，程序会在进入模式菜单前连接一次 ESP32，等待 `7.5` 秒，让 ESP32 端完成首次连接后的上电准备。之后可以连续选择多个模式发送，这些模式会复用同一个 TCP 连接，不会每个模式重新连接。每个步骤发送一帧，步骤之间等待该模式的 delay。

菜单命令中：

- `q`：退出程序，并关闭 ESP32 TCP 连接。
- `x`：断开 ESP32 TCP 连接并退出程序。
- `d`：显示所有模式延迟配置。
- `s`：查看已保存的评分结果。
- `m`：重新显示模式列表。

ESP32 端需要运行兼容下面协议的 TCP 服务：

```text
MAGIC(4B) + length(1B) + payload(N<=128B) + checksum(1B)
```

其中：

```python
MAGIC = b"\xAA\x55\xAA\x55"
payload = bytes(step)
checksum = sum(payload) & 0xFF
```

例如步骤 `[1, 4, 7]` 会发送为：

```text
AA 55 AA 55 03 01 04 07 0C
```

## 代码调用示例

```python
from matrix_output import single_matrix, staggered_matrices, sequential_matrices
from config import MATRIX1, MATRIX2

# 单矩阵：按列从左到右输出
steps = single_matrix(MATRIX1, axis='col', direction='l2r')

# 双矩阵错位：matrix1 先，从左到右按列错位
steps = staggered_matrices(
    MATRIX1,
    MATRIX2,
    axis='col',
    direction='l2r',
    first='matrix1',
)

# 双矩阵顺序：先 matrix1 后 matrix2，按行输出
steps = sequential_matrices(
    MATRIX1,
    MATRIX2,
    axis='row',
    order='matrix1_first',
)
```

## 输出示例

以 `staggered_list1_first_col_l2r` 为例，输入默认矩阵时输出：

```text
步骤 1: [1, 4, 7]
步骤 2: [2, 5, 8, 10, 13, 16]
步骤 3: [3, 6, 9, 11, 14, 17]
步骤 4: [12, 15, 18]
```

注意：这里是列表拼接，不是数值相加。

## 文件说明

```text
input_function/
├── matrix_output.py                    # 核心矩阵输出引擎
├── config.py                           # 默认矩阵、模式映射、模式分类
├── mode_delays_config.py               # 每个模式的默认延迟配置
├── demo.py                             # 基础演示和交互选择
├── interactive_with_config_delay.py    # 使用配置延迟的交互版本
├── interactive_with_scoring.py         # 带评分和 CSV 保存的交互版本
├── interactive_with_config_delay_and_scoring.py # 配置延迟 + 评分保存入口
├── interactive_send_to_esp32_with_scoring.py    # 配置延迟 + TCP发送ESP32 + 评分保存入口
├── test.py                             # 断言式测试脚本
├── quick_test.py                       # 快速人工检查脚本
├── output_scores.csv                   # 评分结果 CSV
├── 33input_function.md                 # 原始需求说明
├── nn_input_function.md                # 架构设计说明
└── CLAUDE.md                           # 既有项目说明文档
```

## 当前限制和注意事项

- 当前验证逻辑要求两个输入矩阵都是相同大小的方阵。
- 核心函数支持任意 `N x N` 方阵，不限于默认的 3x3。
- 单矩阵模式目前只使用 `MATRIX1`。
- 双矩阵错位输出的总步骤数为 `N + 1`。
- 双矩阵顺序输出的总步骤数为 `2N`。
- 交互脚本中的延迟只影响打印节奏；核心函数会一次性返回完整步骤列表。
- ESP32 发送入口只负责发送当前步骤的通道 payload，不负责硬件安全关闭。
- ESP32 发送入口会检查每个通道必须是 `0-127` 范围内的整数，且每帧 payload 长度不能超过 `128`。

## 如何扩展

- 修改输入矩阵：编辑 `config.py` 中的 `MATRIX1` 和 `MATRIX2`。
- 添加输出模式：在 `config.py` 的 `OUTPUT_MODES` 中新增模式名和参数映射。
- 调整默认延迟：编辑 `mode_delays_config.py` 中的 `MODE_DELAYS`。
- 扩展非方阵支持：需要调整 `validate_matrices()` 以及依赖 `len(matrix)` 假设方阵大小的输出逻辑。
