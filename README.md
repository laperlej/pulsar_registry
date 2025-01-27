# Pulsar API Documentation

## Authentication

All endpoints except `/health` require Bearer token authentication using header:

```
Authorization: Bearer PULSAR_REGISTRY_KEY
```

## Endpoints

### Health Check

```
GET /api/pulsar/health
```

Simple health check endpoint to verify API availability.

### Create Pulsar

```
POST /api/pulsar
```

Creates a new pulsar instance.

**Request Body:**

```json
{
  "url": "string",
  "api_key": "string",
  "users": ["email@domain.com"]
}
```

**Response:** Returns created pulsar ID with status 201

### Get Pulsar

```
GET /api/pulsar/{id}
```

Retrieves specific pulsar details by ID.

**Response:** Returns full pulsar object with status 200

### Search Pulsar

```
GET /api/pulsar?user={email}
```

Searches for pulsars by user email.

**Response:** Returns array of matching pulsar objects with status 200

### Update Pulsar

```
PUT /api/pulsar/{id}
```

Updates existing pulsar configuration.

**Request Body:**

```json
{
  "url": "string",
  "api_key": "string",
  "users": ["email@domain.com"]
}
```

**Response:** Returns updated pulsar ID with status 200

### Delete Pulsar

```
DELETE /api/pulsar/{id}
```

Removes a pulsar instance.

**Response:** Returns 204 No Content on success

All error responses will return appropriate HTTP status codes with error details.
