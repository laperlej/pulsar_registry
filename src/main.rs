use axum::{Router, routing::get};

type Email = String;

struct RegisterPulsarRequest {
    users: Vec<Email>,
    pulsar_url: String,
}

struct RoutingRequest {
    user: Email,
}

struct RoutingResponse {
    pulsar_url: String,
}

async fn register() -> &'static str {
    "Hello, World!"
}

async fn routing() -> &'static str {
    "Hello, World!"
}


#[tokio::main]
async fn main() {
    let app = Router::new()
        .route("/register", get(register))
        .route("/routing", get(routing));
    let listener = tokio::net::TcpListener::bind("0.0.0.0:3456").await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
