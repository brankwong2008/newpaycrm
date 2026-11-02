# -*- coding: utf-8 -*-
from django.shortcuts import render
from dipay import price_config
from dipay.models import PriceConfig, ExchangeRate


def get_config_value(key, fallback):
    """读取 stark 后台维护的价格参数，读不到时用 price_config 兜底"""
    try:
        obj = PriceConfig.objects.get(key=key)
        return float(obj.value)
    except Exception:
        return fallback


def get_latest_usd_rate():
    """取汇率表最新美元汇率，返回 (rate, date)；没有数据返回 (None, None)"""
    try:
        r = (ExchangeRate.objects.filter(currency__title='美元')
             .order_by('-update_date', '-id').first())
        if r:
            return float(r.rate), r.update_date
    except Exception:
        pass
    return None, None


def price_calc(request):
    """手机版价格计算工具（逻辑来自《价格自动计算表2.xlsx》）

    可调参数（税率/加成率）在 stark 后台「价格参数」维护；
    汇率直接读汇率管理表最新美元价。
    """
    rate, rate_date = get_latest_usd_rate()
    if rate is None:
        rate = price_config.EXCHANGE_RATE
        rate_date = None

    # 模板里用字符串键取值
    color_prices_str = {
        'c016': price_config.COLOR_PRICES[0.16],
        'c018': price_config.COLOR_PRICES[0.18],
        'c020': price_config.COLOR_PRICES[0.20],
        'c030': price_config.COLOR_PRICES[0.30],
        'c035': price_config.COLOR_PRICES[0.35],
        'c040': price_config.COLOR_PRICES[0.40],
    }
    context = {
        'exchange_rate': rate,
        'exchange_date': rate_date,
        'steel_base': price_config.STEEL_BASE_03,
        'color_prices': color_prices_str,
        'default_markup': price_config.DEFAULT_MARKUP,
        'markup_reference': price_config.MARKUP_REFERENCE,
        'tax_rate': get_config_value('tax_rate', price_config.FOB_MARGIN),
        'default_markup_rate': get_config_value('markup_rate', price_config.DEFAULT_MARKUP_RATE),
    }
    return render(request, 'dipay/price_calc.html', context)
