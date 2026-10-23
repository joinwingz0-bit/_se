use rust_web_test_app::{create_app, AppState};

#[tokio::main]
async fn main() {
    let state = AppState::default();
    let app = create_app(state);

    let addr = "127.0.0.1:3000";
    let listener = tokio::net::TcpListener::bind(addr).await.unwrap();
    println!("Server running on http://{}", addr);

    axum::serve(listener, app).await.unwrap();
}