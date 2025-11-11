#!/usr/bin/env python3
"""
图片识别工具 - v0.6.0 Phase 4

支持图片上传、分析和理解
使用Claude Vision或GPT-4V进行图片识别
"""

import os
import base64
import requests
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class VisionTool:
    """图片识别工具类"""

    def __init__(self):
        """初始化视觉工具"""
        self.api_type = os.getenv("AI_API_TYPE", "deepseek")
        self.claude_key = os.getenv("CLAUDE_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.qwen_key = os.getenv("QWEN_API_KEY")

        # 支持的图片格式
        self.supported_formats = {'.jpg', '.jpeg',
                                  '.png', '.gif', '.webp', '.bmp'}

        # 上传目录
        self.upload_dir = Path("uploads")
        self.upload_dir.mkdir(exist_ok=True)

    def encode_image(self, image_path: str) -> str:
        """
        将图片编码为base64字符串

        Args:
            image_path: 图片文件路径

        Returns:
            str: base64编码的图片数据
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def validate_image(self, image_path: str) -> tuple[bool, str]:
        """
        验证图片文件

        Args:
            image_path: 图片路径

        Returns:
            tuple: (是否有效, 错误信息)
        """
        path = Path(image_path)

        # 检查文件是否存在
        if not path.exists():
            return False, f"文件不存在: {image_path}"

        # 检查文件格式
        if path.suffix.lower() not in self.supported_formats:
            return False, f"不支持的文件格式: {path.suffix}。支持的格式: {', '.join(self.supported_formats)}"

        # 检查文件大小 (限制20MB)
        max_size = 20 * 1024 * 1024
        if path.stat().st_size > max_size:
            return False, f"文件过大: {path.stat().st_size / 1024 / 1024:.1f}MB (最大20MB)"

        return True, ""

    def analyze_with_qwen(self, image_path: str, prompt: str = "请详细描述这张图片") -> Dict[str, Any]:
        """使用通义千问 Qwen-VL 分析图片"""
        if not self.qwen_key:
            return {'success': False, 'error': 'Qwen API密钥未配置'}

        valid, error = self.validate_image(image_path)
        if not valid:
            return {'success': False, 'error': error}

        base64_image = self.encode_image(image_path)
        image_format = Path(image_path).suffix[1:]
        if image_format == 'jpg':
            image_format = 'jpeg'

        try:
            url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
            headers = {
                "Authorization": f"Bearer {self.qwen_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": "qwen-vl-max",  # 使用 max 版本，识别更准确
                "input": {
                    "messages": [{
                        "role": "user",
                        "content": [
                            {"image": f"data:image/{image_format};base64,{base64_image}"},
                            {"text": prompt}
                        ]
                    }]
                },
                "parameters": {}
            }

            response = requests.post(
                url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()

            if result.get('output') and result['output'].get('choices'):
                description = result['output']['choices'][0]['message']['content'][0]['text']
                return {
                    'success': True,
                    'description': description,
                    'model': 'qwen-vl-max',
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {'success': False, 'error': f'无法解析API响应: {result}'}

        except requests.exceptions.HTTPError as e:
            resp_text = ''
            try:
                resp_text = e.response.text
            except Exception:
                pass
            return {
                'success': False,
                'error': f'API请求失败: {str(e)}',
                'details': resp_text
            }
        except Exception as e:
            return {'success': False, 'error': f'分析失败: {str(e)}'}

    def analyze_with_claude(self, image_path: str, prompt: str = "请详细描述这张图片的内容") -> Dict[str, Any]:
        """
        使用Claude Vision分析图片

        Args:
            image_path: 图片路径
            prompt: 分析提示语

        Returns:
            dict: 分析结果
        """
        if not self.claude_key:
            return {
                'success': False,
                'error': 'Claude API密钥未配置'
            }

        # 验证图片
        valid, error = self.validate_image(image_path)
        if not valid:
            return {'success': False, 'error': error}

        # 编码图片
        base64_image = self.encode_image(image_path)

        # 获取图片格式
        image_format = Path(image_path).suffix[1:]  # 去掉点号
        if image_format == 'jpg':
            image_format = 'jpeg'

        try:
            # 调用Claude API
            url = "https://api.anthropic.com/v1/messages"
            headers = {
                "x-api-key": self.claude_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }

            data = {
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 1024,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": f"image/{image_format}",
                                    "data": base64_image
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            }

            response = requests.post(
                url, headers=headers, json=data, timeout=30)
            response.raise_for_status()

            result = response.json()

            return {
                'success': True,
                'description': result['content'][0]['text'],
                'model': 'claude-3.5-sonnet',
                'timestamp': datetime.now().isoformat()
            }

        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'API请求失败: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'分析失败: {str(e)}'
            }

    def analyze_with_gpt4v(self, image_path: str, prompt: str = "What's in this image?") -> Dict[str, Any]:
        """
        使用GPT-4V分析图片

        Args:
            image_path: 图片路径
            prompt: 分析提示语

        Returns:
            dict: 分析结果
        """
        if not self.openai_key:
            return {
                'success': False,
                'error': 'OpenAI API密钥未配置'
            }

        # 验证图片
        valid, error = self.validate_image(image_path)
        if not valid:
            return {'success': False, 'error': error}

        # 编码图片
        base64_image = self.encode_image(image_path)

        try:
            # 调用OpenAI API
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.openai_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": "gpt-4-vision-preview",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 1024
            }

            response = requests.post(
                url, headers=headers, json=data, timeout=30)
            response.raise_for_status()

            result = response.json()

            return {
                'success': True,
                'description': result['choices'][0]['message']['content'],
                'model': 'gpt-4-vision',
                'timestamp': datetime.now().isoformat()
            }

        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'API请求失败: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'分析失败: {str(e)}'
            }

    def analyze_image(self, image_path: str, prompt: Optional[str] = None,
                      prefer_model: str = "auto") -> Dict[str, Any]:
        """
        智能图片分析（自动选择可用模型）

        Args:
            image_path: 图片路径
            prompt: 分析提示语（可选）
            prefer_model: 优先使用的模型 ("qwen", "claude", "gpt4v", "auto")

        Returns:
            dict: 分析结果
        """
        # 默认提示语
        if prompt is None:
            prompt = "请详细描述这张图片的内容，包括场景、物体、人物、文字等所有可见元素。"

        # 检查密钥是否有效
        valid_qwen = self.qwen_key and self.qwen_key != "your_qwen_api_key_here"
        valid_claude = self.claude_key and len(self.claude_key) > 30
        valid_openai = self.openai_key and self.openai_key != "your_openai_api_key_here"

        # Auto 模式：优先 Qwen（国内可用）
        if prefer_model == "auto":
            if valid_qwen:
                result = self.analyze_with_qwen(image_path, prompt)
                if result['success']:
                    return result
                print(f"⚠️ Qwen失败: {result.get('error')}")

            if valid_claude:
                result = self.analyze_with_claude(image_path, prompt)
                if result['success']:
                    return result
                print(f"⚠️ Claude失败: {result.get('error')}")

            if valid_openai:
                return self.analyze_with_gpt4v(image_path, prompt)

            return {'success': False, 'error': '没有配置可用的视觉API (推荐配置 QWEN_API_KEY)'}

        # 指定使用 Qwen
        if prefer_model == "qwen":
            return self.analyze_with_qwen(image_path, prompt)

        # 根据优先级选择模型
        if prefer_model == "claude" or (prefer_model == "auto" and self.claude_key):
            result = self.analyze_with_claude(image_path, prompt)
            if result['success']:
                return result
            # Claude失败，尝试GPT-4V
            if self.openai_key:
                return self.analyze_with_gpt4v(image_path, prompt)
            return result

        elif prefer_model == "gpt4v" or (prefer_model == "auto" and self.openai_key):
            result = self.analyze_with_gpt4v(image_path, prompt)
            if result['success']:
                return result
            # GPT-4V失败，尝试Claude
            if self.claude_key:
                return self.analyze_with_claude(image_path, prompt)
            return result

        else:
            return {
                'success': False,
                'error': '没有配置可用的视觉API (需要CLAUDE_API_KEY或OPENAI_API_KEY)'
            }

    def save_upload(self, file_data: bytes, filename: str) -> tuple[bool, str]:
        """
        保存上传的图片文件

        Args:
            file_data: 文件二进制数据
            filename: 文件名

        Returns:
            tuple: (是否成功, 文件路径或错误信息)
        """
        try:
            # 生成唯一文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_filename = f"{timestamp}_{filename}"
            file_path = self.upload_dir / safe_filename

            # 保存文件
            with open(file_path, 'wb') as f:
                f.write(file_data)

            # 返回相对路径（用于前端访问）
            relative_path = f"uploads/{safe_filename}"
            return True, relative_path

        except Exception as e:
            return False, f"保存失败: {str(e)}"


# 工具接口（供tool_manager调用）
def vision_tool_interface(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    视觉工具接口

    Parameters:
        image_path: 图片路径 (必需)
        prompt: 分析提示语 (可选)
        model: 优先模型 "claude"/"gpt4v"/"auto" (可选，默认auto)

    Returns:
        dict: 图片分析结果
    """
    tool = VisionTool()

    # 获取参数
    image_path = parameters.get('image_path')
    prompt = parameters.get('prompt')
    model = parameters.get('model', 'auto')

    if not image_path:
        return {
            'success': False,
            'error': '缺少必需参数: image_path'
        }

    # 分析图片
    return tool.analyze_image(image_path, prompt, model)


# 工具元数据
VISION_TOOL_META = {
    'name': 'vision',
    'description': '分析和理解图片内容，识别物体、场景、文字等',
    'category': 'multimodal',
    'parameters': {
        'image_path': {
            'type': 'string',
            'description': '图片文件路径',
            'required': True
        },
        'prompt': {
            'type': 'string',
            'description': '分析提示语（可选）',
            'required': False
        },
        'model': {
            'type': 'string',
            'description': '优先使用的模型: claude/gpt4v/auto',
            'required': False,
            'default': 'auto'
        }
    },
    'examples': [
        {
            'prompt': '分析这张图片',
            'parameters': {'image_path': 'uploads/photo.jpg'}
        },
        {
            'prompt': '图片里有什么文字？',
            'parameters': {
                'image_path': 'uploads/document.png',
                'prompt': '识别图片中的所有文字内容'
            }
        }
    ]
}


if __name__ == "__main__":
    # 测试代码
    print("🧪 测试Vision Tool")
    print("=" * 60)

    tool = VisionTool()

    # 测试图片验证
    print("\n测试1: 图片验证")
    valid, error = tool.validate_image("test.jpg")
    print(f"结果: {'✅ 有效' if valid else f'❌ {error}'}")

    print("\n✅ Vision Tool初始化成功")
    print(f"支持格式: {', '.join(tool.supported_formats)}")
    print(f"上传目录: {tool.upload_dir}")
    print(f"Claude可用: {'✅' if tool.claude_key else '❌'}")
    print(f"GPT-4V可用: {'✅' if tool.openai_key else '❌'}")
