import face_recognition
import numpy as np
import os
import logging
import base64
import requests
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from tool_manager import Tool, ToolParameter
from db_setup import SessionLocal, FaceEncoding

logger = logging.getLogger(__name__)


class VisionTool(Tool):
    def __init__(self):
        super().__init__()
        self.name = "vision_analysis"
        self.description = "Analyze images to identify people using face recognition."
        self.category = "vision"
        self.parameters = [
            ToolParameter(
                name="image_path",
                param_type="string",
                description="The path to the image file to analyze.",
                required=True
            )
        ]
        self.qwen_key = os.getenv("QWEN_API_KEY")
        self.claude_key = os.getenv("CLAUDE_API_KEY")

    def _resolve_path(self, image_path: str) -> Optional[str]:
        """Resolve image path relative to backend or project root"""
        if os.path.exists(image_path):
            return image_path

        # Try relative to backend root
        backend_root = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))
        potential_path = os.path.join(backend_root, image_path)
        if os.path.exists(potential_path):
            return potential_path

        # Try relative to project root
        project_root = os.path.dirname(backend_root)
        potential_path = os.path.join(project_root, image_path)
        if os.path.exists(potential_path):
            return potential_path

        # Try removing leading slash if present
        if image_path.startswith('/'):
            return self._resolve_path(image_path[1:])

        return None

    def analyze_image(self, image_path: str, prompt: str = None, prefer_model: str = "auto") -> Dict[str, Any]:
        """
        Analyze image content using hybrid approach:
        1. Use face_recognition to identify known people
        2. Use Vision LLM (Qwen-VL/Claude) for general scene description
        """
        try:
            if not prompt:
                prompt = "请详细描述这张图片的内容。"

            full_path = self._resolve_path(image_path)
            if not full_path:
                return {"success": False, "error": f"Image file not found: {image_path}"}

            # Step 1: Face Recognition
            face_info = ""
            try:
                # Load image
                image = face_recognition.load_image_file(full_path)
                # Detect faces
                face_locations = face_recognition.face_locations(image)

                if len(face_locations) > 0:
                    face_encodings = face_recognition.face_encodings(
                        image, face_locations)

                    # Load known faces from DB
                    db = SessionLocal()
                    known_face_encodings = []
                    known_face_names = []
                    try:
                        known_faces = db.query(FaceEncoding).all()
                        for face in known_faces:
                            if face.encoding:
                                known_face_encodings.append(
                                    np.array(face.encoding))
                                known_face_names.append(face.name)
                    finally:
                        db.close()

                    identified_people = []
                    if known_face_encodings:
                        for face_encoding in face_encodings:
                            matches = face_recognition.compare_faces(
                                known_face_encodings, face_encoding, tolerance=0.6)
                            name = "未知人物"

                            face_distances = face_recognition.face_distance(
                                known_face_encodings, face_encoding)
                            if len(face_distances) > 0:
                                best_match_index = np.argmin(face_distances)
                                if matches[best_match_index]:
                                    name = known_face_names[best_match_index]

                            identified_people.append(name)
                    else:
                        identified_people = ["未知人物"] * len(face_locations)

                    # Filter out unknown people to avoid noise if desired, or keep them
                    known_people = [
                        p for p in identified_people if p != "未知人物"]

                    if known_people:
                        face_info = f"【人脸识别结果】图中发现了以下熟人：{', '.join(known_people)}。\n"
                    else:
                        face_info = f"【人脸识别结果】图中发现了 {len(face_locations)} 个人，但未识别出具体身份。\n"

            except Exception as e:
                logger.error(f"Face recognition failed: {e}")
                face_info = "【人脸识别】人脸检测过程中出现错误，跳过此步骤。\n"

            # Step 2: Vision LLM Analysis
            llm_result = {}
            # Dispatch based on model preference and availability
            if prefer_model == "qwen" or (prefer_model == "auto" and self.qwen_key):
                llm_result = self.analyze_with_qwen(full_path, prompt)
            elif prefer_model == "claude" or (prefer_model == "auto" and self.claude_key):
                llm_result = self.analyze_with_claude(full_path, prompt)
            else:
                llm_result = {
                    "success": False,
                    "error": "No suitable vision model configured. Please set QWEN_API_KEY or CLAUDE_API_KEY."
                }

            if not llm_result.get("success"):
                return llm_result

            # Combine results
            final_description = face_info + "\n" + \
                llm_result.get("description", "")

            return {
                "success": True,
                "description": final_description.strip(),
                "model": llm_result.get("model", "unknown"),
                "face_info": face_info
            }

        except Exception as e:
            logger.error(f"Analyze image failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    def analyze_with_qwen(self, image_path: str, prompt: str) -> Dict[str, Any]:
        """Use Qwen-VL-Plus for image analysis"""
        try:
            if not self.qwen_key:
                return {"success": False, "error": "Qwen API key not configured"}

            # Encode image to base64
            with open(image_path, "rb") as f:
                base64_image = base64.b64encode(f.read()).decode('utf-8')

            # Determine mime type
            ext = os.path.splitext(image_path)[1].lower()
            mime_type = "image/jpeg"
            if ext == ".png":
                mime_type = "image/png"
            elif ext == ".webp":
                mime_type = "image/webp"
            elif ext == ".gif":
                mime_type = "image/gif"

            data_uri = f"data:{mime_type};base64,{base64_image}"

            url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
            headers = {
                "Authorization": f"Bearer {self.qwen_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "qwen-vl-plus",
                "input": {
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"image": data_uri},
                                {"text": prompt}
                            ]
                        }
                    ]
                }
            }

            response = requests.post(
                url, headers=headers, json=payload, timeout=60)

            if response.status_code == 200:
                result = response.json()
                if "output" in result and "choices" in result["output"]:
                    content = result["output"]["choices"][0]["message"]["content"][0]["text"]
                    return {
                        "success": True,
                        "description": content,
                        "model": "qwen-vl-plus"
                    }
                else:
                    return {"success": False, "error": f"Qwen API format error: {result}"}
            else:
                return {"success": False, "error": f"Qwen API error: {response.status_code} - {response.text}"}

        except Exception as e:
            return {"success": False, "error": f"Qwen analysis failed: {str(e)}"}

    def analyze_with_claude(self, image_path: str, prompt: str) -> Dict[str, Any]:
        """Use Claude 3.5 Sonnet for image analysis"""
        try:
            if not self.claude_key:
                return {"success": False, "error": "Claude API key not configured"}

            import anthropic
            client = anthropic.Anthropic(api_key=self.claude_key)

            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode("utf-8")

            ext = os.path.splitext(image_path)[1].lower().replace('.', '')
            if ext == 'jpg':
                ext = 'jpeg'
            media_type = f"image/{ext}"

            message = client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_data,
                                },
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ],
                    }
                ],
            )

            return {
                "success": True,
                "description": message.content[0].text,
                "model": "claude-3-5-sonnet"
            }

        except Exception as e:
            return {"success": False, "error": f"Claude analysis failed: {str(e)}"}

    async def execute(self, image_path: str, prompt: str = None, **kwargs) -> Dict[str, Any]:
        try:
            # Handle relative paths
            image_path = self._resolve_path(image_path) or image_path

            # Check if path exists
            if not os.path.exists(image_path):
                return {
                    "success": False,
                    "error": f"Image file not found: {image_path}",
                    "result": None
                }

            logger.info(f"👁️ VisionTool analyzing: {image_path}")

            # Use the hybrid analysis method
            analysis_result = self.analyze_image(image_path, prompt=prompt)

            if not analysis_result.get("success"):
                return {
                    "success": False,
                    "error": analysis_result.get("error", "Unknown error during analysis"),
                    "result": None
                }

            return {
                "success": True,
                "result": {
                    "description": analysis_result.get("description", ""),
                    "face_info": analysis_result.get("face_info", ""),
                    "model": analysis_result.get("model", "unknown")
                }
            }

        except Exception as e:
            logger.error(f"VisionTool error: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "result": None
            }

    def save_upload(self, file_data: bytes, filename: str) -> tuple[bool, str]:
        """Save uploaded image file"""
        try:
            # Determine upload directory
            # Try to find backend/uploads directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # tools/vision_tool.py -> tools/ -> root -> backend -> uploads

            project_root = os.path.dirname(current_dir)
            uploads_dir = os.path.join(project_root, "backend", "uploads")

            if not os.path.exists(uploads_dir):
                os.makedirs(uploads_dir, exist_ok=True)

            # Generate safe filename
            import time
            timestamp = int(time.time())
            safe_filename = f"{timestamp}_{filename}"
            file_path = os.path.join(uploads_dir, safe_filename)

            # Save file
            with open(file_path, "wb") as f:
                f.write(file_data)

            # Return relative path (for frontend access)
            # Frontend access /uploads/xxx -> Backend mount /uploads
            # -> backend/uploads/xxx
            return True, f"/uploads/{safe_filename}"

        except Exception as e:
            logger.error(f"Failed to save uploaded image: {e}")
            return False, str(e)


class RegisterFaceTool(Tool):
    def __init__(self):
        super().__init__()
        self.name = "register_face"
        self.description = "Register a new face for recognition. Use this when the user explicitly says 'This is [Name]' or wants to teach the AI a person's face."
        self.category = "vision"
        self.parameters = [
            ToolParameter(
                name="image_path",
                param_type="string",
                description="The path to the image file containing the face.",
                required=True
            ),
            ToolParameter(
                name="person_name",
                param_type="string",
                description="The name of the person to register.",
                required=True
            )
        ]

    def _resolve_path(self, image_path: str) -> Optional[str]:
        """Resolve image path relative to backend or project root"""
        if os.path.exists(image_path):
            return image_path

        # Try relative to backend root
        backend_root = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))
        potential_path = os.path.join(backend_root, image_path)
        if os.path.exists(potential_path):
            return potential_path

        # Try relative to project root
        project_root = os.path.dirname(backend_root)
        potential_path = os.path.join(project_root, image_path)
        if os.path.exists(potential_path):
            return potential_path

        # Try removing leading slash if present
        if image_path.startswith('/'):
            return self._resolve_path(image_path[1:])

        return None

    async def execute(self, image_path: str, person_name: str, **kwargs) -> Dict[str, Any]:
        try:
            full_path = self._resolve_path(image_path)
            if not full_path:
                return {"success": False, "error": f"Image file not found: {image_path}"}

            logger.info(
                f"👤 Registering face for '{person_name}' from {full_path}")

            # Load image
            image = face_recognition.load_image_file(full_path)

            # Detect faces
            face_locations = face_recognition.face_locations(image)

            if len(face_locations) == 0:
                return {
                    "success": False,
                    "error": "No faces detected in the image. Please provide a clear photo of the person."
                }

            if len(face_locations) > 1:
                return {
                    "success": False,
                    "error": f"Found {len(face_locations)} faces. Please provide a photo with only one person to avoid ambiguity."
                }

            # Get encoding
            face_encodings = face_recognition.face_encodings(
                image, face_locations)
            if not face_encodings:
                return {
                    "success": False,
                    "error": "Could not generate face encoding. The face might be too small or unclear."
                }

            new_encoding = face_encodings[0].tolist()

            # Save to DB
            db = SessionLocal()
            try:
                # Check if name already exists, if so, update/add new encoding?
                # For simplicity, we just add a new record.
                # Ideally we might want to merge or check duplicates, but multiple encodings for same name is fine (improves accuracy).

                face_record = FaceEncoding(
                    name=person_name,
                    encoding=new_encoding,
                    created_at=datetime.now()
                )
                db.add(face_record)
                db.commit()

                return {
                    "success": True,
                    "result": f"Successfully registered face for '{person_name}'."
                }
            except Exception as e:
                db.rollback()
                return {"success": False, "error": f"Database error: {str(e)}"}
            finally:
                db.close()

        except Exception as e:
            logger.error(f"RegisterFaceTool error: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
