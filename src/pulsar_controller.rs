use axum::{http::StatusCode, extract::{Json, Query, Path, State}};
use crate::state::AppState;
use crate::data::{Pulsar, GetPulsar, CreatePulsar, SearchPulsar, DeletePulsar, PulsarId, Email};

// Regular trait definition without automock
pub trait IPulsarService {
    fn search_pulsar(&self, email: Email) -> Result<Vec<Pulsar>, String>;
    fn create_pulsar(&self, users: Vec<Email>, pulsar_url: String) -> Result<Pulsar, String>;
    fn get_pulsar(&self, _id: PulsarId) -> Result<Pulsar, String>;
    fn delete_pulsar(&self, id: PulsarId) -> Result<(), String>;
}


pub async fn get_pulsar(State(state): State<AppState>, Path(payload): Path<GetPulsar>) -> (StatusCode, Json<Option<Pulsar>>) {
    let pulsar = state.pulsar_service.get_pulsar(payload.id);
    match pulsar {
        Ok(pulsar) => (StatusCode::OK, Json(Some(pulsar))),
        Err(_) => (StatusCode::INTERNAL_SERVER_ERROR, Json(None)),
    }
}

pub async fn search_pulsar(State(state): State<AppState>, Query(payload): Query<SearchPulsar>) -> (StatusCode, Json<Option<Vec<Pulsar>>>) {
    let pulsars = state.pulsar_service.search_pulsar(payload.email);
    match pulsars {
        Ok(pulsars) => (StatusCode::OK, Json(Some(pulsars))),
        Err(_) => (StatusCode::INTERNAL_SERVER_ERROR, Json(None)),
    }
}

pub async fn create_pulsar(State(state): State<AppState>, Json(payload): Json<CreatePulsar>) -> (StatusCode, Json<Option<Pulsar>>) {
    match state.pulsar_service.create_pulsar(payload.users, payload.pulsar_url) {
        Ok(pulsar) => (StatusCode::CREATED, Json(Some(pulsar))),
        Err(_) => (StatusCode::INTERNAL_SERVER_ERROR, Json(None)),
    }
}

pub async fn delete_pulsar(State(state): State<AppState>, Path(payload): Path<DeletePulsar>) -> (StatusCode, ()) {
    match state.pulsar_service.delete_pulsar(payload.id) {
        Ok(_) => (StatusCode::NO_CONTENT, ()),
        Err(_) => (StatusCode::INTERNAL_SERVER_ERROR, ()),
    }
}

// Mock generation only in test configuration
#[cfg(test)]
mod test_utils {
    use super::*;
    use std::sync::Arc;

    mockall::mock! {
        pub PulsarService {}
        impl IPulsarService for PulsarService {
            fn search_pulsar(&self, email: Email) -> Result<Vec<Pulsar>, String>;
            fn create_pulsar(&self, users: Vec<Email>, pulsar_url: String) -> Result<Pulsar, String>;
            fn get_pulsar(&self, _id: PulsarId) -> Result<Pulsar, String>;
            fn delete_pulsar(&self, id: PulsarId) -> Result<(), String>;
        }
    }

    mod get_pulsar_tests {
        use super::*;

        #[tokio::test]
        async fn test_get_pulsar_success() {
            let mut mock_service = MockPulsarService::new();
            let pulsar = Pulsar::new("test.pulsar.com".to_string(), vec!["test@example.com".to_string()]);
            let payload = GetPulsar { id: pulsar.id.unwrap() };
            mock_service
                .expect_get_pulsar()
                .times(1)
                .return_once(move |_| Ok(pulsar.clone()));
            let state = AppState::new(Arc::new(mock_service));
            let (status, response) = get_pulsar(State(state), Path(payload)).await;
            assert_eq!(status, StatusCode::OK);
            assert_eq!(response.0.unwrap().pulsar_url, "test.pulsar.com");
        }
    }
}
