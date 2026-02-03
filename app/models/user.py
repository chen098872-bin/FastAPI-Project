from typing import Optional

from . import Base
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Integer, String, DateTime, Text, Boolean  # 新增 Boolean
import bcrypt
from datetime import datetime

class User(Base):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    username: Mapped[str] = mapped_column(String(100))
    _password: Mapped[str] = mapped_column(String(200))

    # ********** 新增用户资料字段 **********
    nickname: Mapped[str] = mapped_column(String(100), default="", comment="用户展示昵称（可与username不同）")
    gender: Mapped[str]= mapped_column(String(10), default="未知", comment="用户性别（男/女/未知）")
    avatar: Mapped[str] = mapped_column(Text, default="", comment="用户头像URL")
    phone: Mapped[str] = mapped_column(String(11), unique=True, index=True, default="",
                                                 comment="用户手机号（11位，唯一）")


    def __init__(self, *args, **kwargs):
        password = kwargs.pop("password", None)
        super().__init__(*args, **kwargs)
        if password:
            self.password = password

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        if not password:
            raise ValueError("密码不能为空")
        if len(password) < 8:
            raise ValueError("密码至少需要8个字符")
        salt = bcrypt.gensalt()
        self._password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def check_password(self, raw_password):
        if not raw_password or not self._password:
            return False
        return bcrypt.checkpw(raw_password.encode('utf-8'), self._password.encode('utf-8'))

class EmailCode(Base):
    __tablename__ = 'email_code'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(100))
    code: Mapped[str] = mapped_column(String(10))
    create_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)