# -*- coding: utf-8 -*-
"""cn-life tool handlers — LLM 调用的入口"""
import json
import os

from . import rail
from . import amap as amap_mod
from . import mcd


def _key(**kwargs):
    return (kwargs.get("amap_key")
            or os.environ.get("AMAP_KEY")
            or (kwargs.get("plugin_config") or {}).get("amap_key", ""))


def _mcd_token(**kwargs):
    return (os.environ.get("MCD_MCP_TOKEN")
            or (kwargs.get("plugin_config") or {}).get("mcd_token", ""))


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


def cn_mcd_stores(args: dict, **kwargs) -> str:
    try:
        t = _mcd_token(**kwargs)
        r = mcd.nearby_stores(t, args.get("city", ""), args.get("keyword"),
                              int(args.get("search_type", 1)))
        return json.dumps(r, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"ok": False, "error": f"麦当劳查询失败: {e}"}, ensure_ascii=False)


def cn_mcd_coupons(args: dict, **kwargs) -> str:
    try:
        t = _mcd_token(**kwargs)
        action = args.get("action", "list")
        r = mcd.coupons_auto_claim(t) if action == "claim" else mcd.coupons_mine(t)
        return json.dumps(r, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"ok": False, "error": f"麦当劳券操作失败: {e}"}, ensure_ascii=False)


def cn_mcd_tools(args: dict, **kwargs) -> str:
    try:
        t = _mcd_token(**kwargs)
        if args.get("call"):
            r = mcd._call(t, args["call"], args.get("args") or {})
        else:
            r = mcd.tools_list(t)
        return json.dumps(r, ensure_ascii=False)[:6000]
    except Exception as e:
        return json.dumps({"ok": False, "error": f"麦当劳MCP调用失败: {e}"}, ensure_ascii=False)
