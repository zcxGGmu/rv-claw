from __future__ import annotations

import asyncio
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase


async def add_user_role(db: AsyncIOMotorDatabase) -> dict[str, Any]:
    """为现有 users 集合补 role 字段（默认 user）.

    幂等执行：重复运行无副作用.

    Args:
        db: MongoDB 数据库实例.

    Returns:
        执行结果统计.
    """
    users = db.get_collection("users")

    result = await users.update_many(
        {"role": {"$exists": False}},
        {"$set": {"role": "user"}},
    )

    return {
        "modified_count": result.modified_count,
        "matched_count": result.matched_count,
    }


async def create_pipeline_collections(db: AsyncIOMotorDatabase) -> dict[str, Any]:
    """创建 Pipeline 相关集合和索引.

    幂等执行：重复运行无副作用.

    Args:
        db: MongoDB 数据库实例.

    Returns:
        执行结果统计.
    """
    from backend.db.collections import create_pipeline_indexes, create_ttl_indexes

    # 创建集合（如果存在则跳过）
    for name in ["contribution_cases", "human_reviews", "audit_log", "stage_outputs"]:
        try:
            await db.create_collection(name)
        except Exception:
            pass  # 集合已存在

    # 创建索引
    await create_pipeline_indexes(db)
    await create_ttl_indexes(db)

    return {"status": "ok"}


async def main():
    from backend.mongodb.db import db
    await db.connect()
    try:
        result1 = await add_user_role(db.get_db())
        print(f"Migration 001 (add user role): {result1}")

        result2 = await create_pipeline_collections(db.get_db())
        print(f"Migration 002 (create pipeline collections): {result2}")
    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(main())
