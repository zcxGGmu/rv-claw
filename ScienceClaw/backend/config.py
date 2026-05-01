import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "local")
    if ENVIRONMENT == "local":
        load_dotenv(".env")

    model_ds_name: str = os.environ.get("DS_MODEL") or "gpt-5.4"
    model_ds_api_key: str = os.environ.get("DS_API_KEY") or "sk-c83004a45ce5c4ce4f81fe0b8fa93b61"
    model_ds_base_url: str = os.environ.get("DS_URL") or "https://claude.hanbbq.top/v1"
    max_tokens: int = int(os.environ.get("MAX_TOKENS", "2000"))
    context_window: int = int(os.environ.get("CONTEXT_WINDOW", "1000000"))

    https_only: bool = os.environ.get("HTTPS_ONLY", "false").lower() == "true"
    session_cookie: str = os.environ.get("SESSION_COOKIE") or "zdtc-agent-session"
    session_max_age: int = int(os.environ.get("SESSION_MAX_AGE", str(3600 * 24 * 7)))

    auth_provider: str = os.environ.get("AUTH_PROVIDER", "local")

    bootstrap_admin_enabled: bool = os.environ.get("BOOTSTRAP_ADMIN_ENABLED", "true").lower() == "true"
    bootstrap_admin_username: str = os.environ.get("BOOTSTRAP_ADMIN_USERNAME", "admin")
    bootstrap_admin_password: str = os.environ.get("BOOTSTRAP_ADMIN_PASSWORD", "admin123")
    bootstrap_admin_fullname: str = os.environ.get("BOOTSTRAP_ADMIN_FULLNAME", "Administrator")
    bootstrap_admin_email: str = os.environ.get("BOOTSTRAP_ADMIN_EMAIL", "admin@localhost")
    bootstrap_update_admin_password: bool = os.environ.get("BOOTSTRAP_UPDATE_ADMIN_PASSWORD", "false").lower() == "true"

    mongodb_host: str = os.environ.get("MONGODB_HOST", "localhost")
    mongodb_port: int = int(os.environ.get("MONGODB_PORT", "27014"))
    mongodb_db_name: str = os.environ.get("MONGODB_DB", "ai_agent")
    mongodb_username: str = os.environ.get("MONGODB_USER", "")
    mongodb_password: str = os.environ.get("MONGODB_PASSWORD", "")

    xelatex_cmd: str = os.environ.get("XELATEX_CMD", "/usr/local/texlive/2025/bin/universal-darwin/xelatex")
    pandoc_cmd: str = os.environ.get("PANDOC_CMD", "/usr/local/bin/pandoc")

    # 网页搜索服务（websearch 微服务）
    websearch_base_url: str = os.environ.get("WEBSEARCH_BASE_URL", "http://websearch:8068")
    websearch_api_key: str = os.environ.get("WEBSEARCH_API_KEY", "")

    # 沙盒服务（MCP 协议）
    sandbox_mcp_url: str = os.environ.get("SANDBOX_MCP_URL", "http://sandbox:8080/mcp")

    # 任务调度服务调用聊天接口时的 API Key（可选）
    task_service_api_key: str = os.environ.get("TASK_SERVICE_API_KEY", "")
    im_enabled: bool = os.environ.get("IM_ENABLED", "false").lower() == "true"
    im_response_timeout: int = int(os.environ.get("IM_RESPONSE_TIMEOUT", "300"))
    im_max_message_length: int = int(os.environ.get("IM_MAX_MESSAGE_LENGTH", "4000"))

    lark_enabled: bool = os.environ.get("LARK_ENABLED", "false").lower() == "true"
    lark_app_id: str = os.environ.get("LARK_APP_ID", "")
    lark_app_secret: str = os.environ.get("LARK_APP_SECRET", "")

    # PostgreSQL (LangGraph Checkpointer)
    postgres_uri: str = os.environ.get(
        "POSTGRES_URI",
        "postgresql+asyncpg://rv:rv_password@localhost:5432/rv_checkpoints",
    )

    # Redis
    redis_url: str = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

    # Pipeline 配置
    max_review_iterations: int = int(os.environ.get("MAX_REVIEW_ITERATIONS", "3"))
    max_agent_turns: int = int(os.environ.get("MAX_AGENT_TURNS", "50"))
    max_concurrent_claude: int = int(os.environ.get("MAX_CONCURRENT_CLAUDE", "3"))
    max_concurrent_openai: int = int(os.environ.get("MAX_CONCURRENT_OPENAI", "5"))
    max_concurrent_qemu: int = int(os.environ.get("MAX_CONCURRENT_QEMU", "2"))

    # 成本限制
    max_cost_per_case: float = float(os.environ.get("MAX_COST_PER_CASE", "10.0"))
    max_cost_per_hour: float = float(os.environ.get("MAX_COST_PER_HOUR", "50.0"))

    # Claude / OpenAI 配置 — 统一使用同一 OpenAI 兼容接口
    claude_api_key: str = os.environ.get("CLAUDE_API_KEY", "sk-c83004a45ce5c4ce4f81fe0b8fa93b61")
    claude_model: str = os.environ.get("CLAUDE_MODEL", "gpt-5.4")
    openai_api_key: str = os.environ.get("OPENAI_API_KEY", "sk-c83004a45ce5c4ce4f81fe0b8fa93b61")
    openai_model: str = os.environ.get("OPENAI_MODEL", "gpt-5.4")
    codex_model: str = os.environ.get("CODEX_MODEL", "gpt-5.4")
    openai_base_url: str = os.environ.get("OPENAI_BASE_URL", "https://claude.hanbbq.top/v1")

    # Feature Flags
    pipeline_enabled: bool = os.environ.get("PIPELINE_ENABLED", "false").lower() == "true"
    qemu_sandbox_enabled: bool = os.environ.get("QEMU_SANDBOX_ENABLED", "false").lower() == "true"


# 全局配置实例
settings = Settings()
