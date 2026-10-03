# -*- coding: utf-8 -*-
"""cn-life tool handlers — LLM 调用的入口"""
import json
import os

from . import rail
from . import amap as amap_mod


def _key(**kwargs):
    return (kwargs.get("amap_key")
            or os.environ.get("AMAP_KEY")
            or (kwargs.get("plugin_config") or {}).get("amap_key", ""))


def cn_train_query(args: dict, **kwargs) -> str:
    try:
        r = rail.query_tickets(
            args.get("from", ""), args.get("to", ""), args.get("date", ""),
            only_gaotie=bool(args.get("only_gaotie", False)))
        return json.dumps(r, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"ok": False, "error": f"12306查询失败: {e}"}, ensure_ascii=False)


def cn_train_station(args: dict, **kwargs) -> str:
    try:
        code, name = rail.resolve_station(args.get("keyword", ""))
        if code:
            return json.dumps({"ok": True, "station": name, "code": code}, ensure_ascii=False)
        return json.dumps({"ok": False, "error": "未找到该站，试试完整站名"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False)


def cn_amap_poi(args: dict, **kwargs) -> str:
    try:
        k = _key(**kwargs)
        r = amap_mod.poi_search(args.get("keywords", ""), args.get("city", ""),
                                args.get("location"), args.get("radius"), k)
        return json.dumps(r, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"ok": False, "error": f"高德查询失败: {e}"}, ensure_ascii=False)


def cn_amap_route(args: dict, **kwargs) -> str:
    try:
        k = _key(**kwargs)
        r = amap_mod.route_plan(args.get("origin", ""), args.get("destination", ""),
                                args.get("mode", "driving"), args.get("city", ""), k)
        return json.dumps(r, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"ok": False, "error": f"路线规划失败: {e}"}, ensure_ascii=False)


def cn_amap_weather(args: dict, **kwargs) -> str:
    try:
        k = _key(**kwargs)
        r = amap_mod.weather(args.get("city", ""), k)
        return json.dumps(r, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"ok": False, "error": f"天气查询失败: {e}"}, ensure_ascii=False)
