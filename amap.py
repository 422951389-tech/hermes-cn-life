# -*- coding: utf-8 -*-
"""cn-life 高德模块 — 需要免费 AMAP key"""
import json
import time
import urllib.request
import urllib.parse

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"


def _get(url, retry=2):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    last = None
    for i in range(retry + 1):
        try:
            with urllib.request.urlopen(req, timeout=12) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            last = e
            time.sleep(1)
    raise last


def _key(key):
    if not key:
        return {"ok": False, "error": "未配置高德key：到 https://console.amap.com 免费申请(Web服务)，填入 AMAP_KEY 环境变量"}
    return None


def geocode(address, city, key):
    """地址 → 坐标"""
    qs = urllib.parse.urlencode({"address": address, "city": city or "", "key": key})
    d = _get(f"https://restapi.amap.com/v3/geocode/geo?{qs}")
    if d.get("status") == "1" and d.get("geocodes"):
        return d["geocodes"][0]["location"]
    return None


def poi_search(keywords, city, location, radius, amap_key):
    e = _key(amap_key)
    if e:
        return e
    params = {"keywords": keywords, "key": amap_key, "offset": 8, "page": 1,
              "extensions": "base"}
    if city:
        params["city"] = city
    if location:
        params["location"] = location
        if radius:
            params["radius"] = str(radius)
            params["sortrule"] = "distance"
    qs = urllib.parse.urlencode(params)
    d = _get(f"https://restapi.amap.com/v3/place/text?{qs}")
    if d.get("status") != "1":
        return {"ok": False, "error": f"高德API: {d.get('info')}"}
    pois = []
    for p in d.get("pois", [])[:8]:
        pois.append({
            "名称": p.get("name"),
            "地址": (p.get("pname") or "") + (p.get("cityname") or "") + (p.get("address") or ""),
            "类型": p.get("type"),
            "坐标": p.get("location"),
            "电话": p.get("tel"),
        })
    return {"ok": True, "count": d.get("count"), "results": pois}


def route_plan(origin, destination, mode, city, amap_key):
    e = _key(amap_key)
    if e:
        return e
    # 文本地址先转坐标
    if "," not in origin or not origin.split(",")[0].replace(".", "").isdigit():
        c = geocode(origin, city, amap_key)
        if not c:
            return {"ok": False, "error": f"起点无法解析: {origin}"}
        origin = c
    if "," not in destination or not destination.split(",")[0].replace(".", "").isdigit():
        c = geocode(destination, city, amap_key)
        if not c:
            return {"ok": False, "error": f"终点无法解析: {destination}"}
        destination = c

    base = {"origin": origin, "destination": destination, "key": amap_key}
    if mode == "transit":
        base["city"] = city or "北京"
        url = "https://restapi.amap.com/v3/direction/transit/integrated?"
    elif mode == "walking":
        url = "https://restapi.amap.com/v3/direction/walking?"
    elif mode == "bicycling":
        url = "https://restapi.amap.com/v4/direction/bicycling?"
    else:
        mode = "driving"
        url = "https://restapi.amap.com/v3/direction/driving?"
    qs = urllib.parse.urlencode(base)
    d = _get(url + qs)
    if d.get("status") != "1" and not d.get("data"):
        return {"ok": False, "error": f"高德API: {d.get('info')}"}

    if mode == "driving":
        r = d["route"]
        path = r["paths"][0]
        return {"ok": True, "mode": mode,
                "距离km": round(int(path["distance"]) / 1000, 1),
                "耗时分": round(int(path["duration"]) / 60),
                "方案": path.get("strategy", ""),
                "起点": origin, "终点": destination}
    if mode == "bicycling":
        path = d["data"]["paths"][0]
        return {"ok": True, "mode": mode,
                "距离km": round(int(path["distance"]) / 1000, 1),
                "耗时分": round(int(path["duration"]) / 60)}
    # transit
    t = d.get("route", {}).get("transits", [])
    if not t:
        return {"ok": False, "error": "无公交方案"}
    out = []
    for tr in t[:3]:
        segs = []
        for s in tr.get("segments", [])[:6]:
            w = s.get("walking", {})
            bus = s.get("bus", {})
            if w.get("distance", 0) and int(w["distance"]) > 50:
                segs.append(f"步行{int(w['distance'])}米")
            if bus.get("buslines"):
                bl = bus["buslines"][0]
                segs.append(f"{bl.get('name')} {bl.get('departure_stop',{}).get('name','')}→{bl.get('arrival_stop',{}).get('name','')}")
        out.append({"耗时分": round(int(tr.get("duration", 0)) / 60),
                    "步行米": tr.get("walking_distance"),
                    " segments": segs})
    return {"ok": True, "mode": "transit", "方案": out}


def weather(city, amap_key):
    e = _key(amap_key)
    if e:
        return e
    qs = urllib.parse.urlencode({"city": city, "key": amap_key, "extensions": "all"})
    d = _get(f"https://restapi.amap.com/v3/weather/weatherInfo?{qs}")
    if d.get("status") != "1" or not d.get("forecasts"):
        # 城市名可能要 adcode — 先地理编码拿 adcode
        qs2 = urllib.parse.urlencode({"address": city, "key": amap_key})
        g = _get(f"https://restapi.amap.com/v3/geocode/geo?{qs2}")
        adcode = None
        if g.get("geocodes"):
            adcode = g["geocodes"][0].get("adcode")
        if not adcode:
            return {"ok": False, "error": f"城市无法识别: {city}"}
        qs3 = urllib.parse.urlencode({"city": adcode, "key": amap_key, "extensions": "all"})
        d = _get(f"https://restapi.amap.com/v3/weather/weatherInfo?{qs3}")
    f = d["forecasts"][0]
    casts = []
    for c in f.get("casts", [])[:4]:
        casts.append({"日期": c.get("date"), "白天": c.get("dayweather"),
                      "夜间": c.get("nightweather"),
                      "温度": f"{c.get('nighttemp')}~{c.get('daytemp')}℃",
                      "风向": c.get("daywind")})
    return {"ok": True, "城市": f.get("city"), "预报": casts}
