use serde::{Deserialize, Serialize};
use uuid::Uuid;

#[derive(Clone, Serialize, Deserialize, Eq, PartialEq, Debug, Hash, Copy)]
pub struct PulsarId(Uuid);

impl PulsarId {
    pub fn new() -> Self {
        Self(Uuid::now_v7())
    }
}

#[derive(Clone, Serialize, Deserialize, Eq, PartialEq, Debug)]
pub struct Pulsar {
    pub id: Option<PulsarId>,
    pub pulsar_url: String,
    pub users: Vec<Email>,
}

impl Pulsar {
    pub fn new(pulsar_url: String, users: Vec<Email>) -> Self {
        let id = PulsarId::new();
        Self { id: Some(id), pulsar_url, users }
    }
}

#[derive(Clone, Serialize, Deserialize, Eq, PartialEq, Debug)]
pub struct Email(String);

#[derive(Debug)]
pub struct EmailValidationError;

impl std::error::Error for EmailValidationError {}

impl std::fmt::Display for EmailValidationError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "Invalid email")
    }
}

impl Email {
    pub fn new(email: &str) -> Result<Self, EmailValidationError> {
        if !Self::validate_email(email) {
            return Err(EmailValidationError{});
        }
        Ok(Self(email.to_string()))
    }

    fn validate_email(email: &str) -> bool {
        //validate without regex
        let email_parts: Vec<&str> = email.split('@').collect();
        if email_parts.len() != 2 {
            return false;
        }
        let domain = email_parts[1];
        let domain_parts: Vec<&str> = domain.split('.').collect();
        if domain_parts.len() < 2 {
            return false;
        }
        true
    }
}


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
        let users = vec![Email("test1@example.com".to_string())];
        let pulsar = Pulsar::new(url.to_string(), users.clone());
        assert_eq!(pulsar.pulsar_url, url);
        assert_eq!(pulsar.users, users);
    }

    #[test]
    fn test_invalid_domain() {
        let email = "test@example";
        let result = Email::new(email);
        assert!(result.is_err());
    }

    #[test]
    fn test_invalid_email() {
        let email = "testexample";
        let result = Email::new(email);
        assert!(result.is_err());
    }

    #[test]
    fn test_valid_email() {
        let email = "test@example.com";
        let result = Email::new(email);
        assert!(result.is_ok());
    }
}
}
