# -*- coding: utf-8 -*-
"""
价格计算工具 - 公共数据配置
数据来源：《价格自动计算表2.xlsx》（镀锌带彩带价格 / 价格计算表 / 财务核算规则）
说明：
- 汇率、钢价为"最新一期"快照，页面上可临时修改；长期维护直接改这里。
- 厚度阶梯 / 彩价阶梯来自价格计算表 F 列、I 列的 IF 公式。
- 系数（密度、毛利、镀层、增值税）来自公式内常量。
"""

# ============ 当前价格快照（对应钢价表最新行，2026-10-20） ============
EXCHANGE_RATE = 6.6606          # 汇率（美元→人民币）
STEEL_BASE_03 = 3830            # 0.3 普锌带钢价（元/吨），底料阶梯的基准

# 彩涂带钢价（元/吨），键为厚度 mm
COLOR_PRICES = {
    0.16: 6150,
    0.18: 6050,
    0.20: 5850,
    0.25: None,   # 0.25 = (0.20 + 0.30) / 2，由阶梯公式推导
    0.30: 5250,
    0.35: 5150,
    0.40: 5000,
}

# Z180 高锌层彩涂价（元/吨）
Z180_PRICES = {
    0.50: 5100,
    0.55: 5000,
    0.70: 4600,   # 0.7 = 0.55 价 - 350
}

# ============ 厚度阶梯（底料价 = 0.3普钢价 + 偏移），单位 mm / 元/吨 ============
# E >= 阈值 取该档；从厚到薄匹配
THICKNESS_LADDER = [
    # (厚度下限, 价差)
    (0.70, -300),
    (0.66, -250),
    (0.56, -200),
    (0.46, -150),
    (0.38, -100),
    (0.35, -50),
    (0.30, 0),
    (0.27, +50),
    (0.25, +150),
    (0.23, +300),
    (0.20, +450),
]

# ============ 彩价阶梯（面带含税价），键为面带厚 H ============
# 0.25 特殊：彩0.3价 + 200
COLOR_LADDER = {
    0.40: 'color_040',
    0.39: 'color_040',
    0.35: 'color_035',
    0.30: 'color_030',
    0.25: 'color_030_plus_200',
    0.20: 'color_020',
    0.18: 'color_016',
}

# ============ 公式常量 ============
STEEL_DENSITY = 7.85        # 钢密度 g/cm³
FOB_MARGIN = 1.08           # FOB 毛利/损耗系数
COATING_DEDUCT = 0.02       # 面料计价时扣除的镀层厚度 mm
VAT_FACTOR = 1.09           # 增值税系数（含税/1.09 = 不含税）

# ============ 纸箱费分档（元/只），按长度 C 是否 >= 3.6m ============
CARTON_FEE = {
    'long_ge_3.6': 0.50,
    'long_ge_3.6_light': 0.25,
    'short_lt_3.6': 0.45,
    'short_lt_3.6_light': 0.20,
}

# ============ 常用加点参考（元/吨，来自财务核算规则表） ============
DEFAULT_MARKUP = 600        # 普通轻钢（轻钢产品按"元/吨"加点）
MARKUP_REFERENCE = {
    '普通轻钢': 600,
    '蛇皮骨': 650,
    '高锌层': 1000,
    '打孔边角 0.4mm以下': 1000,
    '打孔边角 0.4-0.45': 800,
    '打孔边角 0.45以上': 600,
    '打孔沿地(加拿大)': 1200,
}

# 烤漆龙骨加成率（成本加成法默认值，待与实际业务核对后调整）
DEFAULT_MARKUP_RATE = 1.08


def base_material_price(thickness, steel_base=None):
    """底料价：按厚度阶梯查 0.3 普钢价 + 偏移"""
    base = steel_base if steel_base is not None else STEEL_BASE_03
    t = float(thickness)
    for threshold, diff in THICKNESS_LADDER:
        if t >= threshold:
            return base + diff
    # 薄于 0.20 的超出阶梯范围，按最薄一档
    return base + THICKNESS_LADDER[-1][1]


def face_material_price(face_thick, color_prices=None):
    """面带含税价：按彩价阶梯"""
    prices = color_prices if color_prices is not None else COLOR_PRICES
    h = round(float(face_thick), 2)
    if h in (0.40, 0.39):
        return prices.get(0.40)
    if h == 0.35:
        return prices.get(0.35)
    if h == 0.30:
        return prices.get(0.30)
    if h == 0.25:
        p30 = prices.get(0.30)
        return (p30 + 200) if p30 is not None else None
    if h == 0.20:
        return prices.get(0.20)
    if h == 0.18:
        return prices.get(0.16)
    return None


def calc(length_m, width_mm, thickness_mm, face_width_mm, face_thick_mm,
         carton_fee, markup, exchange_rate=None, steel_base=None,
         color_prices=None, fob_margin=None):
    """
    核心计算链（与 Excel 公式一一对应）：
      单只重 J     = D×E×C×7.85/1000
      底料价 F     = 厚度阶梯(E, 0.3普钢价)
      面带含税 I   = 彩价阶梯(H, 彩涂价表)
      净成本 L     = D×E×C×7.85×F/1e6 + G×(H-0.02)×C×7.85×I/1.09/1e6 + K
      FOB N(USD)   = J×(F+M)/汇率/1000×1.08
    返回 dict，含全部中间量。
    """
    rate = exchange_rate if exchange_rate is not None else EXCHANGE_RATE
    margin = fob_margin if fob_margin is not None else FOB_MARGIN

    unit_weight = width_mm * thickness_mm * length_m * STEEL_DENSITY / 1000.0
    f_base = base_material_price(thickness_mm, steel_base)
    i_face = face_material_price(face_thick_mm, color_prices)

    cost_base_mat = width_mm * thickness_mm * length_m * STEEL_DENSITY * f_base / 1e6
    cost_face_mat = (face_width_mm * (face_thick_mm - COATING_DEDUCT) * length_m
                     * STEEL_DENSITY * i_face / VAT_FACTOR / 1e6) if i_face is not None else None
    net_cost_rmb = cost_base_mat + cost_face_mat + carton_fee
    fob_usd = unit_weight * (f_base + markup) / rate / 1000.0 * margin

    return {
        'unit_weight': round(unit_weight, 4),          # 单只重 kg
        'base_price': f_base,                          # 底料价 元/吨
        'face_price': i_face,                          # 面带含税 元/吨
        'cost_base_mat': round(cost_base_mat, 4),      # 底料成本 元
        'cost_face_mat': round(cost_face_mat, 4),      # 面料成本 元
        'net_cost_rmb': round(net_cost_rmb, 4),        # 人民币净成本 元
        'fob_usd': round(fob_usd, 4),                  # FOB 单只价 USD
    }
