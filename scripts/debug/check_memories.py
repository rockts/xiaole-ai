from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_setup import Memory
from dotenv import load_dotenv
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))


load_dotenv()

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
    connect_args={'check_same_thread': False} if DB_URL.startswith('sqlite')
    else {'client_encoding': 'utf8'}
)
Session = sessionmaker(bind=engine)
session = Session()

memories = session.query(Memory).order_by(
    Memory.created_at.desc()).limit(20).all()

print(f"Total memories: {session.query(Memory).count()}")
print("-" * 50)
for m in memories:
    print(
        f"ID: {m.id}, Tag: {m.tag}, Created: {m.created_at}, Content: {m.content[:50]}...")
