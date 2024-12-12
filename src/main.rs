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

async fn key() -> String {
    get_auth_token().unwrap()
}

// get auth_token from PULSAR_REGISTRY_KEY env var
fn get_auth_token() -> Result<String, String> {
    let key = std::env::var("PULSAR_REGISTRY_KEY").unwrap();
    if key.is_empty() {
        Err("PULSAR_REGISTRY_KEY is empty".to_string())
    } else {
        Ok(key)
    }
}

#[tokio::main]
async fn main() {
    let app = Router::new()
        .route("/api/pulsar/health", get(health))
        .route("/api/pulsar/key", get(key));
    let listener = tokio::net::TcpListener::bind("0.0.0.0:3456").await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
