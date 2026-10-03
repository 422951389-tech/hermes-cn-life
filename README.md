# cn-life — 中国生活服务插件 for Hermes Agent

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

让 Hermes Agent 接入中国互联网生活服务：**火车票查询、快递物流、地图/POI/路线/天气、麦当劳官方点餐**。
人在外面发条消息（QQ/Telegram/微信/任何 Hermes 支持的 20+ 平台），家里的 Agent 帮你查。

## 设计原则

1. **平台无关** — 工具返回纯 JSON，不绑定任何聊天平台，QQ/Telegram/微信通用
2. **永不碰钱** — 插件只做查询和规划；任何交易只推进到「给用户链接/二维码，用户手机扫码支付」
3. **渐进配置** — 12306 零配置开箱即用；高德填个免费 key 解锁；不填也不影响别的模块

## 安装

```bash
# 方式一: 目录安装 (当前)
git clone https://github.com/422951389-tech/hermes-cn-life ~/.hermes/plugins/cn-life
hermes plugins enable cn-life

# 方式二: 待发布到目录后
hermes plugins install 422951389-tech/hermes-cn-life
```

## 模块

| 工具 | 功能 | 依赖 |
|---|---|---|
| `cn_train_query` | 12306 余票/车次/座位/票价（支持按发车时间/历时最短排序） | 无（纯HTTP+cookie） |
| `cn_train_station` | 站名模糊解析（中文/拼音/缩写） | 无 |
| `cn_express_track` | 快递物流查询（自动识别公司+轨迹，支持批量≤10单） | 无（快递100免key公开接口） |
| `cn_mcd_stores` | 麦当劳门店查询 | MCD_MCP_TOKEN |
| `cn_mcd_coupons` | 麦当劳优惠券（查/一键领） | MCD_MCP_TOKEN |
| `cn_mcd_tools` | 麦当劳全工具透传（点餐/积分/订单） | MCD_MCP_TOKEN |
| `cn_amap_poi` | POI 搜索（找店/景点/停车场） | AMAP_KEY |
| `cn_amap_route` | 驾车/步行/公交/骑行路线 | AMAP_KEY |
| `cn_amap_weather` | 城市天气预报 | AMAP_KEY |

### 高德 key（免费）

到 [console.amap.com](https://console.amap.com) 注册 → 创建应用 → 添加 Key（服务类型选 **Web服务**）：
```bash
export AMAP_KEY="你的key"   # 或写进 plugins.entries.cn-life.settings.amap_key
```

## 使用示例

> 帮我查下周六北京南到上海虹桥的高铁，下午出发的
> 附近有什么好吃的川菜馆？（配城市/位置）
> 明天杭州天气怎么样，适合骑行吗？

## Roadmap

- [x] v0.2 麦当劳官方 MCP（门店/优惠券/全工具透传，`MCD_MCP_TOKEN`）
- [ ] v0.2 电影档期（猫眼/淘票票页面解析）
- [ ] v0.2 机票查询（飞常准/航旅纵横接口）
- [ ] v0.3 余票监控 cron（放票提醒推送到聊天平台）
- [ ] v0.4 外卖/购物比价（浏览器自动化，只到购物车，支付留给人）

## 生态地图（哪些服务接得上，2026-10 调研）

| 服务 | 通道 | 状态 |
|---|---|---|
| 12306 火车票 | 官方网页接口 | ✅ 本插件实现 |
| 高德地图 | 官方 MCP / REST | ✅ 本插件实现 |
| **麦当劳** | **官方 MCP** (mcp.mcd.cn) | ✅ 本插件实现（点餐/积分/券全套） |
| 滴滴打车 | 官方远程 MCP | 可直连（mcp.didialift.com） |
| 星巴克中国 | 社区 MCP | 可包一层 |
| 飞常准航班 | 社区 MCP | 可包一层 |
| 淘宝/京东/拼多多 | ❌ 无官方API | 仅浏览器自动化 |
| 美团/饿了么外卖 | ❌ API白名单制 | 仅手机机械臂（meituan-cli 路线） |
| 电影票（猫眼/淘票票） | ❌ 无公开API | 仅页面解析 |

## 致谢

- 12306 接口字段整理参考 [Joooook/12306-mcp](https://github.com/Joooook/12306-mcp) (MIT)
- 高德开放平台官方 API

## License

MIT
