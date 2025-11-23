from db_setup import SessionLocal, Message
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def fix_latex_spacing(session_id):
    session = SessionLocal()
    try:
        messages = session.query(Message).filter(
            Message.session_id == session_id).all()

        for msg in messages:
            original_content = msg.content
            new_content = original_content

            # Fix 1: Add space after inline math and before Chinese parenthesis
            # Target: $\mu_0 \varepsilon_0 \frac{d\Phi_E}{dt}$（位移电流）
            if "$\\mu_0 \\varepsilon_0 \\frac{d\\Phi_E}{dt}$（位移电流）" in new_content:
                print(f"Message {msg.id}: Adding space before （位移电流）")
                new_content = new_content.replace(
                    "$\\mu_0 \\varepsilon_0 \\frac{d\\Phi_E}{dt}$（位移电流）",
                    "$\\mu_0 \\varepsilon_0 \\frac{d\\Phi_E}{dt}$ （位移电流）"
                )

            # Fix 2: Ensure blank line before block math $$
            # Target: 高斯定律的数学表达式是：\n$$
            if "高斯定律的数学表达式是：\n$$" in new_content:
                print(f"Message {msg.id}: Adding blank line before block math")
                new_content = new_content.replace(
                    "高斯定律的数学表达式是：\n$$",
                    "高斯定律的数学表达式是：\n\n$$"
                )

            # Fix 3: Ensure blank line after block math $$ if needed
            # Target: $$\n\n**第一步
            # It seems there is already a newline in the previous output:
            # $$
            #
            # **第一步...
            # Let's check the raw content from previous inspect.
            # Message 4: ...\varepsilon_0}\n$$\n\n**第一步...
            # This looks fine (two newlines).

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
    fix_latex_spacing(session_id)
