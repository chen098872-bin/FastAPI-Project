"""
测试配置模块
"""
import pytest
from app.core.config import Settings


def test_settings_default_values():
    """测试配置默认值"""
    settings = Settings()

    # 测试基本配置
    assert settings.API_HOST == "127.0.0.1"
    assert settings.API_PORT == 8000
    assert settings.DEBUG is False

    # 测试AI配置
    assert settings.DEEPSEEK_MODEL == "deepseek-chat"
    assert settings.ALIBABA_MODEL == "qwen-plus"

    # 测试文件上传配置
    assert settings.MAX_UPLOAD_SIZE == 5242880
    assert '.png' in settings.ALLOWED_EXTENSIONS


def test_settings_database_url():
    """测试数据库URL生成"""
    settings = Settings(
        DB_HOST="localhost",
        DB_PORT=3306,
        DB_NAME="test_db",
        DB_USER="test_user",
        DB_PASSWORD="test_pass"
    )

    expected_url = "mysql+aiomysql://test_user:test_pass@localhost:3306/test_db"
    assert settings.DATABASE_URL == expected_url


def test_settings_env_override(monkeypatch):
    """测试环境变量覆盖"""
    monkeypatch.setenv("API_HOST", "0.0.0.0")
    monkeypatch.setenv("API_PORT", "9000")
    monkeypatch.setenv("DEBUG", "true")

    settings = Settings()

    assert settings.API_HOST == "0.0.0.0"
    assert settings.API_PORT == 9000
    assert settings.DEBUG is True


def test_settings_secret_key_generation():
    """测试SECRET_KEY自动生成"""
    settings = Settings(SECRET_KEY="your-secret-key-change-in-production")

    # 应该生成一个新的随机密钥
    assert len(settings.SECRET_KEY) == 64  # 32字节的十六进制字符串
    assert settings.SECRET_KEY != "your-secret-key-change-in-production"


def test_settings_directory_creation(tmp_path):
    """测试目录自动创建"""
    settings = Settings(BASE_DIR=tmp_path)

    avatar_dir = tmp_path / "static" / "avatars"
    assert avatar_dir.exists()


def test_settings_validation():
    """测试配置验证"""
    # 测试有效的扩展名
    settings = Settings(ALLOWED_EXTENSIONS=".png,.jpg,.jpeg")
    assert settings.ALLOWED_EXTENSIONS == {'.png', '.jpg', '.jpeg'}

    # 测试DEBUG字符串解析
    settings = Settings(DEBUG="false")
    assert settings.DEBUG is False

    settings = Settings(DEBUG="true")
    assert settings.DEBUG is True
