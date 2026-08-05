"""
实验池配置文件。

TRIAL_POOL 定义本轮实验候选模式，以及每个模式出现几次。
CHOICE_LABELS 定义受试者界面看到的代称；这些代称会映射回真实模式名。
"""

# 实验池：模式名称必须存在于 config.py 的 OUTPUT_MODES 中。
TRIAL_POOL = {
    "single_list1_col_l2r": 2,
    "edge_single_list1_row_top": 2,
    "edge_single_list1_row_bottom": 1,
    "edge_pair_list1_then_list2_row_top":1

}

# 受试者看到的选项标签。标签应在本轮实验池中保持唯一。
CHOICE_LABELS = {
    "single_list1_col_l2r": "列→",
    "single_list1_col_r2l": "列←",
    "single_list1_col_t2b": "上到下列",
    "single_list1_col_b2t": "下到上列",
    "single_list1_row_l2r": "左到右行",
    "single_list1_row_r2l": "右到左行",
    "single_list1_row_t2b": "行↓",
    "single_list1_row_b2t": "行↑",
    "staggered_list1_first_col_l2r": "L1先列->",
    "staggered_list1_first_col_r2l": "L1先列<-",
    "staggered_list1_first_col_t2b": "L1先列上到下",
    "staggered_list1_first_col_b2t": "L1先列下到上",
    "staggered_list1_first_row_l2r": "L1先行->",
    "staggered_list1_first_row_r2l": "L1先行<-",
    "staggered_list1_first_row_t2b": "L1先行上到下",
    "staggered_list1_first_row_b2t": "L1先行下到上",
    "staggered_list2_first_col_l2r": "L2先列->",
    "staggered_list2_first_col_r2l": "L2先列<-",
    "staggered_list2_first_col_t2b": "L2先列上到下",
    "staggered_list2_first_col_b2t": "L2先列下到上",
    "staggered_list2_first_row_l2r": "L2先行->",
    "staggered_list2_first_row_r2l": "L2先行<-",
    "staggered_list2_first_row_t2b": "L2先行上到下",
    "staggered_list2_first_row_b2t": "L2先行下到上",
    "sequential_list1_then_list2_col": "L1后L2列",
    "sequential_list1_then_list2_row": "L1后L2行",
    "sequential_list2_then_list1_col": "L2后L1列",
    "sequential_list2_then_list1_row": "L2后L1行",
    "edge_single_list1_row_top": "L1上边",
    "edge_single_list1_row_bottom": "L1下边",
    "edge_single_list1_col_left": "L1左边",
    "edge_single_list1_col_right": "L1右边",
    "edge_single_list2_row_top": "L2上边",
    "edge_single_list2_row_bottom": "L2下边",
    "edge_single_list2_col_left": "L2左边",
    "edge_single_list2_col_right": "L2右边",
    "edge_pair_list1_then_list2_row_top": "L1→L2上边",
    "edge_pair_list1_then_list2_row_bottom": "L1→L2下边",
    "edge_pair_list1_then_list2_col_left": "L1→L2左边",
    "edge_pair_list1_then_list2_col_right": "L1→L2右边",
    "edge_pair_list2_then_list1_row_top": "L2→L1上边",
    "edge_pair_list2_then_list1_row_bottom": "L2→L1下边",
    "edge_pair_list2_then_list1_col_left": "L2→L1左边",
    "edge_pair_list2_then_list1_col_right": "L2→L1右边",
}

# 每题最多允许重播的次数。超过后本题记为未作答并进入下一题。
MAX_REPLAYS = 3

# None 表示每次真随机；填整数可复现实验顺序。
RANDOM_SEED = None

# 正式实验结果和随机顺序记录。
RESULTS_CSV = "experiment_results.csv"
SEQUENCE_CSV_TEMPLATE = "experiment_sequence_{session_id}.csv"
