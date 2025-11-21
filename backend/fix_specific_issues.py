from db_setup import SessionLocal, Message
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def fix_specific_issues(session_id):
    session = SessionLocal()
    try:
        messages = session.query(Message).filter(
            Message.session_id == session_id).all()

        for msg in messages:
            original_content = msg.content
            new_content = original_content

            # Fix 1: Q_{\text{内}} -> Q_{\text{in}}
            if "Q_{\\text{内}}" in new_content:
                print(
                    f"Message {msg.id}: Replacing Q_{{\\text{{内}}}} with Q_{{\\text{{in}}}}")
                new_content = new_content.replace(
                    "Q_{\\text{内}}", "Q_{\\text{in}}")

            # Fix 2: Add spaces around $\mu_0 I$ in the description
            # Target: 总电流 $\mu_0 I$（传导电流
            if "总电流 $\\mu_0 I$（传导电流" in new_content:
                print(f"Message {msg.id}: Adding space after $\\mu_0 I$")
                new_content = new_content.replace(
                    "总电流 $\\mu_0 I$（传导电流", "总电流 $\\mu_0 I$ （传导电流")

            # Also check if there are other places needing spaces
            # ...常数 $\varepsilon_0$ 与...
            # It seems fine, but let's be safe.

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
    fix_specific_issues(session_id)
