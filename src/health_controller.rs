pub async fn health() -> &'static str {
    "OK"
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_health() {
        let health = health().await;
        assert_eq!(health, "OK");
    }
}
