use axum::{Router, routing::{get, post, delete}};
use tower_http::{trace::TraceLayer, compression::CompressionLayer, limit::RequestBodyLimitLayer, validate_request::ValidateRequestHeaderLayer};
use std::sync::Arc;

mod pulsar_controller;
mod pulsar_service;
mod health_controller;
mod state;
mod data;

use pulsar_controller::{get_pulsar, search_pulsar, create_pulsar, delete_pulsar};
use pulsar_service::PulsarService;
use health_controller::health;
use state::AppState;

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
    let state = AppState::new(Arc::new(PulsarService::new()));

    let auth_token = get_auth_token().unwrap();
    let middleware = tower::ServiceBuilder::new()
        .layer(RequestBodyLimitLayer::new(4096))
        .layer(TraceLayer::new_for_http())
        .layer(CompressionLayer::new());
    let auth_middleware = tower::ServiceBuilder::new()
        .layer(ValidateRequestHeaderLayer::bearer(auth_token.as_str()));

    let app = Router::new()
        .route("/api/pulsar", get(search_pulsar))
        .route("/api/pulsar", post(create_pulsar))
        .route("/api/pulsar/:id", get(get_pulsar))
        .route("/api/pulsar/:id", delete(delete_pulsar))
        .layer(auth_middleware)
        .route("/api/pulsar/health", get(health))
        .layer(middleware)
        .with_state(state);
    
    let listener = tokio::net::TcpListener::bind("0.0.0.0:3456").await.unwrap();
    println!("Listening on http://0.0.0.0:3456");
    axum::serve(listener, app).await.unwrap();
}

