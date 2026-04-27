"""
模式延迟配置文件 - 为每个输出模式配置默认延迟时间
"""

# 每个输出模式的默认延迟时间（秒）
MODE_DELAYS = {
    # 类别A: 单个矩阵
    'single_list1_col_l2r': 0.3,
    'single_list1_col_r2l': 0.3,
    'single_list1_col_t2b': 0.3,
    'single_list1_col_b2t': 0.3,

    'single_list1_row_l2r': 0.4,
    'single_list1_row_r2l': 0.4,
    'single_list1_row_t2b': 0.4,
    'single_list1_row_b2t': 0.4,

    # 类别B: 双矩阵错位，matrix1先
    'staggered_list1_first_col_l2r': 0.5,
    'staggered_list1_first_col_r2l': 0.5,
    'staggered_list1_first_col_t2b': 0.5,
    'staggered_list1_first_col_b2t': 0.5,

    'staggered_list1_first_row_l2r': 0.6,
    'staggered_list1_first_row_r2l': 0.6,
    'staggered_list1_first_row_t2b': 0.6,
    'staggered_list1_first_row_b2t': 0.6,

    # 类别C: 双矩阵错位，matrix2先
    'staggered_list2_first_col_l2r': 0.5,
    'staggered_list2_first_col_r2l': 0.5,
    'staggered_list2_first_col_t2b': 0.5,
    'staggered_list2_first_col_b2t': 0.5,

    'staggered_list2_first_row_l2r': 0.6,
    'staggered_list2_first_row_r2l': 0.6,
    'staggered_list2_first_row_t2b': 0.6,
    'staggered_list2_first_row_b2t': 0.6,

    # 类别D: 顺序输出
    'sequential_list1_then_list2_col': 0.4,
    'sequential_list1_then_list2_row': 0.4,
    'sequential_list2_then_list1_col': 0.4,
    'sequential_list2_then_list1_row': 0.4,
}

# 默认延迟（当模式不在配置中时使用）
DEFAULT_DELAY = 0.5


def get_mode_delay(mode_name: str) -> float:
    """获取模式的延迟配置

    Args:
        mode_name: 模式名称

    Returns:
        延迟时间（秒）
    """
    return MODE_DELAYS.get(mode_name, DEFAULT_DELAY)


def list_modes_with_delays() -> list:
    """列出所有模式及其延迟配置

    Returns:
        列表，每个元素是(模式名称, 延迟)元组
    """
    return [(mode, delay) for mode, delay in MODE_DELAYS.items()]