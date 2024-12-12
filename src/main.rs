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

async fn health() -> &'static str {
    "OK"
}


#[tokio::main]
async fn main() {
    let app = Router::new()
        .route("/api/pulsar/health", get(health));
    let listener = tokio::net::TcpListener::bind("0.0.0.0:3456").await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
