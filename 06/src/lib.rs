pub mod models;

use axum::{
    extract::{Path, State},
    http::StatusCode,
    response::IntoResponse,
    routing::{delete, get, post},
    Json, Router,
};
use models::{validate_task_title, CreateTaskInput, Task};
use std::sync::{Arc, Mutex};
use tower_http::services::ServeDir;

#[derive(Clone, Default)]
pub struct AppState {
    pub tasks: Arc<Mutex<Vec<Task>>>,
    pub next_id: Arc<Mutex<u64>>,
}

pub fn create_app(state: AppState) -> Router {
    let api_routes = Router::new()
        .route("/tasks", get(get_tasks))
        .route("/tasks", post(create_task))
        .route("/tasks/:id", delete(delete_task))
        .with_state(state);

    Router::new()
        .nest("/api", api_routes)
        .fallback_service(ServeDir::new("static"))
}

async fn get_tasks(State(state): State<AppState>) -> Json<Vec<Task>> {
    let tasks = state.tasks.lock().unwrap();
    Json(tasks.clone())
}

async fn create_task(
    State(state): State<AppState>,
    Json(payload): Json<CreateTaskInput>,
) -> Result<(StatusCode, Json<Task>), (StatusCode, &'static str)> {
    let valid_title = validate_task_title(&payload.title)
        .map_err(|err| (StatusCode::BAD_REQUEST, err))?;

    let mut tasks = state.tasks.lock().unwrap();
    let mut id_counter = state.next_id.lock().unwrap();
    *id_counter += 1;

    let new_task = Task {
        id: *id_counter,
        title: valid_title,
    };
    tasks.push(new_task.clone());

    Ok((StatusCode::CREATED, Json(new_task)))
}

async fn delete_task(
    State(state): State<AppState>,
    Path(id): Path<u64>,
) -> impl IntoResponse {
    let mut tasks = state.tasks.lock().unwrap();
    let before_len = tasks.len();
    tasks.retain(|t| t.id != id);

    if tasks.len() < before_len {
        StatusCode::NO_CONTENT
    } else {
        StatusCode::NOT_FOUND
    }
}