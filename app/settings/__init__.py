from datetime import timedelta

# 数据库相关配置
DB_URI = "mysql+aiomysql://root:111111@127.0.0.1:3306/llm-chat?charset=utf8mb4"


# 邮箱相关配置
MAIL_USERNAME="1726729576@qq.com"
MAIL_PASSWORD="nvmleymfxkxuecjb"
MAIL_FROM="1726729576@qq.com"
MAIL_PORT=587
MAIL_SERVER="smtp.qq.com"
MAIL_FROM_NAME="llm-chat"
MAIL_STARTTLS=True
MAIL_SSL_TLS=False



JWT_SECRET_KEY = "sfsadadafsjw"
JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=15)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)