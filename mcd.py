# -*- coding: utf-8 -*-
"""cn-life 麦当劳模块 — 官方 MCP (mcp.mcd.cn) 的 Streamable HTTP 客户端。
用户去 open.mcd.cn/mcp 手机号登录领 Token 填进 MCD_MCP_TOKEN。
流程: initialize → initialized → tools/call (JSON-RPC over HTTP POST)。
支付红线: create-order 返回支付链接后停下, 人扫码。"""
import json
import time
import urllib.request

URL = "https://mcp.mcd.cn"
PROTO = "2025-06-18"


def _key(token):
    if not token:
        return {"ok": False, "error": "未配置麦当劳Token：手机登录 open.mcd.cn/mcp → 控制台激活 → 复制Token → 设 MCD_MCP_TOKEN 环境变量"}
    return None


def _post(token, payload, timeout=30):
    req = urllib.request.Request(
        URL, data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json",
                 "Accept": "application/json, text/event-stream",
                 "Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read().decode("utf-8", errors="replace")
    # SSE 格式: data: {...}
    for line in raw.splitlines():
        if line.startswith("data:"):
            try:
                return json.loads(line[5:].strip())
            except json.JSONDecodeError:
                continue
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw[:500]}


def _call(token, tool, args, timeout=40):
    # 每次独立会话: init → initialized → call (Streamable HTTP 允许无状态模式)
    init = _post(token, {
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": PROTO, "capabilities": {},
                   "clientInfo": {"name": "hermes-cn-life", "version": "0.2"}}})
    if "error" in init:
        return {"ok": False, "error": f"init失败: {init['error'].get('message', init['error'])}"}
    _post(token, {"jsonrpc": "2.0", "method": "notifications/initialized"})
    r = _post(token, {
        "jsonrpc": "2.0", "id": 2, "method": "tools/call",
        "params": {"name": tool, "arguments": args}}, timeout=timeout)
    if "error" in r:
        return {"ok": False, "error": r["error"].get("message", str(r["error"]))}
    content = (r.get("result") or {}).get("content", [])
    for c in content:
        if c.get("type") == "text":
            try:
                return {"ok": True, "data": json.loads(c["text"])}
            except (json.JSONDecodeError, TypeError):
                return {"ok": True, "data": c["text"][:2000]}
    return {"ok": True, "data": r.get("result")}


def nearby_stores(token, city, keyword=None, search_type=1):
    """searchType: 1=外送 2=到店"""
    e = _key(token)
    if e:
        return e
    args = {"city": city, "searchType": search_type}
    if keyword:
        args["keyword"] = keyword
    return _call(token, "query-nearby-stores", args)


def meals(token, store_id):
    return _call(token, "query-meals", {"storeId": store_id})


def coupons_mine(token):
    return _call(token, "query-my-coupons", {})


def coupons_auto_claim(token):
    return _call(token, "auto-bind-coupons", {})


def create_order(token, order_payload):
    """官方 create-order: 返回订单+支付链接。支付链接发给用户, 人扫码 — 插件永不代付。"""
    return _call(token, "create-order", order_payload)


def tools_list(token):
    """诊断: 列出服务端全部工具"""
    e = _key(token)
    if e:
        return e
    init = _post(token, {"jsonrpc": "2.0", "id": 1, "method": "initialize",
                         "params": {"protocolVersion": PROTO, "capabilities": {},
                                    "clientInfo": {"name": "hermes-cn-life", "version": "0.2"}}})
    _post(token, {"jsonrpc": "2.0", "method": "notifications/initialized"})
    r = _post(token, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
    return r
