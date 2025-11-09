"""
天气查询工具

使用和风天气API查询实时天气和天气预报
API文档: https://dev.qweather.com/docs/api/
"""
import os
import logging
from typing import Dict, Any
import aiohttp
from datetime import datetime
from tool_manager import Tool, ToolParameter

logger = logging.getLogger(__name__)


class WeatherTool(Tool):
    """天气查询工具"""

    def __init__(self):
        super().__init__()
        self.name = "weather"
        self.description = "查询指定城市的实时天气和天气预报"
        self.category = "weather"

        # 从环境变量获取API密钥
        self.api_key = os.getenv('QWEATHER_API_KEY', '')
        if not self.api_key:
            logger.warning("⚠️ 未配置和风天气API密钥 (QWEATHER_API_KEY)")
            self.enabled = False

        # 定义参数
        self.parameters = [
            ToolParameter(
                name="city",
                param_type="string",
                description="城市名称，如：北京、上海、广州",
                required=True
            ),
            ToolParameter(
                name="query_type",
                param_type="string",
                description="查询类型：now(实时天气)、3d(3天预报)、7d(7天预报)",
                required=False,
                default="now",
                enum=["now", "3d", "7d"]
            )
        ]

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """执行天气查询"""
        city = kwargs.get('city')
        query_type = kwargs.get('query_type', 'now')

        try:
            # 第一步：获取城市Location ID
            location_id = await self._get_location_id(city)
            if not location_id:
                return {
                    'success': False,
                    'error': f"未找到城市 '{city}'",
                    'result': None
                }

            # 第二步：根据查询类型获取天气数据
            if query_type == "now":
                weather_data = await self._get_realtime_weather(location_id)
            else:
                days = 3 if query_type == "3d" else 7
                weather_data = await self._get_forecast_weather(
                    location_id, days
                )

            if not weather_data:
                return {
                    'success': False,
                    'error': "获取天气数据失败",
                    'result': None
                }

            # 格式化返回结果
            result = self._format_weather_result(
                city, query_type, weather_data
            )

            return {
                'success': True,
                'result': result,
                'error': None,
                'metadata': {
                    'location_id': location_id,
                    'query_type': query_type,
                    'timestamp': datetime.now().isoformat()
                }
            }

        except Exception as e:
            logger.error(f"天气查询异常: {e}", exc_info=True)
            return {
                'success': False,
                'error': f"查询异常: {str(e)}",
                'result': None
            }

    async def _get_location_id(self, city: str) -> str:
        """获取城市Location ID"""
        url = "https://geoapi.qweather.com/v2/city/lookup"
        params = {
            'location': city,
            'key': self.api_key,
            'lang': 'zh'
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    data = await response.json()

                    if data.get('code') == '200' and data.get('location'):
                        # 返回第一个匹配的城市ID
                        return data['location'][0]['id']

                    logger.warning(f"城市查询失败: {city}, 响应: {data}")
                    return None

        except Exception as e:
            logger.error(f"获取城市ID异常: {e}", exc_info=True)
            return None

    async def _get_realtime_weather(self, location_id: str) -> Dict:
        """获取实时天气"""
        url = "https://devapi.qweather.com/v7/weather/now"
        params = {
            'location': location_id,
            'key': self.api_key,
            'lang': 'zh'
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    data = await response.json()

                    if data.get('code') == '200':
                        return data.get('now', {})

                    logger.warning(f"实时天气查询失败, 响应: {data}")
                    return None

        except Exception as e:
            logger.error(f"获取实时天气异常: {e}", exc_info=True)
            return None

    async def _get_forecast_weather(
        self, location_id: str, days: int
    ) -> Dict:
        """获取天气预报"""
        # 和风天气API: 3天预报和7天预报使用不同endpoint
        endpoint = "3d" if days == 3 else "7d"
        url = f"https://devapi.qweather.com/v7/weather/{endpoint}"
        params = {
            'location': location_id,
            'key': self.api_key,
            'lang': 'zh'
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    data = await response.json()

                    if data.get('code') == '200':
                        return data.get('daily', [])

                    logger.warning(f"天气预报查询失败, 响应: {data}")
                    return None

        except Exception as e:
            logger.error(f"获取天气预报异常: {e}", exc_info=True)
            return None

    def _format_weather_result(
        self, city: str, query_type: str, weather_data: Any
    ) -> str:
        """格式化天气结果为易读文本"""
        if query_type == "now":
            # 实时天气格式化
            return self._format_realtime(city, weather_data)
        else:
            # 预报格式化
            days = 3 if query_type == "3d" else 7
            return self._format_forecast(city, weather_data, days)

    def _format_realtime(self, city: str, data: Dict) -> str:
        """格式化实时天气"""
        text = data.get('text', '未知')
        temp = data.get('temp', '--')
        feels_like = data.get('feelsLike', '--')
        humidity = data.get('humidity', '--')
        wind_dir = data.get('windDir', '未知')
        wind_scale = data.get('windScale', '--')

        result = f"📍 {city} 实时天气\n\n"
        result += f"🌡️ 温度: {temp}°C (体感 {feels_like}°C)\n"
        result += f"☁️ 天气: {text}\n"
        result += f"💧 湿度: {humidity}%\n"
        result += f"🌬️ 风向风力: {wind_dir} {wind_scale}级\n"

        update_time = data.get('obsTime', '')
        if update_time:
            result += f"\n更新时间: {update_time}"

        return result

    def _format_forecast(
        self, city: str, data: list, days: int
    ) -> str:
        """格式化天气预报"""
        result = f"📍 {city} {days}天天气预报\n\n"

        for i, day in enumerate(data[:days], 1):
            date = day.get('fxDate', '')
            text_day = day.get('textDay', '未知')
            text_night = day.get('textNight', '未知')
            temp_max = day.get('tempMax', '--')
            temp_min = day.get('tempMin', '--')

            # 解析日期显示
            date_str = ""
            if date:
                try:
                    dt = datetime.fromisoformat(date)
                    weekdays = ['一', '二', '三', '四', '五', '六', '日']
                    weekday = weekdays[dt.weekday()]
                    date_str = f"{dt.month}月{dt.day}日 周{weekday}"
                except Exception:
                    date_str = date

            result += f"第{i}天 ({date_str})\n"
            result += f"  🌡️ 温度: {temp_min}°C ~ {temp_max}°C\n"
            result += f"  ☀️ 白天: {text_day}\n"
            result += f"  🌙 夜间: {text_night}\n\n"

        return result.strip()


# 创建工具实例
weather_tool = WeatherTool()
