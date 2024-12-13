use std::sync::Arc;
use crate::pulsar_controller::IPulsarService;

#[derive(Clone)]
pub struct AppState {
    pub pulsar_service: Arc<dyn IPulsarService + Send + Sync>,
}

impl AppState {
    pub fn new(pulsar_service: Arc<dyn IPulsarService + Send + Sync>) -> Self {
        Self { pulsar_service }
    }
}

#[cfg(test)]
mod tests {
use super::*;

mod new_app_state {
    use super::*;
    use crate::pulsar_service::PulsarService;
    #[test]
    fn test_new_app_state() {
        let service = PulsarService::new();
        let _ = AppState::new(Arc::new(service));
    }
}
}
