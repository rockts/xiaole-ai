"""
百度语音识别工具
支持语音识别（ASR）和语音合成（TTS）
"""
import os
from aip import AipSpeech
from typing import Optional


class BaiduVoiceTool:
    """百度语音识别工具类"""
    
    def __init__(self):
        """初始化百度语音客户端"""
        # 从环境变量读取配置
        self.app_id = os.getenv('BAIDU_APP_ID', '')
        self.api_key = os.getenv('BAIDU_API_KEY', '')
        self.secret_key = os.getenv('BAIDU_SECRET_KEY', '')
        
        self.client = None
        if self.app_id and self.api_key and self.secret_key:
            self.client = AipSpeech(self.app_id, self.api_key, self.secret_key)
            print("✅ 百度语音服务初始化成功")
        else:
            print("⚠️  百度语音服务未配置，请设置环境变量：")
            print("   BAIDU_APP_ID, BAIDU_API_KEY, BAIDU_SECRET_KEY")
    
    def is_enabled(self) -> bool:
        """检查服务是否可用"""
        return self.client is not None
    
    async def recognize(self, audio_data: bytes, format: str = 'wav', rate: int = 16000) -> dict:
        """
        语音识别（ASR）
        
        Args:
            audio_data: 音频二进制数据
            format: 音频格式（wav/pcm/amr/m4a）
            rate: 采样率（8000/16000）
            
        Returns:
            {"success": True/False, "text": "识别结果", "error": "错误信息"}
        """
        if not self.is_enabled():
            return {
                "success": False,
                "error": "百度语音服务未配置"
            }
        
        try:
            # 调用百度语音识别
            result = self.client.asr(audio_data, format, rate, {
                'dev_pid': 1537,  # 1537=普通话(支持简单的英文识别)
                'cuid': 'xiaole-ai',
            })
            
            if result.get('err_no') == 0:
                # 识别成功
                text = ''.join(result.get('result', []))
                return {
                    "success": True,
                    "text": text
                }
            else:
                # 识别失败
                error_msg = result.get('err_msg', '未知错误')
                return {
                    "success": False,
                    "error": f"识别失败: {error_msg}"
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"识别异常: {str(e)}"
            }
    
    async def synthesize(self, text: str, person: int = 0, speed: int = 5, pitch: int = 5, volume: int = 5) -> Optional[bytes]:
        """
        语音合成（TTS）
        
        Args:
            text: 要合成的文本
            person: 发音人选择（0=度小美女声, 1=度小宇男声, 3=度逍遥男声, 4=度丫丫女声）
            speed: 语速（0-15，默认5）
            pitch: 音调（0-15，默认5）
            volume: 音量（0-15，默认5）
            
        Returns:
            音频二进制数据，失败返回None
        """
        if not self.is_enabled():
            print("⚠️  百度语音服务未配置")
            return None
        
        try:
            result = self.client.synthesis(text, 'zh', 1, {
                'spd': speed,
                'pit': pitch,
                'vol': volume,
                'per': person,
            })
            
            # 如果返回字典则是错误
            if isinstance(result, dict):
                error_msg = result.get('err_msg', '未知错误')
                print(f"❌ 语音合成失败: {error_msg}")
                return None
            
            # 返回的是音频数据
            return result
        
        except Exception as e:
            print(f"❌ 语音合成异常: {str(e)}")
            return None

# 创建全局实例
baidu_voice_tool = BaiduVoiceTool()
