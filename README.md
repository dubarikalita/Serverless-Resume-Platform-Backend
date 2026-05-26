# Serverless Resume Platform — Backend

The serverless backend for the [Serverless Resume Platform](https://github.com/dubarikalita/Serverless-Resume-Platform). This repository contains the visitor counter API — a Python Lambda function connected to DynamoDB via API Gateway — along with the complete Infrastructure as Code definition using AWS SAM, unit tests, and an automated CI/CD pipeline via GitHub Actions.

---

## What This Project Does

Every time someone visits the resume site, the frontend JavaScript sends a `POST` request to this API. The API Gateway routes the request to a Python Lambda function, which atomically increments a counter in DynamoDB and returns the new count as JSON. The frontend then displays that number live on the page.

```
Browser JS (fetch POST)
        │
        ▼
API Gateway (/prod/count)       ← Public HTTPS endpoint
        │
        ▼
Lambda Function (Python 3.12)   ← Increments counter atomically
        │
        ▼
DynamoDB Table                  ← Stores { id: "visitor_count", count: N }
        │
        ▼
Returns { "count": N }          ← Back to the browser
```

---

## Architecture

```
GitHub (source control)
        │
        │  git push to main
        ▼
GitHub Actions CI/CD Pipeline
        │
        ├── Run pytest (unit tests)
        │     └── If any test fails → pipeline stops, nothing deploys
        │
        ├── SAM Build (packages Lambda)
        │
        └── SAM Deploy (CloudFormation)
                │
                ▼
        AWS CloudFormation Stack: serverless-resume-platform-backend
                ├── API Gateway (REST API, /count POST route, CORS)
                ├── Lambda Function (Python 3.12, counter.py)
                ├── DynamoDB Table (PAY_PER_REQUEST billing)
                └── IAM Role (least-privilege DynamoDB access)
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Runtime | Python 3.12 |
| Serverless compute | AWS Lambda |
| API layer | AWS API Gateway (REST) |
| Database | AWS DynamoDB |
| Infrastructure as Code | AWS SAM (Serverless Application Model) |
| Testing | pytest + unittest.mock |
| CI/CD | GitHub Actions |

---

## Repository Structure

```
Serverless-Resume-Platform-Backend/
├── template.yaml                   # SAM template — defines ALL AWS infrastructure
├── samconfig.toml                  # SAM deployment configuration
├── requirements.txt                # Python dependencies
├── lambda/
│   ├── counter.py                  # Lambda function — the actual business logic
│   └── test_counter.py             # Unit tests — must pass before any deploy
└── .github/
    └── workflows/
        └── deploy-backend.yml      # CI/CD pipeline
```

---

## Infrastructure as Code — template.yaml

All AWS resources are defined in `template.yaml`. Running `sam deploy` creates or updates every resource automatically. There is no manual console clicking required.

**Resources defined:**

| Resource | Type | Purpose |
|---|---|---|
| `VisitorCounterTable` | `AWS::DynamoDB::Table` | Stores the visitor count |
| `VisitorCounterFunction` | `AWS::Serverless::Function` | Python Lambda — increments counter |
| `VisitorCounterApi` | `AWS::Serverless::Api` | API Gateway with CORS configured |

---

## CI/CD Pipeline

Every push to `main` triggers `.github/workflows/deploy-backend.yml`.

**The pipeline has a hard test gate — if any test fails, SAM never runs:**

```
git push → GitHub Actions triggers
                │
                ▼
       1. Checkout code
       2. Set up Python 3.12
       3. Install dependencies (boto3, pytest)
       4. Run pytest ← GATE: failure stops everything here
                │
          all tests pass
                │
                ▼
       5. Set up SAM CLI
       6. Configure AWS credentials
       7. sam build
       8. sam deploy
                │
                ▼
     Infrastructure updated in ~60 seconds
```

---

## Unit Tests

Tests are in `lambda/test_counter.py`. They use `unittest.mock` to patch `boto3` so no real AWS connection is needed — tests run in under 1 second with zero AWS cost.

**Test coverage:**

| Test | What it checks |
|---|---|
| `test_counter_returns_200` | Lambda always returns HTTP 200 |
| `test_counter_returns_count` | Response body contains the correct count |
| `test_cors_headers_present` | CORS headers exist so the browser allows the call |
| `test_dynamodb_update_called` | DynamoDB `update_item` is actually invoked |
| `test_response_body_is_valid_json` | Response body is valid, parseable JSON |

**Run tests locally:**
```bash
cd lambda
pip install boto3 pytest
python -m pytest test_counter.py -v
```

Expected output:
```
test_counter.py::TestVisitorCounter::test_cors_headers_present PASSED
test_counter.py::TestVisitorCounter::test_counter_returns_200 PASSED
test_counter.py::TestVisitorCounter::test_counter_returns_count PASSED
test_counter.py::TestVisitorCounter::test_dynamodb_update_called PASSED
test_counter.py::TestVisitorCounter::test_response_body_is_valid_json PASSED

5 passed in 0.3s
```

---

## GitHub Secrets Required

These secrets must be set under **Settings → Secrets and variables → Actions**:

| Secret Name | Description |
|---|---|
| `AWS_ACCESS_KEY_ID` | IAM user access key |
| `AWS_SECRET_ACCESS_KEY` | IAM user secret key |
| `AWS_REGION` | AWS region (e.g. `ap-south-1`) |

---

## How to Deploy Manually

**Prerequisites:**
- AWS CLI installed and configured (`aws configure`)
- SAM CLI installed (`sam --version`)
- Python 3.12+

**Step 1 — Clone the repo:**
```bash
git clone https://github.com/dubarikalita/Serverless-Resume-Platform-Backend.git
cd Serverless-Resume-Platform-Backend
```

**Step 2 — Run tests:**
```bash
cd lambda
python -m pytest test_counter.py -v
cd ..
```

**Step 3 — Build:**
```bash
sam build
```

**Step 4 — Deploy:**
```bash
sam deploy
```

SAM will print the API endpoint URL in the Outputs section when done:
```
Outputs
──────────────────────────────────────────────────────────
Key    ApiEndpoint
Value  https://xxxxxxx.execute-api.ap-south-1.amazonaws.com/prod/count
```

**Step 5 — Seed the DynamoDB table:**
```bash
aws dynamodb put-item \
  --table-name serverless-resume-platform-counter \
  --item '{"id": {"S": "visitor_count"}, "count": {"N": "0"}}' \
  --region ap-south-1
```

---

## API Reference

### `POST /count`

Increments the visitor counter by 1 and returns the new value.

**Request:**
```
POST https://xxxxxxx.execute-api.ap-south-1.amazonaws.com/prod/count
Content-Type: application/json
```

**Response:**
```json
{
  "count": 42
}
```

**Status codes:**

| Code | Meaning |
|---|---|
| `200` | Success — counter incremented |
| `500` | Lambda execution error |

**Test it with curl:**
```bash
curl -X POST https://xxxxxxx.execute-api.ap-south-1.amazonaws.com/prod/count \
  -H "Content-Type: application/json"
```

---

## Tearing Down

To delete all AWS resources created by this project:

```bash
sam delete --stack-name serverless-resume-platform-backend --region ap-south-1
```

This removes the Lambda function, API Gateway, DynamoDB table, and IAM roles in one command. Nothing is left behind.

---

## Related Repository

| Repo | Description |
|---|---|
| [Serverless-Resume-Platform](https://github.com/dubarikalita/Serverless-Resume-Platform) | Frontend — HTML/CSS/JS resume hosted on S3 + CloudFront |

---

## Author

**dubarikalita**
- GitHub: [@dubarikalita](https://github.com/dubarikalita)
- Built as part of the Cloud Resume Challenge
