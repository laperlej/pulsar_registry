use serde::{Deserialize, Serialize};
use uuid::Uuid;

pub type PulsarId = Uuid;

#[derive(Clone, Serialize, Deserialize, Eq, PartialEq, Debug)]
pub struct Pulsar {
    pub id: Option<PulsarId>,
    pub pulsar_url: String,
    pub users: Vec<Email>,
}

impl Pulsar {
    pub fn new(pulsar_url: String, users: Vec<Email>) -> Self {
        let id = Uuid::now_v7();
        Self { id: Some(id), pulsar_url, users }
    }
}

pub type Email = String;

#[derive(Deserialize)]
pub struct CreatePulsar {
    pub users: Vec<Email>,
    pub pulsar_url: String,
}

#[derive(Deserialize)]
pub struct GetPulsar {
    pub id: PulsarId,
}

#[derive(Deserialize)]
pub struct SearchPulsar {
    pub email: Email,
}

#[derive(Deserialize)]
pub struct DeletePulsar {
    pub id: PulsarId,
}

#[cfg(test)]
mod tests {
use super::*;

mod new_pulsar {
    use super::*;

    #[test]
    fn test_new_pulsar() {
        let url = "pulsar1.example.com";
        let users = vec!["test1@example.com".to_string()];
        let pulsar = Pulsar::new(url.to_string(), users.clone());
        assert_eq!(pulsar.pulsar_url, url);
        assert_eq!(pulsar.users, users);
    }
}
}
