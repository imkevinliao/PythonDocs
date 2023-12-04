#sqlalchemy
首先写好模型
```
# filename  moudules.py
from sqlalchemy import Column, Integer, Text
from sqlalchemy import String
from sqlalchemy.orm import declarative_base
from sqlalchemy_repr import RepresentableBase

Base = declarative_base(cls=RepresentableBase)

class UserInfo(Base):
    __tablename__ = "UserInfo"
    id = Column(Integer, primary_key=True)
    user_first_name = Column(String(10))
    user_last_name = Column(String(20))
    user_info = Column(Text)
    user_content = Column(String(100))

```

---
在需要使用的地方进行导入
```
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from modules import Base, UserInfo

def create_table(is_force=False):
    if is_force:
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
    else:
        Base.metadata.create_all(engine, checkfirst=True)

if __name__ == '__main__':
    url = f"""sqlite:///{os.path.join(os.path.dirname(__file__), "user.db")}"""
    engine = create_engine(url)
    session = Session(engine)
    create_table(is_force=True)
    session.add(UserInfo(user_first_name="first_name",user_last_name="last_name",user_info="none info",user_content="none content"))
    session.commit()
    session.close()
```
