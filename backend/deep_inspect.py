from db_setup import SessionLocal, Message
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def deep_inspect(session_id):
    session = SessionLocal()
    try:
        messages = session.query(Message).filter(
            Message.session_id == session_id).all()

        for msg in messages:
            content = msg.content
            if "mu_0 I" in content:
                print(f"--- Message {msg.id} (mu_0 I check) ---")
                index = content.find("mu_0 I")
                # Print 20 chars before and after
                start = max(0, index - 20)
                end = min(len(content), index + 20)
                snippet = content[start:end]
                print(f"Snippet: {repr(snippet)}")

            if "Q_{\\text{内}}" in content or "Q_{\text{内}}" in content:
                print(f"--- Message {msg.id} (Q_text check) ---")
                # Find index
                try:
                    index = content.index("Q_{\\text{内}}")
                except ValueError:
                    try:
                        index = content.index("Q_{\text{内}}")
                    except ValueError:
                        index = -1

                if index != -1:
                    start = max(0, index - 20)
                    end = min(len(content), index + 20)
                    snippet = content[start:end]
                    print(f"Snippet: {repr(snippet)}")

    finally:
        session.close()


if __name__ == "__main__":
    session_id = "50ca2114-edcb-4f9a-a979-d4e3455a4c4a"
    deep_inspect(session_id)
