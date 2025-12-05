
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.db_setup import Memory
import os
from dotenv import load_dotenv

load_dotenv()

# Setup DB connection
if os.getenv('DATABASE_URL'):
    DB_URL = os.getenv('DATABASE_URL')
else:
    DB_URL = (
        f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}"
        f"/{os.getenv('DB_NAME')}"
    )

engine = create_engine(
    DB_URL,
    client_encoding='utf8'
)
Session = sessionmaker(bind=engine)
session = Session()


def search_memory(keywords):
    print(f"Searching for keywords: {keywords}")
    results = []
    for kw in keywords:
        # Use ilike for case-insensitive search if needed, but for Chinese like is fine.
        # The issue might be client encoding.
        try:
            memories = session.query(Memory).filter(
                Memory.content.like(f'%{kw}%')).all()
            for m in memories:
                results.append(f"[{m.tag}] {m.content}")
        except Exception as e:
            print(f"Error searching for {kw}: {e}")

    return list(set(results))


keywords = ['女儿', '姑娘', '闺女', '名字', '叫']
found = search_memory(keywords)

if found:
    print("Found memories:")
    for f in found:
        print(f)
else:
    print("No relevant memories found.")

session.close()
