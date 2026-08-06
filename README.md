# input_function

这是一个用于生成矩阵逐步输出序列的 Python 小项目。它把一个或两个方阵按照指定方向、轴向和组合方式转换成一组步骤输出，每个步骤都是一个列表。

项目当前只依赖 Python 标准库，不需要安装第三方包。

## 已经实现的功能

### 1. 核心矩阵输出引擎

核心逻辑在 `matrix_output.py` 中，已经实现：

- `get_column(matrix, col_idx, reverse=False)`：提取指定列。
- `get_row(matrix, row_idx, reverse=False)`：提取指定行。
- `get_edge_line(matrix, edge)`：提取矩阵的上、下、左、右边缘行/列。
- `single_matrix(matrix, axis='col', direction='l2r')`：单矩阵输出。
- `staggered_matrices(matrix1, matrix2, axis='col', direction='l2r', first='matrix1')`：双矩阵错位输出。
- `sequential_matrices(matrix1, matrix2, axis='col', order='matrix1_first')`：双矩阵顺序输出。
- `edge_single_matrix(matrix1, matrix2, matrix='matrix1', edge='top')`：单个矩阵边缘输出。
- `edge_pair_matrices(matrix1, matrix2, edge='top', order='matrix1_first')`：两个矩阵同一边缘按顺序输出。
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

`OUTPUT_MODES` 当前配置了 44 种模式：

- 类别 A：单矩阵输出，8 种。支持按列/按行，以及 `l2r`、`r2l`、`t2b`、`b2t` 四个方向。
- 类别 B：双矩阵错位输出，`matrix1` 先开始，8 种。
- 类别 C：双矩阵错位输出，`matrix2` 先开始，8 种。
- 类别 D：双矩阵顺序输出，4 种。支持先 `matrix1` 后 `matrix2`，或先 `matrix2` 后 `matrix1`，并支持按列或按行。
- 类别 E：单矩阵边缘输出，8 种。支持 `matrix1` 或 `matrix2` 的上、下、左、右边缘。
- 类别 F：双矩阵边缘顺序输出，`matrix1` 先、`matrix2` 后，4 种。
- 类别 G：双矩阵边缘顺序输出，`matrix2` 先、`matrix1` 后，4 种。

`CATEGORIES` 已经把这些模式按 A 到 G 七类整理好，方便批量运行或展示。

### 3. 延迟配置

`mode_delays_config.py` 已经为每个模式配置默认延迟：

- 单矩阵按列模式默认 `0.3` 秒。
- 单矩阵按行模式默认 `0.4` 秒。
- 双矩阵错位按列模式默认 `0.5` 秒。
- 双矩阵错位按行模式默认 `0.6` 秒。
- 顺序输出模式默认 `0.4` 秒。
- 单矩阵边缘模式默认 `0.4` 秒。
- 双矩阵边缘顺序模式默认 `0.5` 秒。
- 未配置模式使用 `DEFAULT_DELAY = 0.5`。

可通过 `get_mode_delay(mode_name)` 获取某个模式的默认延迟。

### 4. 演示、交互与ESP32发送脚本

项目提供了多个可直接运行的脚本：

- `demo.py`：演示核心模式、按类别运行部分模式，并提供基础交互式模式选择。
- `interactive_with_config_delay.py`：交互式选择模式，并从 `mode_delays_config.py` 读取默认延迟；用户也可以覆盖延迟。
- `interactive_with_scoring.py`：交互式选择模式、输入延迟、运行输出、输入评分，并把结果保存到 `output_scores.csv`。
- `interactive_with_config_delay_and_scoring.py`：同时支持模式默认延迟、手动覆盖延迟、输出后评分和 CSV 保存。
- `interactive_send_to_esp32_with_scoring.py`：同时支持模式默认延迟、TCP 逐步发送到 ESP32、发送后评分和 CSV 保存。
- `interactive_send_to_esp32_pwm_with_scoring.py`：面向 `esp32_fast_main_pwm.py`，在 ESP32 TCP 发送基础上可选附加 PWM 控制字节。
- `interactive_send_to_esp32_hv507_gate_with_scoring.py`：面向 `esp32_fast_main_hv507_gate.py`，使用 HV507 gate 控制帧发送输出步骤，并在退出时请求关闭输出 gate。
- `interactive_send_to_esp32_hv507_gate_autoff_with_scoring.py`：面向 `esp32_fast_main_hv507_gate_autoff.py`，使用带 auto-off 时间码的 HV507 gate 控制帧发送输出步骤。
- `interactive_experiment_send_to_esp32_hv507_gate.py`：随机实验入口，从实验池生成随机 trial 顺序，发送刺激后记录受试者答案、反应时间和重播次数。
- `interactive_experiment_send_to_esp32_hv507_gate_autoff.py`：面向 `esp32_fast_main_hv507_gate_autoff.py` 的随机实验入口，实验逻辑同上，但发送协议使用 auto-off 控制字节。
- `interactive_send_to_esp32_hv507_gate_autoff_guard.py`：PC 端最小测试入口，复用 auto-off 协议，但在下一帧发送前等待 `auto_off_time + guard`，用于避免下一帧提前截断上一帧 BL 高电平。

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

运行 ESP32 PWM 发送版本：

```bash
python interactive_send_to_esp32_pwm_with_scoring.py
```

运行 ESP32 HV507 gate 发送版本：

```bash
python interactive_send_to_esp32_hv507_gate_with_scoring.py
```

运行 ESP32 HV507 gate auto-off 发送版本：

```bash
python interactive_send_to_esp32_hv507_gate_autoff_with_scoring.py
```

运行随机实验版本：

```bash
python interactive_experiment_send_to_esp32_hv507_gate.py
```

运行随机实验 auto-off 版本：

```bash
python interactive_experiment_send_to_esp32_hv507_gate_autoff.py
```

运行 HV507 gate auto-off + PC frame guard 测试入口：

```bash
python interactive_send_to_esp32_hv507_gate_autoff_guard.py
```

该入口启动后会先选择：

```text
1. 普通模式选择 + 评分
2. 随机实验池
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

PWM 发送版本会额外询问是否启用 PWM 控制。默认不启用，此时 payload 与普通 ESP32 发送版本一致：

```text
[channel1, channel2, ...]
```

启用 PWM 后，每个 payload 前面会增加一个控制字节：

```text
[control_byte, channel1, channel2, ...]
```

控制字节按 `esp32_fast_main_pwm.py` 的规则生成：

```python
control_byte = 0x80 | (pwm_mode << 2) | duration_code
```

当前可选 PWM 模式：

- `0`：关闭
- `1`：开启，100%，1kHz
- `2`：1kHz，50%
- `3`：500Hz，75%
- `4`：2kHz，25%

当前可选持续时间：

- `0`：持续
- `1`：100ms
- `2`：500ms
- `3`：1000ms

HV507 gate 发送版本面向 `esp32_fast_main_hv507_gate.py`。这个 ESP32 程序把 BL 当成输出 gate，默认关闭输出；因此 PC 端每个正常输出步骤都会发送带控制字节的 payload：

```text
[0xE0, channel1, channel2, ...]
```

`0xE0` 的含义：

- `0x80`：这是 control frame。
- `0x40`：打开 HV507 输出 gate。
- `0x20`：使用本帧通道数据更新并 latch HV507。

例如步骤 `[1, 4, 7]` 会发送：

```text
AA 55 AA 55 04 E0 01 04 07 EC
```

真实发送模式退出时，程序会尽力先发送 gate-off 控制帧，再关闭 TCP 连接：

```text
AA 55 AA 55 01 80 80
```

如果 PC 端发送 gate-off 失败，程序仍会关闭 TCP 连接；ESP32 端在客户端断开时也会调用 `force_outputs_off()` 作为本地安全兜底。

HV507 gate auto-off 发送版本面向 `esp32_fast_main_hv507_gate_autoff.py`。协议外壳不变，但正常输出帧的 control byte 会携带 auto-off 时间码：

```text
[0xE0 | duration_code, channel1, channel2, ...]
```

其中：

```text
duration_code = ceil(delay_ms / 50ms)
auto_off_ms = duration_code * 50ms
```

`duration_code` 会限制在 `1..31`，因此最短 auto-off 为 `50ms`，最长为 `1550ms`。例如模式 delay 为 `0.3` 秒时：

```text
duration_code = 6
control_byte = 0xE6
```

步骤 `[1, 4, 7]` 会发送：

```text
AA 55 AA 55 04 E6 01 04 07 F2
```

退出时仍会尽力发送 gate-off：

```text
AA 55 AA 55 01 80 80
```

HV507 gate auto-off + PC frame guard 测试入口是在上一版 auto-off 基础上的 PC 端最小改动。它的原因是：PC 端原来在 `sendall()` 返回后等待 `delay` 秒再发下一帧，但 ESP32 端真正的 BL 高电平开始时间发生在“收到帧、解析、SPI 写入、latch、打开 BL”之后。如果下一帧在当前帧 auto-off 前到达，ESP32 处理下一帧时会先 `_blank_outputs()`，上一帧 BL 高电平就会被提前截断。

这个测试入口不改变 control byte、payload、checksum，也不改变 ESP32 端代码，只改变 PC 端下一帧发送前的等待策略：

```text
PC下一帧前等待 = auto_off_time + INTER_FRAME_GUARD_SEC
```

当前：

```text
INTER_FRAME_GUARD_SEC = 0.20
```

例如模式 delay 为 `0.3` 秒时，ESP32 auto-off 仍然是 `300ms`，PC 端会在两帧之间等待：

```text
300ms + 200ms = 500ms
```

这样用于测试“BL 高电平不足 300ms/500ms 是否来自下一帧过早到达”。如果测量结果变稳定，说明后续可以保留 PC guard，或者进一步把排队/序列播放逻辑下沉到 ESP32。

随机实验版本使用 `experiment_pool_config.py` 配置实验池：

- `TRIAL_POOL`：哪些模式进入实验池，以及每个模式出现几次。
- `CHOICE_LABELS`：受试者看到的代称选项，不能直接等于真实模式名。
- `MAX_REPLAYS`：每题最多允许重播次数。
- `RANDOM_SEED`：`None` 表示真随机，填整数可复现实验顺序。
- `RESULTS_CSV`：trial 结果文件，默认 `experiment_results.csv`。

实验启动时会选择：

- `session_id`：直接回车自动生成。
- `run_mode`：`train` 训练模式或 `test` 受试模式。
- 是否显示本次 trial 帧内容：训练模式默认显示，受试模式默认隐藏。
- 是否 dry-run：dry-run 不连接 ESP32，也不写实验 CSV。

训练模式会显示本题正确的 `CHOICE_LABELS` 标签；受试模式不会显示正确标签。真实发送模式会保存完整随机顺序到 `experiment_sequence_{session_id}.csv`，每题结果写入 `experiment_results.csv`，字段包含：

```text
timestamp,session_id,run_mode,trial_index,true_mode,true_label,answer_mode,answer_label,is_correct,reaction_time_sec,replay_count,status
```

训练/受试模式与帧显示开关：

- `train`：训练模式，屏幕会提示本题正确标签，例如 `训练提示: 本次信号 = 列→`。
- `test`：受试模式，屏幕不会提示本题正确标签。
- `是否显示本次trial帧内容`：控制屏幕上是否打印 channels 和 frame；训练模式默认 `y`，受试模式默认 `n`。
- 以上设置在 dry-run 和真实 ESP32 连接模式下都生效。

当前可以放入 `TRIAL_POOL` 的模式必须来自 `config.py` 的 `OUTPUT_MODES`。下面这些模式都已经在 `experiment_pool_config.py` 里配置了受试者可见标签。

类别 A：单矩阵输出

```text
single_list1_col_l2r  -> 列→
single_list1_col_r2l  -> 列←
single_list1_col_t2b  -> 上到下列
single_list1_col_b2t  -> 下到上列
single_list1_row_l2r  -> 左到右行
single_list1_row_r2l  -> 右到左行
single_list1_row_t2b  -> 行↓
single_list1_row_b2t  -> 行↑
```

类别 B：双矩阵错位输出，list1 先

```text
staggered_list1_first_col_l2r -> L1先列->
staggered_list1_first_col_r2l -> L1先列<-
staggered_list1_first_col_t2b -> L1先列上到下
staggered_list1_first_col_b2t -> L1先列下到上
staggered_list1_first_row_l2r -> L1先行->
staggered_list1_first_row_r2l -> L1先行<-
staggered_list1_first_row_t2b -> L1先行上到下
staggered_list1_first_row_b2t -> L1先行下到上
```

类别 C：双矩阵错位输出，list2 先

```text
staggered_list2_first_col_l2r -> L2先列->
staggered_list2_first_col_r2l -> L2先列<-
staggered_list2_first_col_t2b -> L2先列上到下
staggered_list2_first_col_b2t -> L2先列下到上
staggered_list2_first_row_l2r -> L2先行->
staggered_list2_first_row_r2l -> L2先行<-
staggered_list2_first_row_t2b -> L2先行上到下
staggered_list2_first_row_b2t -> L2先行下到上
```

类别 D：双矩阵顺序输出

```text
sequential_list1_then_list2_col -> L1后L2列
sequential_list1_then_list2_row -> L1后L2行
sequential_list2_then_list1_col -> L2后L1列
sequential_list2_then_list1_row -> L2后L1行
```

类别 E：单矩阵边缘输出

```text
edge_single_list1_row_top    -> L1上边
edge_single_list1_row_bottom -> L1下边
edge_single_list1_col_left   -> L1左边
edge_single_list1_col_right  -> L1右边
edge_single_list2_row_top    -> L2上边
edge_single_list2_row_bottom -> L2下边
edge_single_list2_col_left   -> L2左边
edge_single_list2_col_right  -> L2右边
```

类别 F：双矩阵边缘输出，list1 后接 list2

```text
edge_pair_list1_then_list2_row_top    -> L1→L2上边
edge_pair_list1_then_list2_row_bottom -> L1→L2下边
edge_pair_list1_then_list2_col_left   -> L1→L2左边
edge_pair_list1_then_list2_col_right  -> L1→L2右边
```

类别 G：双矩阵边缘输出，list2 后接 list1

```text
edge_pair_list2_then_list1_row_top    -> L2→L1上边
edge_pair_list2_then_list1_row_bottom -> L2→L1下边
edge_pair_list2_then_list1_col_left   -> L2→L1左边
edge_pair_list2_then_list1_col_right  -> L2→L1右边
```

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
from matrix_output import (
    single_matrix,
    staggered_matrices,
    sequential_matrices,
    edge_single_matrix,
    edge_pair_matrices,
)
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

# 单矩阵边缘：matrix1 第一行
steps = edge_single_matrix(MATRIX1, MATRIX2, matrix='matrix1', edge='top')

# 双矩阵边缘：先 matrix2 右列，再 matrix1 右列
steps = edge_pair_matrices(MATRIX1, MATRIX2, edge='right', order='matrix2_first')
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
├── interactive_send_to_esp32_pwm_with_scoring.py # 配置延迟 + TCP发送ESP32 PWM版 + 评分保存入口
├── interactive_send_to_esp32_hv507_gate_with_scoring.py # 配置延迟 + TCP发送ESP32 HV507 gate版 + 评分保存入口
├── interactive_send_to_esp32_hv507_gate_autoff_with_scoring.py # 配置延迟 + TCP发送ESP32 HV507 gate auto-off版 + 评分保存入口
├── interactive_send_to_esp32_hv507_gate_autoff_guard.py # auto-off + PC帧间guard测试入口
├── experiment_pool_config.py            # 随机实验池和选项标签配置
├── interactive_experiment_send_to_esp32_hv507_gate.py # 随机实验入口
├── interactive_experiment_send_to_esp32_hv507_gate_autoff.py # 随机实验auto-off入口
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
- 类别 A 的传统单矩阵模式目前只使用 `MATRIX1`；类别 E 的单矩阵边缘模式可以指定 `MATRIX1` 或 `MATRIX2`。
- 双矩阵错位输出的总步骤数为 `N + 1`。
- 双矩阵顺序输出的总步骤数为 `2N`。
- 单矩阵边缘输出的总步骤数为 `1`。
- 双矩阵边缘顺序输出的总步骤数为 `2`。
- 交互脚本中的延迟只影响打印节奏；核心函数会一次性返回完整步骤列表。
- ESP32 发送入口只负责发送当前步骤的通道 payload，不负责硬件安全关闭。
- ESP32 发送入口会检查每个通道必须是 `0-127` 范围内的整数，且每帧 payload 长度不能超过 `128`。
- ESP32 PWM 发送入口默认不启用 PWM；启用后每帧会占用 1 字节 control byte，因此每帧最多 `127` 个通道。
- ESP32 HV507 gate 发送入口每个正常输出步骤都会占用 1 字节 control byte，因此每帧最多 `127` 个通道；退出时会尝试发送 gate-off，但最终硬件兜底仍应由 ESP32 端断连处理负责。
- `interactive_send_to_esp32_hv507_gate_autoff_guard.py` 是 PC 端最小测试方案：它通过增加帧间等待避免下一帧提前截断上一帧，但 ESP32 端仍不是完整的内部序列播放器。

## 如何扩展

- 修改输入矩阵：编辑 `config.py` 中的 `MATRIX1` 和 `MATRIX2`。
- 添加输出模式：在 `config.py` 的 `OUTPUT_MODES` 中新增模式名和参数映射。
- 调整默认延迟：编辑 `mode_delays_config.py` 中的 `MODE_DELAYS`。
- 扩展非方阵支持：需要调整 `validate_matrices()` 以及依赖 `len(matrix)` 假设方阵大小的输出逻辑。
