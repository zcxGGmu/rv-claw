"""StateGraph 构建与编译 — LangGraph Pipeline 引擎核心."""
from __future__ import annotations

from typing import Any

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from backend.pipeline.state import PipelineState
from backend.pipeline.nodes.explore import explore_node
from backend.pipeline.nodes.plan import plan_node
from backend.pipeline.nodes.develop import develop_node
from backend.pipeline.nodes.review import review_node
from backend.pipeline.nodes.test import test_node
from backend.pipeline.nodes.human_gate import human_gate_node
from backend.pipeline.nodes.escalate import escalate_node
from backend.pipeline.routes import route_human_decision, route_review_decision


# 条件边映射
HUMAN_GATE_ROUTES = {
    "human_gate_explore": {"approve": "plan", "reject": "explore", "abandon": END},
    "human_gate_plan": {"approve": "develop", "reject": "plan", "abandon": END},
    "human_gate_code": {"approve": "test", "reject": "develop", "abandon": END},
    "human_gate_test": {"approve": END, "reject": "develop", "abandon": END},
}

REVIEW_ROUTES = {
    "approve": "human_gate_code",
    "reject": "develop",
    "escalate": "escalate",
}


def build_pipeline_graph() -> StateGraph:
    """构建 Pipeline StateGraph.

    Returns:
        未编译的 StateGraph 实例.
    """
    builder = StateGraph(PipelineState)

    # 注册节点
    builder.add_node("explore", explore_node)
    builder.add_node("human_gate_explore", human_gate_node)
    builder.add_node("plan", plan_node)
    builder.add_node("human_gate_plan", human_gate_node)
    builder.add_node("develop", develop_node)
    builder.add_node("review", review_node)
    builder.add_node("human_gate_code", human_gate_node)
    builder.add_node("test", test_node)
    builder.add_node("human_gate_test", human_gate_node)
    builder.add_node("escalate", escalate_node)

    # 设置入口点
    builder.set_entry_point("explore")

    # 定义线性边
    builder.add_edge("explore", "human_gate_explore")
    builder.add_edge("plan", "human_gate_plan")
    builder.add_edge("develop", "review")
    builder.add_edge("test", "human_gate_test")
    builder.add_edge("escalate", END)

    # 定义人工门条件边
    builder.add_conditional_edges(
        "human_gate_explore",
        route_human_decision,
        HUMAN_GATE_ROUTES["human_gate_explore"],
    )
    builder.add_conditional_edges(
        "human_gate_plan",
        route_human_decision,
        HUMAN_GATE_ROUTES["human_gate_plan"],
    )
    builder.add_conditional_edges(
        "human_gate_code",
        route_human_decision,
        HUMAN_GATE_ROUTES["human_gate_code"],
    )
    builder.add_conditional_edges(
        "human_gate_test",
        route_human_decision,
        HUMAN_GATE_ROUTES["human_gate_test"],
    )

    # 定义 Review 条件边
    builder.add_conditional_edges(
        "review",
        route_review_decision,
        REVIEW_ROUTES,
    )

    return builder


async def compile_graph(
    postgres_uri: str,
) -> Any:
    """编译 StateGraph 并注入 AsyncPostgresSaver.

    Args:
        postgres_uri: PostgreSQL 连接字符串.

    Returns:
        编译后的 StateGraph 实例.
    """
    from backend.db.postgres import init_checkpointer

    saver = await init_checkpointer(postgres_uri)
    graph = build_pipeline_graph().compile(checkpointer=saver)
    return graph
