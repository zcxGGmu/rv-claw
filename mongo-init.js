"""MongoDB 初始化脚本.

TODO: 创建 contribution_cases, human_reviews, audit_log, stage_outputs 集合及验证器.
参考 progress.md P0.5.1 和 design.md §6.1.
"""

// contribution_cases 集合 + 验证器
db.createCollection("contribution_cases", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["title", "status", "target_repo", "created_at", "updated_at"],
      properties: {
        _id: { bsonType: "string" },
        title: { bsonType: "string" },
        status: {
          enum: [
            "created", "exploring", "pending_explore_review",
            "planning", "pending_plan_review",
            "developing", "reviewing", "pending_code_review",
            "testing", "pending_test_review",
            "completed", "abandoned", "escalated"
          ]
        },
        target_repo: { bsonType: "string" },
        input_context: { bsonType: "object" },
        exploration_result: { bsonType: "object" },
        execution_plan: { bsonType: "object" },
        development_result: { bsonType: "object" },
        review_verdict: { bsonType: "object" },
        test_result: { bsonType: "object" },
        review_iterations: { bsonType: "int" },
        cost: {
          bsonType: "object",
          properties: {
            input_tokens: { bsonType: "int" },
            output_tokens: { bsonType: "int" },
            estimated_usd: { bsonType: "double" }
          }
        },
        created_by: { bsonType: "string" },
        created_at: { bsonType: "date" },
        updated_at: { bsonType: "date" },
        abandoned_at: { bsonType: "date" }
      }
    }
  }
})

// human_reviews 集合
db.createCollection("human_reviews")

// audit_log 集合
db.createCollection("audit_log")

// stage_outputs 集合
db.createCollection("stage_outputs")

// 创建索引
db.contribution_cases.createIndex({ status: 1, created_at: -1 })
db.contribution_cases.createIndex({ target_repo: 1 })
db.contribution_cases.createIndex({ created_by: 1 })
db.contribution_cases.createIndex(
  { abandoned_at: 1 },
  { expireAfterSeconds: 7776000, partialFilterExpression: { status: "abandoned" } }
)

db.human_reviews.createIndex({ case_id: 1, created_at: -1 })
db.audit_log.createIndex({ case_id: 1, timestamp: -1 })
db.audit_log.createIndex({ timestamp: 1 }, { expireAfterSeconds: 63072000 })
