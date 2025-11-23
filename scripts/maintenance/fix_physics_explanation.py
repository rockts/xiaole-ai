from db_setup import SessionLocal, Message
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def fix_physics_explanation(session_id):
    session = SessionLocal()
    try:
        messages = session.query(Message).filter(
            Message.session_id == session_id).all()

        for msg in messages:
            original_content = msg.content
            new_content = original_content

            # Target the specific misleading sentence in Inference 3
            old_text = "无论袋子多奇怪，只要有电场线穿入，就必然从另一侧穿出（因为电场线始于正电荷，不会无故中断），最终计算出的净通量依然是 **+Q / ε₀**。"
            new_text = "无论袋子形状多奇怪，源自内部电荷 +Q 的每一条电场线最终都必须穿出袋子才能延伸到远处。虽然对于凹陷的袋子，同一条线可能多次穿进穿出，但穿出的次数总比穿进多一次，所以总的净通量（穿出减穿进）依然保持不变，等于 **+Q / ε₀**。"

            if old_text in new_content:
                print(
                    f"Message {msg.id}: Fixing physics explanation in Inference 3")
                new_content = new_content.replace(old_text, new_text)

            if original_content != new_content:
                msg.content = new_content
                session.add(msg)
                print(f"Message {msg.id} updated.")
            else:
                print(f"Message {msg.id} needs no changes.")

        session.commit()
        print("All updates committed.")

    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    session_id = "50ca2114-edcb-4f9a-a979-d4e3455a4c4a"
    fix_physics_explanation(session_id)
