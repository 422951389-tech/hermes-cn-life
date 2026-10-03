# -*- coding: utf-8 -*-
"""cn-life — 中国生活服务插件 (12306 + 高德)
平台无关设计：工具返回纯 JSON 文本，任何 gateway 平台 (QQ/Telegram/微信/...)
都能用；不持有支付能力，交易环节永远回到用户手机。"""
import logging

from . import schemas, tools

logger = logging.getLogger(__name__)


def register(ctx):
    """注册工具。高德工具在无 key 时仍注册但返回引导错误（渐进式配置）。"""
    ctx.register_tool(name="cn_train_query", toolset="cnlife",
                      schema=schemas.TRAIN_QUERY, handler=tools.cn_train_query)
    ctx.register_tool(name="cn_train_station", toolset="cnlife",
                      schema=schemas.TRAIN_STATION, handler=tools.cn_train_station)
    ctx.register_tool(name="cn_amap_poi", toolset="cnlife",
                      schema=schemas.AMAP_POI, handler=tools.cn_amap_poi)
    ctx.register_tool(name="cn_amap_route", toolset="cnlife",
                      schema=schemas.AMAP_ROUTE, handler=tools.cn_amap_route)
    ctx.register_tool(name="cn_amap_weather", toolset="cnlife",
                      schema=schemas.AMAP_WEATHER, handler=tools.cn_amap_weather)
    logger.info("cn-life registered: 2 rail tools + 3 amap tools")
