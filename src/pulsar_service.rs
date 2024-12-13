use std::sync::Arc;
use std::collections::HashMap;
use std::sync::RwLock;
use crate::data::{Pulsar, PulsarId, Email};
use crate::pulsar_controller::IPulsarService;

#[derive(Clone)]
pub struct PulsarService {
    pulsars: Arc<RwLock<HashMap<PulsarId, Pulsar>>>,
}

impl PulsarService {
    pub fn new() -> Self {
        Self {
            pulsars: Arc::new(RwLock::new(HashMap::<PulsarId, Pulsar>::new()))
        }
    }
}

impl IPulsarService for PulsarService {

    fn search_pulsar(&self, email: Email) -> Result<Vec<Pulsar>, String> {
        let pulsars = self.pulsars.read().unwrap();
        let user_pulsars = pulsars.iter().filter(|(_, pulsar)| pulsar.users.contains(&email)).map(|(_, pulsar)| pulsar.clone()).collect();
        Ok(user_pulsars)
    }

    fn create_pulsar(&self, users: Vec<Email>, pulsar_url: String) -> Result<Pulsar, String> {
        let new_pulsar = Pulsar::new(pulsar_url, users);
        let id = new_pulsar.id.unwrap();
        self.pulsars.write().unwrap().insert(id, new_pulsar.clone());
        Ok(new_pulsar)
    }

    fn get_pulsar(&self, _id: PulsarId) -> Result<Pulsar, String> {
        let pulsars = self.pulsars.read().unwrap();
        let maybe_pulsar = pulsars.get(&_id);
        match maybe_pulsar {
            Some(pulsar) => Ok(pulsar.clone()),
            None => Err("".to_string())
        }
    }

    fn delete_pulsar(&self, id: PulsarId) -> Result<(), String> {
        let maybe_pulsar = self.pulsars.write().unwrap().remove(&id);
        match maybe_pulsar {
            Some(_) => Ok(()),
            None => Err("".to_string())
        }
    }
}


#[cfg(test)]
mod tests {
use super::*;

fn setup() -> PulsarService {
    PulsarService::new()
}

fn create_test_email(id: u32) -> Email {
    format!("test{}@example.com", id)
}

#[test]
fn test_new_service_is_empty() {
    let service = setup();
    assert_eq!(service.pulsars.read().unwrap().len(), 0);
}

mod create_pulsar {
    use super::*;

    #[test]
    fn test_create_pulsar_success() {
        let service = setup();
        let users = vec![create_test_email(1)];
        let url = "pulsar1.example.com";

        let result = service.create_pulsar(users.clone(), url.to_string());
        assert!(result.is_ok());

        let pulsar = result.unwrap();
        assert_eq!(pulsar.pulsar_url, url);
        assert_eq!(pulsar.users, users);
        
        // Verify it was stored
        assert_eq!(service.pulsars.read().unwrap().len(), 1);
    }

    #[test]
    fn test_create_multiple_pulsars() {
        let service = setup();
        let users1 = vec![create_test_email(1)];
        let users2 = vec![create_test_email(2)];

        let pulsar1 = service.create_pulsar(users1, "pulsar1.example.com".to_string()).unwrap();
        let pulsar2 = service.create_pulsar(users2, "pulsar2.example.com".to_string()).unwrap();

        assert_ne!(pulsar1.id, pulsar2.id);
        assert_eq!(service.pulsars.read().unwrap().len(), 2);
    }
}

mod get_pulsar {
    use super::*;

    #[test]
    fn test_get_existing_pulsar() {
        let service = setup();
        let users = vec![create_test_email(1)];
        let created_pulsar = service.create_pulsar(users, "pulsar1.example.com".to_string()).unwrap();
        
        let result = service.get_pulsar(created_pulsar.id.unwrap());
        assert!(result.is_ok());
        
        let retrieved_pulsar = result.unwrap();
        assert_eq!(retrieved_pulsar.id, created_pulsar.id);
        assert_eq!(retrieved_pulsar.pulsar_url, created_pulsar.pulsar_url);
        assert_eq!(retrieved_pulsar.users, created_pulsar.users);
    }

    #[test]
    fn test_get_nonexistent_pulsar() {
        let service = setup();
        let result = service.get_pulsar(uuid::Uuid::now_v7());
        assert!(result.is_err());
    }
}

mod search_pulsar {
    use super::*;

    #[test]
    fn test_search_pulsar_with_results() {
        let service = setup();
        let user_email = create_test_email(1);
        let other_email = create_test_email(2);

        // Create two pulsars, one with our test user
        service.create_pulsar(vec![user_email.clone()], "pulsar1.example.com".to_string()).unwrap();
        service.create_pulsar(vec![other_email], "pulsar2.example.com".to_string()).unwrap();

        let results = service.search_pulsar(user_email).unwrap();
        assert_eq!(results.len(), 1);
        assert_eq!(results[0].pulsar_url, "pulsar1.example.com");
    }

    #[test]
    fn test_search_pulsar_no_results() {
        let service = setup();
        let user_email = create_test_email(1);
        let other_email = create_test_email(2);

        // Create a pulsar but with different user
        service.create_pulsar(vec![other_email], "pulsar1.example.com".to_string()).unwrap();

        let results = service.search_pulsar(user_email).unwrap();
        assert_eq!(results.len(), 0);
    }

    #[test]
    fn test_search_pulsar_multiple_results() {
        let service = setup();
        let user_email = create_test_email(1);

        // Create multiple pulsars for the same user
        service.create_pulsar(vec![user_email.clone()], "pulsar1.example.com".to_string()).unwrap();
        service.create_pulsar(vec![user_email.clone()], "pulsar2.example.com".to_string()).unwrap();

        let results = service.search_pulsar(user_email).unwrap();
        assert_eq!(results.len(), 2);
    }
}

mod delete_pulsar {
    use super::*;

    #[test]
    fn test_delete_existing_pulsar() {
        let service = setup();
        let users = vec![create_test_email(1)];
        let created_pulsar = service.create_pulsar(users, "pulsar1.example.com".to_string()).unwrap();
        
        let result = service.delete_pulsar(created_pulsar.id.unwrap());
        assert!(result.is_ok());
        
        // Verify it's gone
        assert_eq!(service.pulsars.read().unwrap().len(), 0);
    }

    #[test]
    fn test_delete_nonexistent_pulsar() {
        let service = setup();
        let result = service.delete_pulsar(uuid::Uuid::now_v7());
        assert!(result.is_err());
    }

    #[test]
    fn test_delete_already_deleted_pulsar() {
        let service = setup();
        let users = vec![create_test_email(1)];
        let created_pulsar = service.create_pulsar(users, "pulsar1.example.com".to_string()).unwrap();
        let pulsar_id = created_pulsar.id.unwrap();
        
        // Delete first time
        assert!(service.delete_pulsar(pulsar_id).is_ok());
        
        // Try to delete again
        let result = service.delete_pulsar(pulsar_id);
        assert!(result.is_err());
    }
}
}


