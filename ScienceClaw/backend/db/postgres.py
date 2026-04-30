"""PostgreSQL 数据库连接层 — LangGraph Checkpointer 支持.

TODO: 实现 init_checkpointer() 函数和 AsyncConnectionPool 配置.
参考 progress.md P0.4.2 和 design.md §5.2.
"""
from typing import Any

from psycopg_pool import AsyncConnectionPool


async def init_checkpointer(
    postgres_uri: str,
) -> Any:
    """初始化 AsyncPostgresSaver.

    Args:
        postgres_uri: PostgreSQL 连接字符串，格式：
            postgresql+asyncpg://user:password@host:port/database

    Returns:
        AsyncPostgresSaver 实例

    TODO: 完成实现后返回正确的类型.
    """
    from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

    connection_kwargs = {"autocommit": True, "prepare_threshold": 0}
    pool = AsyncConnectionPool(
        conninfo=postgres_uri,
        max_size=20,
        kwargs=connection_kwargs,
    )
    saver = AsyncPostgresSaver(pool)
    await saver.setup()
    return saver
