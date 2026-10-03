# -*- coding: utf-8 -*-
"""cn-life 12306 查询核心 — 纯 HTTP 无需登录。
先访问 init 页拿 cookie（JSESSIONID/BIGipServerotn），再查 query 接口。
字段解析参考社区公开整理（Joooook/12306-mcp, MIT）。
"""
import http.cookiejar
import json
import re
import time
import urllib.request
import urllib.parse

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")

STATION_URL = "https://kyfw.12306.cn/otn/resources/js/framework/station_name.js"
INIT_URL = "https://kyfw.12306.cn/otn/leftTicket/init"
QUERY_BASE = "https://kyfw.12306.cn/otn/leftTicket/query"

_station_cache = None
_opener = None
_opener_ts = 0.0


def _get_opener():
    """带 cookie 的 opener（12306 反爬：无 cookie 的 query 只回 HTML）。"""
    global _opener, _opener_ts
    if _opener is not None and time.time() - _opener_ts < 600:
        return _opener
    cj = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    req = urllib.request.Request(INIT_URL, headers={"User-Agent": UA})
    op.open(req, timeout=15).read()
    _opener = op
    _opener_ts = time.time()
    return _opener


def _get(url, retry=2, use_opener=False):
    last = None
    for i in range(retry + 1):
        try:
            if use_opener:
                req = urllib.request.Request(url, headers={
                    "User-Agent": UA,
                    "Referer": "https://kyfw.12306.cn/otn/leftTicket/init"})
                with _get_opener().open(req, timeout=15) as r:
                    return r.read().decode("utf-8", errors="replace")
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=15) as r:
                return r.read().decode("utf-8", errors="replace")
        except Exception as e:
            last = e
            time.sleep(1.2)
    raise last


def _load_stations():
    global _station_cache
    if _station_cache is not None:
        return _station_cache
    js = _get(STATION_URL)
    cache = {}
    cn_by_code = {}
    for m in re.finditer(r"@([^|]+)\|([^|]+)\|([A-Z]+)\|([^|]+)\|([^|]+)", js):
        abbr1, cn, code, pinyin, abbr2 = (m.group(1), m.group(2), m.group(3),
                                          m.group(4), m.group(5))
        cache[cn] = code
        cache[pinyin.lower()] = code
        cache[abbr1.lower()] = code
        cache[abbr2.lower()] = code
        cn_by_code[code] = cn
    _station_cache = (cache, cn_by_code)
    return _station_cache


def resolve_station(name):
    """中文/拼音/缩写/中文片段 → (电报码, 正式中文名)。"""
    cache, cn_by_code = _load_stations()
    key = name.strip()
    if key in cache:
        return cache[key], cn_by_code.get(cache[key], key)
    kl = key.lower()
    if kl in cache:
        return cache[kl], cn_by_code.get(cache[kl], key)
    # 中文包含匹配 & 拼音前缀
    cands = [k for k in cache if not k.isascii() and key in k]
    if not cands and len(kl) >= 3:
        cands = [k for k in cache if k.isascii() and k.startswith(kl)]
    if cands:
        cands.sort(key=lambda k: len(cn_by_code.get(cache[k], k)))
        code = cache[cands[0]]
        return code, cn_by_code.get(code, cands[0])
    return None, None


def query_tickets(from_cn, to_cn, date, only_gaotie=False):
    fcode, fname = resolve_station(from_cn)
    tcode, tname = resolve_station(to_cn)
    if not fcode:
        return {"ok": False, "error": f"出发站无法识别: {from_cn}"}
    if not tcode:
        return {"ok": False, "error": f"到达站无法识别: {to_cn}"}

    qs = urllib.parse.urlencode({
        "leftTicketDTO.train_date": date,
        "leftTicketDTO.from_station": fcode,
        "leftTicketDTO.to_station": tcode,
        "purpose_codes": "ADULT",
    })
    raw = None
    global _opener, _opener_ts
    for suffix in ("G", "U", "", "A", "Z", "B"):
        try:
            r = _get(f"{QUERY_BASE}{suffix}?{qs}", retry=0, use_opener=True)
            if "result" in r:
                raw = r
                break
        except Exception:
            pass
        time.sleep(0.5)
    if raw is None:
        _opener = None
        _opener_ts = 0.0
        try:
            r = _get(f"{QUERY_BASE}G?{qs}", retry=1, use_opener=True)
            if "result" in r:
                raw = r
        except Exception:
            pass
    if raw is None:
        return {"ok": False, "error": "12306 未返回数据（接口可能变动或被限流），稍后再试"}

    body = json.loads(raw)
    trains = []
    # 站名简写→全名映射（p[4]/p[5] 是简写码，用站库反查）
    cache, cn_by_code = _load_stations()
    for row in body.get("data", {}).get("result", []):
        p = row.split("|")
        code = p[3]
        if only_gaotie and code[0] not in "GD":
            continue
        seats = {}
        for label, idx in (("商务座", 32), ("一等座", 31), ("二等座", 30),
                           ("高级软卧", 21), ("软卧", 23), ("动卧", 33),
                           ("硬卧", 28), ("软座", 24), ("硬座", 29), ("无座", 26)):
            v = p[idx] if idx < len(p) else ""
            if v and v not in ("-", "", "无"):
                seats[label] = v
        trains.append({
            "车次": code, "发车": p[8], "到达": p[9], "历时": p[10],
            "出发站": cn_by_code.get(p[6], p[6]), "到达站": cn_by_code.get(p[7], p[7]),
            "可订": p[11] == "Y", "余票": seats,
        })
    trains.sort(key=lambda t: t["发车"])
    return {"ok": True, "from": fname, "to": tname, "date": date,
            "count": len(trains), "trains": trains[:60]}
