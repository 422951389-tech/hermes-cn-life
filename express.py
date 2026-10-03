# -*- coding: utf-8 -*-
"""cn-life 快递模块 — 快递100 免key公开接口。
流程: autonumber 自动识别快递公司 → query 查轨迹。
免 key 有隐性频率限制（网页端同款），适合个人低频查询。"""


import json
import time
import urllib.request
import urllib.parse

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


def _get(url, retry=1):
    last = None
    for i in range(retry + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=12) as r:
                return json.loads(r.read().decode("utf-8", errors="replace"))
        except Exception as e:
            last = e
            time.sleep(1)
    raise last


COMPANY_FIX = {
    "shunfeng": "顺丰速运", "yto": "圆通速递", "zto": "中通快递",
    "sto": "申通快递", "yunda": "韵达快递", "jd": "京东物流",
    "debangkuaidi": "德邦快递", "ems": "EMS", "youzhengguonei": "邮政包裹",
    "huitongkuaidi": "百世快递", "jijiexpress": "极兔速递", "jtexpress": "极兔速递", "shentong": "申通快递",
    "zhongtong": "中通快递", "yuantong": "圆通速递",
}


def detect_company(num):
    """单号 → 快递公司列表"""
    d = _get(f"https://www.kuaidi100.com/autonumber/autoComNum?text={urllib.parse.quote(num)}")
    autos = d.get("auto", [])
    return [{"code": a.get("comCode"),
             "name": COMPANY_FIX.get(a.get("comCode"), a.get("comCode"))}
            for a in autos[:5]]


def track(num, company=None):
    """查轨迹。company 不给则自动识别（取第一个候选）。"""
    if not company:
        comps = detect_company(num)
        if not comps:
            return {"ok": False, "error": f"识别不了快递公司：{num}（可能单号有误）"}
        company = comps[0]["code"]
        cname = comps[0]["name"]
    else:
        # 用户给的中文名反转
        rev = {v: k for k, v in COMPANY_FIX.items()}
        code = rev.get(company, company)
        company = code
        cname = COMPANY_FIX.get(company, company)

    d = _get(f"https://www.kuaidi100.com/query?type={company}&postid={urllib.parse.quote(num)}")
    if d.get("status") != "200" and not d.get("data"):
        return {"ok": False, "error": f"查询失败: {d.get('message', '未知错误')}（免费接口限频可稍后再试）"}
    trail = [{"时间": t.get("ftime"), "事件": t.get("context")}
             for t in (d.get("data") or [])[:20]]
    if trail and all("查无结果" in (x["事件"] or "") for x in trail):
        return {"ok": False, "error": "接口通了但查无此单（单号错或刚揽收未入网），稍后再试"}
    state_map = {"0": "运输中", "1": "揽收", "2": "疑难", "3": "已签收",
                 "4": "退签", "5": "派送中", "6": "退回", "7": "转投", "8": "清关"}
    return {"ok": True, "单号": num, "快递": cname or company,
            "状态": state_map.get(d.get("state", ""), d.get("state")),
            "轨迹": trail}


def track_many(numbers):
    """批量查（最多 10 单，免key限频，每单间隔 0.8s）。"""
    out = []
    nums = [n.strip() for n in numbers if str(n).strip()][:10]
    for n in nums:
        try:
            r = track(n)
        except Exception as e:
            r = {"ok": False, "error": str(e)}
        # 批量时轨迹只留最新 3 条，省 token
        if r.get("ok") and r.get("轨迹"):
            r["轨迹"] = r["轨迹"][:3]
        out.append({"单号": n, **r})
        time.sleep(0.8)
    ok_n = sum(1 for x in out if x.get("ok"))
    return {"ok": ok_n > 0, "总数": len(nums), "成功": ok_n, "结果": out}
