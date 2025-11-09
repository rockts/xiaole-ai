"""
天气查询工具

使用Open-Meteo API查询实时天气和天气预报
API文档: https://open-meteo.com/en/docs
优点: 完全免费，无需API key，数据来自气象部门
"""
import logging
from typing import Dict, Any, Optional, Tuple
import aiohttp
from datetime import datetime, timedelta
from tool_manager import Tool, ToolParameter

logger = logging.getLogger(__name__)


class WeatherTool(Tool):
    """天气查询工具 - 使用Open-Meteo API"""

    # 中国主要城市坐标映射
    CITY_COORDS = {
        '北京': (39.9042, 116.4074),
        '上海': (31.2304, 121.4737),
        '广州': (23.1291, 113.2644),
        '深圳': (22.5431, 114.0579),
        '成都': (30.5728, 104.0668),
        '杭州': (30.2741, 120.1551),
        '重庆': (29.5630, 106.5516),
        '西安': (34.2658, 108.9541),
        '苏州': (31.2989, 120.5853),
        '武汉': (30.5928, 114.3055),
        '南京': (32.0603, 118.7969),
        '天津': (39.3434, 117.3616),
        '郑州': (34.7466, 113.6253),
        '长沙': (28.2282, 112.9388),
        '沈阳': (41.8057, 123.4315),
        '青岛': (36.0671, 120.3826),
        '济南': (36.6512, 117.1209),
        '哈尔滨': (45.8038, 126.5340),
        '福州': (26.0745, 119.2965),
        '厦门': (24.4798, 118.0894),
        '昆明': (25.0406, 102.7099),
        '兰州': (36.0611, 103.8343),
        '太原': (37.8706, 112.5489),
        '石家庄': (38.0428, 114.5149),
        '南昌': (28.6829, 115.8579),
        '贵阳': (26.6470, 106.6302),
        '南宁': (22.8170, 108.3665),
        '合肥': (31.8206, 117.2272),
        '乌鲁木齐': (43.8256, 87.6168),
        '大连': (38.9140, 121.6147),
        '天水': (34.5809, 105.7249),
        '秦州': (34.5809, 105.7249),
    }

    def __init__(self):
        super().__init__()
        self.name = "weather"
        self.description = "查询指定城市的实时天气和天气预报（使用Open-Meteo免费API）"
        self.category = "weather"
        self.enabled = True  # Open-Meteo无需API key，始终可用

        # 定义参数
        self.parameters = [
            ToolParameter(
                name="city",
                param_type="string",
                description="城市名称，如：北京、上海、天水",
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

        if not city:
            return {
                'success': False,
                'error': "缺少必需参数: city",
                'result': None
            }

        try:
            logger.info(f"查询天气: 城市={city}, 类型={query_type}")

            # 获取城市坐标
            coords = self._get_city_coords(city)
            if not coords:
                return {
                    'success': False,
                    'error': f"不支持的城市: {city}。支持的城市请参考帮助。",
                    'result': None
                }

            lat, lon = coords
            logger.info(f"城市坐标: {city} -> ({lat}, {lon})")

            # 根据查询类型获取天气数据
            if query_type == 'now':
                weather_data = await self._get_current_weather(lat, lon)
            else:
                days = 7 if query_type == '7d' else 3
                weather_data = await self._get_forecast_weather(
                    lat, lon, days
                )

            if not weather_data:
                return {
                    'success': False,
                    'error': "获取天气数据失败",
                    'result': None
                }

            # 格式化结果
            result = self._format_weather_result(
                city, query_type, weather_data
            )

            return {
                'success': True,
                'result': result,
                'error': None,
                'metadata': {
                    'city': city,
                    'coordinates': {'lat': lat, 'lon': lon},
                    'query_type': query_type,
                    'source': 'Open-Meteo',
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

    def _get_city_coords(self, city: str) -> Optional[Tuple[float, float]]:
        """获取城市坐标"""
        # 移除常见后缀
        city_name = city.replace('市', '').replace('区', '').strip()
        
        # 精确匹配
        if city_name in self.CITY_COORDS:
            return self.CITY_COORDS[city_name]
        
        # 模糊匹配
        for key, coords in self.CITY_COORDS.items():
            if city_name in key or key in city_name:
                logger.info(f"模糊匹配: {city} -> {key}")
                return coords
        
        return None

    async def _get_current_weather(
        self, lat: float, lon: float
    ) -> Optional[Dict]:
        """获取实时天气"""
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            'latitude': lat,
            'longitude': lon,
            'current': [
                'temperature_2m',
                'relative_humidity_2m',
                'apparent_temperature',
                'precipitation',
                'weather_code',
                'wind_speed_10m',
                'wind_direction_10m'
            ],
            'timezone': 'Asia/Shanghai'
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('current', {})
                    else:
                        logger.error(
                            f"Open-Meteo API错误: {response.status}"
                        )
                        return None

        except Exception as e:
            logger.error(f"获取实时天气异常: {e}", exc_info=True)
            return None

    async def _get_forecast_weather(
        self, lat: float, lon: float, days: int
    ) -> Optional[Dict]:
        """获取天气预报"""
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            'latitude': lat,
            'longitude': lon,
            'daily': [
                'weather_code',
                'temperature_2m_max',
                'temperature_2m_min',
                'precipitation_sum',
                'precipitation_probability_max',
                'wind_speed_10m_max'
            ],
            'timezone': 'Asia/Shanghai',
            'forecast_days': days
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('daily', {})
                    else:
                        logger.error(
                            f"Open-Meteo API错误: {response.status}"
                        )
                        return None

        except Exception as e:
            logger.error(f"获取天气预报异常: {e}", exc_info=True)
            return None

    def _format_weather_result(
        self, city: str, query_type: str, weather_data: Dict
    ) -> str:
        """格式化天气结果为易读文本"""
        if query_type == 'now':
            return self._format_current_weather(city, weather_data)
        else:
            return self._format_forecast_weather(city, weather_data)

    def _format_current_weather(
        self, city: str, data: Dict
    ) -> str:
        """格式化实时天气"""
        temp = data.get('temperature_2m', 'N/A')
        feels_like = data.get('apparent_temperature', 'N/A')
        humidity = data.get('relative_humidity_2m', 'N/A')
        wind_speed = data.get('wind_speed_10m', 'N/A')
        weather_code = data.get('weather_code', 0)
        weather_desc = self._get_weather_description(weather_code)

        return (
            f"{city}当前天气：{weather_desc}，"
            f"温度{temp}°C，体感{feels_like}°C，"
            f"湿度{humidity}%，风速{wind_speed}km/h"
        )

    def _format_forecast_weather(
        self, city: str, data: Dict
    ) -> str:
        """格式化天气预报"""
        dates = data.get('time', [])
        temp_max = data.get('temperature_2m_max', [])
        temp_min = data.get('temperature_2m_min', [])
        weather_codes = data.get('weather_code', [])
        precip_prob = data.get('precipitation_probability_max', [])

        lines = [f"{city}未来{len(dates)}天天气预报："]
        
        for i in range(len(dates)):
            date_obj = datetime.fromisoformat(dates[i])
            day_name = self._get_day_name(i, date_obj)
            
            weather_desc = self._get_weather_description(
                weather_codes[i] if i < len(weather_codes) else 0
            )
            t_max = temp_max[i] if i < len(temp_max) else 'N/A'
            t_min = temp_min[i] if i < len(temp_min) else 'N/A'
            rain_prob = precip_prob[i] if i < len(precip_prob) else 0
            
            rain_text = ""
            if rain_prob > 50:
                rain_text = f"，降水概率{rain_prob}%"
            
            lines.append(
                f"  {day_name}：{weather_desc}，"
                f"{t_min}~{t_max}°C{rain_text}"
            )
        
        return '\n'.join(lines)

    def _get_day_name(self, index: int, date_obj: datetime) -> str:
        """获取日期名称"""
        if index == 0:
            return "今天"
        elif index == 1:
            return "明天"
        elif index == 2:
            return "后天"
        else:
            return date_obj.strftime('%m月%d日')

    def _get_weather_description(self, code: int) -> str:
        """根据WMO天气代码获取描述"""
        weather_codes = {
            0: '晴',
            1: '晴',
            2: '多云',
            3: '阴',
            45: '雾',
            48: '雾',
            51: '小雨',
            53: '小雨',
            55: '中雨',
            56: '冻雨',
            57: '冻雨',
            61: '小雨',
            63: '中雨',
            65: '大雨',
            66: '冻雨',
            67: '冻雨',
            71: '小雪',
            73: '中雪',
            75: '大雪',
            77: '雪',
            80: '阵雨',
            81: '阵雨',
            82: '大阵雨',
            85: '阵雪',
            86: '阵雪',
            95: '雷暴',
            96: '雷暴伴冰雹',
            99: '雷暴伴冰雹',
        }
        return weather_codes.get(code, '未知')

    def _get_mock_weather_data(self, city: str, query_type: str) -> Dict[str, Any]:
        """获取模拟天气数据（临时方案，用于测试工具调用流程）"""
        logger.info(f"🔧 使用模拟天气数据测试: {city}, {query_type}")
        
        from datetime import timedelta
        
        if query_type == 'now':
            # 模拟实时天气
            result_text = f"{city}当前天气：多云，15°C，体感13°C，东北风3级，湿度65%"
            return {
                'success': True,
                'result': result_text,
                'error': None,
                'metadata': {
                    'city': city,
                    'query_type': query_type,
                    'is_mock': True,
                    'note': '⚠️ 这是模拟数据，请配置正确的和风天气API key',
                    'timestamp': datetime.now().isoformat()
                }
            }
        else:
            # 模拟天气预报
            days = 3 if query_type == '3d' else 7
            forecast_lines = [f"{city}未来{days}天天气预报："]
            
            for i in range(days):
                date = (datetime.now().date() + timedelta(days=i)).strftime('%m月%d日')
                day_name = '今天' if i == 0 else ('明天' if i == 1 else ('后天' if i == 2 else date))
                temp_max = 18 + i
                temp_min = 8 + i
                weather_text = '晴' if i % 2 == 0 else '多云'
                rain_text = '，有小雨，降水概率60%' if i == 1 else ''
                
                forecast_lines.append(
                    f"  {day_name}：{weather_text}，{temp_min}~{temp_max}°C{rain_text}"
                )
            
            result_text = '\n'.join(forecast_lines)
            
            return {
                'success': True,
                'result': result_text,
                'error': None,
                'metadata': {
                    'city': city,
                    'query_type': query_type,
                    'is_mock': True,
                    'note': '⚠️ 这是模拟数据，请配置正确的和风天气API key',
                    'timestamp': datetime.now().isoformat()
                }
            }

    async def _get_location_id(self, city: str) -> str:
        """获取城市Location ID"""
        url = "https://devapi.qweather.com/v7/city/lookup"
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
