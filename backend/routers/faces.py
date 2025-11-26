from fastapi import APIRouter
from face_manager import FaceManager
from db_setup import SessionLocal, FaceEncoding

router = APIRouter(
    prefix="/api/faces",
    tags=["faces"]
)


@router.get("")
def list_faces():
    """列出所有已注册的人脸"""
    try:
        manager = FaceManager()
        encodings, names = manager.get_known_faces()

        face_counts = {}
        for name in names:
            face_counts[name] = face_counts.get(name, 0) + 1

        result = [
            {"name": name, "count": count}
            for name, count in face_counts.items()
        ]

        return {
            "success": True,
            "faces": result,
            "total_people": len(result),
            "total_encodings": len(names)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.delete("/{name}")
def delete_face(name: str):
    """删除指定人名下的所有面部数据"""
    try:
        db = SessionLocal()
        try:
            deleted_count = db.query(FaceEncoding).filter(
                FaceEncoding.name == name).delete()
            db.commit()

            return {
                "success": True,
                "message": f"已删除 '{name}' 的 {deleted_count} 条面部数据",
                "deleted_count": deleted_count
            }
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
