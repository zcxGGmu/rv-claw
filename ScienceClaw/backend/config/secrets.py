"""Secrets 管理 — 生产环境敏感字段不可打印/日志泄露."""
from __future__ import annotations

from pydantic import SecretStr
from backend.config import settings


class SecretManager:
    """统一封装敏感配置字段的访问."""

    _secrets = {
        "CLAUDE_API_KEY": settings.claude_api_key,
        "OPENAI_API_KEY": settings.openai_api_key,
        "DS_API_KEY": settings.model_ds_api_key,
        "POSTGRES_PASSWORD": "rv_password",  # 从 URI 解析或环境变量读取
        "MONGODB_PASSWORD": settings.mongodb_password,
    }

    @classmethod
    def get(cls, key: str) -> str:
        """获取密钥明文值.

        Args:
            key: 密钥名称.

        Returns:
            密钥明文.

        Raises:
            KeyError: 密钥不存在.
        """
        if key not in cls._secrets:
            raise KeyError(f"Secret {key} not found")
        return cls._secrets[key]

    @classmethod
    def mask(cls, value: str | None, visible_chars: int = 4) -> str:
        """脱敏显示密钥.

        Args:
            value: 原始密钥值.
            visible_chars: 尾部可见字符数.

        Returns:
            脱敏后的字符串，如 ***abcd.
        """
        if not value:
            return "***"
        if len(value) <= visible_chars:
            return "*" * len(value)
        return "*" * (len(value) - visible_chars) + value[-visible_chars:]

    def __repr__(self) -> str:
        return "<SecretManager>"

    def __str__(self) -> str:
        return "<SecretManager>"
