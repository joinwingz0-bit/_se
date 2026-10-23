use reqwest::StatusCode;
use rust_web_test_app::{create_app, AppState};
use serde_json::json;

// 啟動一個綁定隨機可用 Port 的測試伺服器
async fn spawn_test_server() -> String {
    let state = AppState::default();
    let app = create_app(state);

    let listener = tokio::net::TcpListener::bind("127.0.0.1:0")
        .await
        .expect("無法綁定隨機連接埠");
    let port = listener.local_addr().unwrap().port();

    tokio::spawn(async move {
        axum::serve(listener, app).await.unwrap();
    });

    format!("http://127.0.0.1:{}", port)
}

#[tokio::test]
async fn test_api_crud_flow() {
    let base_url = spawn_test_server().await;
    let client = reqwest::Client::new();

    // 1. POST /api/tasks (新增任務)
    let res = client
        .post(format!("{}/api/tasks", base_url))
        .json(&json!({ "title": "API 系統測試任務" }))
        .send()
        .await
        .unwrap();

    assert_eq!(res.status(), StatusCode::CREATED);
    let task: serde_json::Value = res.json().await.unwrap();
    assert_eq!(task["title"], "API 系統測試任務");
    let task_id = task["id"].as_u64().unwrap();

    // 2. GET /api/tasks (確認任務存在於清單)
    let res = client
        .get(format!("{}/api/tasks", base_url))
        .send()
        .await
        .unwrap();

    assert_eq!(res.status(), StatusCode::OK);
    let list: Vec<serde_json::Value> = res.json().await.unwrap();
    assert_eq!(list.len(), 1);
    assert_eq!(list[0]["id"], task_id);

    // 3. DELETE /api/tasks/:id (刪除任務)
    let res = client
        .delete(format!("{}/api/tasks/{}", base_url, task_id))
        .send()
        .await
        .unwrap();
    assert_eq!(res.status(), StatusCode::NO_CONTENT);

    // 4. GET /api/tasks (再次查詢，確認清單為空)
    let res = client
        .get(format!("{}/api/tasks", base_url))
        .send()
        .await
        .unwrap();
    let list_after: Vec<serde_json::Value> = res.json().await.unwrap();
    assert!(list_after.is_empty());
}

#[tokio::test]
async fn test_api_create_task_validation_error() {
    let base_url = spawn_test_server().await;
    let client = reqwest::Client::new();

    // 測試發送空內容，預期返回 400 Bad Request
    let res = client
        .post(format!("{}/api/tasks", base_url))
        .json(&json!({ "title": "   " }))
        .send()
        .await
        .unwrap();

    assert_eq!(res.status(), StatusCode::BAD_REQUEST);
}