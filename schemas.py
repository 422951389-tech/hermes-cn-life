# -*- coding: utf-8 -*-
"""cn-life schemas — LLM 看到的工具说明书"""

TRAIN_QUERY = {
    "name": "cn_train_query",
    "description": (
        "查询 12306 火车票余票：给定出发站/到达站/日期，返回所有车次的"
        "余票、票价、发到时间、历时。支持中转方案查询。"
        "用于用户问'某日从A到B的火车票''还有票吗''高铁多少钱'等场景。"
        "日期格式 YYYY-MM-DD。"
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "from": {"type": "string", "description": "出发站中文名，如 '北京南'"},
            "to": {"type": "string", "description": "到达站中文名，如 '上海虹桥'"},
            "date": {"type": "string", "description": "乘车日期 YYYY-MM-DD"},
            "only_gaotie": {"type": "boolean", "description": "只看高铁/动车 (G/D字头)，默认 false"},
            "transfer": {"type": "boolean", "description": "查询一次中转方案（慢，默认 false）"},
        },
        "required": ["from", "to", "date"],
    },
}

TRAIN_STATION = {
    "name": "cn_train_station",
    "description": "12306 车站名模糊搜索/校验：把用户口语化站名转成正式站名（如'北京南'确认存在，'虹桥'→'上海虹桥'）。查票前先校验。",
    "parameters": {
        "type": "object",
        "properties": {
            "keyword": {"type": "string", "description": "站名片段，中文或拼音"},
        },
        "required": ["keyword"],
    },
}

AMAP_POI = {
    "name": "cn_amap_poi",
    "description": "高德 POI 搜索：找地点/商家/景点（'附近的麦当劳''西湖停车场'）。返回名称+地址+坐标+距离。",
    "parameters": {
        "type": "object",
        "properties": {
            "keywords": {"type": "string", "description": "搜索词"},
            "city": {"type": "string", "description": "城市名（adcode也行），提高准确度"},
            "location": {"type": "string", "description": "可选，'经度,纬度' 基点（搜周边时用）"},
            "radius": {"type": "integer", "description": "周边搜索半径米数（配合 location）"},
        },
        "required": ["keywords"],
    },
}

AMAP_ROUTE = {
    "name": "cn_amap_route",
    "description": "高德路线规划：驾车/步行/公交/骑行，返回距离、耗时、方案摘要。",
    "parameters": {
        "type": "object",
        "properties": {
            "origin": {"type": "string", "description": "起点 '经度,纬度' 或 '地址文本'（文本会自动地理编码）"},
            "destination": {"type": "string", "description": "终点，同上"},
            "mode": {"type": "string", "description": "driving/walking/transit/bicycling 之一，默认 driving"},
            "city": {"type": "string", "description": "公交模式需要的城市"},
        },
        "required": ["origin", "destination"],
    },
}

AMAP_WEATHER = {
    "name": "cn_amap_weather",
    "description": "高德天气查询：指定城市的实况+未来3天预报。",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "城市名或 adcode"},
        },
        "required": ["city"],
    },
}
