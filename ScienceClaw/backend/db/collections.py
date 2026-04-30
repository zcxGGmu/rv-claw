"""MongoDB 集合初始化与索引管理.

TODO: 实现 create_pipeline_indexes() 和 create_ttl_indexes() 函数.
参考 progress.md P0.5.2 和 design.md §6.3.
"""
from motor.motor_asyncio import AsyncIOMotorDatabase


async def create_pipeline_indexes(db: AsyncIOMotorDatabase) -> None:
    """创建 Pipeline 相关集合的索引.

    Args:
        db: MongoDB 数据库实例

    TODO: 创建以下索引:
        - contribution_cases: {status: 1, created_at: -1}
        - contribution_cases: {target_repo: 1}
        - contribution_cases: {created_by: 1}
        - human_reviews: {case_id: 1, created_at: -1}
        - audit_log: {case_id: 1, timestamp: -1}
    """
    ...


async def create_ttl_indexes(db: AsyncIOMotorDatabase) -> None:
    """创建 TTL 索引.

    Args:
        db: MongoDB 数据库实例

    TODO: 创建以下 TTL 索引:
        - contribution_cases: {abandoned_at: 1}, expireAfterSeconds=7776000
          partialFilterExpression={status: "abandoned"}
        - audit_log: {timestamp: 1}, expireAfterSeconds=63072000
    """
    ...
