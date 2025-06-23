# AWS Cost Calculation for Fraud Detection and Prevention (FDP) Agentic Platform

## Executive Summary

This document provides a comprehensive cost calculation for the Fraud Detection and Prevention (FDP) Agentic Platform. The calculation includes all AWS services used in the solution, with estimates based on typical usage patterns for fraud detection systems.

The total estimated monthly cost for the solution is **$1,500 - $3,000** depending on usage volume and specific configuration choices. The primary cost drivers are Amazon Bedrock (for AI/ML capabilities), Lambda functions (for backend processing), and DynamoDB (for data storage).

## AWS Services Used

Based on the infrastructure code analysis, the solution uses the following AWS services:

1. **Amazon Bedrock** - AI/ML foundation models for document analysis and fraud detection
2. **AWS Lambda** - Serverless compute for backend microservices
3. **Amazon DynamoDB** - NoSQL database for storing verification data and results
4. **Amazon API Gateway** - REST API endpoints for frontend-backend communication
5. **Amazon S3** - Storage for documents and static website hosting
6. **Amazon CloudFront** - Content delivery network for frontend
7. **Amazon Cognito** - User authentication and authorization
8. **AWS WAF** - Web application firewall for security
9. **Amazon SQS** - Message queuing for Lambda dead letter queues
10. **Amazon CloudWatch** - Monitoring and logging

## Assumptions

The cost calculation is based on the following assumptions:

1. **Usage Volume**:
   - 1,000 document verifications per day (~30,000 per month)
   - 100 active users accessing the system daily
   - Average document size of 2MB

2. **Regional Deployment**:
   - Primary deployment in US East (N. Virginia) region
   - No multi-region replication (though the infrastructure supports it)

3. **Operational Patterns**:
   - 24/7 availability
   - Typical business hours peak usage (9 AM - 5 PM)
   - 80% of traffic during business hours

4. **Data Transfer**:
   - Minimal cross-region data transfer
   - Most traffic between services within the same region

5. **Retention Policies**:
   - Document storage for 90 days
   - Logs retained for 30 days

## Detailed Cost Breakdown

### Amazon Bedrock

Amazon Bedrock is used for document analysis and fraud detection using the Amazon Nova Lite model.

- **Nova Lite model**: $0.0003 per 1K input tokens, $0.0004 per 1K output tokens
- **Average tokens per verification**: ~4,000 input tokens, ~1,000 output tokens
- **Monthly cost**: 30,000 verifications × (4,000 × $0.0003/1K + 1,000 × $0.0004/1K) = **$48 + $12 = $60**

### AWS Lambda

Lambda functions handle the backend processing for document verification, agent management, and configuration.

- **Average execution**: 5 Lambda functions × 1,024 MB × 5 seconds per verification
- **Monthly invocations**: 30,000 verifications × 5 functions = 150,000 invocations
- **Compute cost**: 150,000 invocations × 5 seconds × 1,024 MB × $0.0000166667 per GB-second = **$12.80**
- **Request cost**: 150,000 invocations × $0.0000002 per request = **$0.03**
- **Total Lambda cost**: **$12.83**

### Amazon DynamoDB

DynamoDB stores verification data, agent configurations, and results.

- **Storage**: 10 GB of data × $0.25 per GB = **$2.50**
- **Read capacity**: 30 RCU × 24 hours × 30 days × $0.00013 per RCU-hour = **$2.81**
- **Write capacity**: 30 WCU × 24 hours × 30 days × $0.00065 per WCU-hour = **$14.04**
- **Total DynamoDB cost**: **$19.35**

### Amazon API Gateway

API Gateway provides REST API endpoints for the frontend to communicate with the backend.

- **API calls**: 100,000 API calls per month
- **Cost**: 100,000 calls × $3.50 per million calls = **$0.35**
- **Data transfer**: Minimal, included in the free tier

### Amazon S3

S3 stores documents for verification and hosts the static website.

- **Storage**: 30,000 documents × 2 MB × 3 months retention = 180 GB × $0.023 per GB = **$4.14**
- **PUT/COPY/POST/LIST requests**: 30,000 × $0.005 per 1,000 requests = **$0.15**
- **GET requests**: 100,000 × $0.0004 per 1,000 requests = **$0.04**
- **Total S3 cost**: **$4.33**

### Amazon CloudFront

CloudFront delivers the frontend application to users.

- **Data transfer**: 100 users × 5 MB per session × 30 days = 15 GB × $0.085 per GB = **$1.28**
- **HTTP/HTTPS requests**: 100,000 requests × $0.0075 per 10,000 = **$0.08**
- **Total CloudFront cost**: **$1.36**

### Amazon Cognito

Cognito handles user authentication and authorization.

- **Monthly active users**: 100 users
- **Cost**: 100 users × $0.0055 per MAU = **$0.55**

### AWS WAF

WAF protects the application from common web exploits.

- **Web ACLs**: 1 × $5.00 per month = **$5.00**
- **Rule evaluations**: 100,000 requests × $0.60 per million = **$0.06**
- **Total WAF cost**: **$5.06**

### Amazon SQS

SQS is used for Lambda dead letter queues.

- **Standard queue requests**: 1,000 messages × $0.40 per million = **$0.0004**
- **Cost is negligible**

### Amazon CloudWatch

CloudWatch monitors the application and stores logs.

- **Dashboard**: 1 × $3.00 per month = **$3.00**
- **Logs**: 5 GB × $0.50 per GB = **$2.50**
- **Metrics**: 10 custom metrics × $0.30 per metric = **$3.00**
- **Total CloudWatch cost**: **$8.50**

## Total Monthly Cost

| Service | Monthly Cost |
|---------|--------------|
| Amazon Bedrock | $60.00 |
| AWS Lambda | $12.83 |
| Amazon DynamoDB | $19.35 |
| Amazon API Gateway | $0.35 |
| Amazon S3 | $4.33 |
| Amazon CloudFront | $1.36 |
| Amazon Cognito | $0.55 |
| AWS WAF | $5.06 |
| Amazon SQS | $0.00 |
| Amazon CloudWatch | $8.50 |
| **Total** | **$112.33** |

## Scaling Considerations

The above calculation represents a baseline for the described usage pattern. Costs will scale with usage:

1. **Linear Scaling Components**:
   - Bedrock costs scale linearly with the number of document verifications
   - Lambda costs scale linearly with invocations
   - S3 storage scales with document volume and retention period

2. **Non-Linear Scaling Components**:
   - DynamoDB can have step increases when provisioned capacity is increased
   - CloudFront costs may benefit from economies of scale with higher traffic

## Cost Optimization Recommendations

1. **Amazon Bedrock**:
   - Optimize prompts to reduce token usage
   - Consider batching document analysis where possible
   - Evaluate if lower-cost models can meet accuracy requirements

2. **AWS Lambda**:
   - Optimize memory allocation based on function requirements
   - Reduce function duration through code optimization
   - Consider using provisioned concurrency for predictable workloads

3. **Amazon DynamoDB**:
   - Use on-demand capacity for unpredictable workloads
   - Implement TTL for automatic data cleanup
   - Consider DAX for read-heavy workloads

4. **Storage**:
   - Implement lifecycle policies to move older documents to lower-cost storage tiers
   - Compress documents before storage
   - Review retention policies regularly

5. **General**:
   - Use AWS Cost Explorer to identify cost anomalies
   - Set up budgets and alerts to monitor spending
   - Consider Reserved Instances or Savings Plans for predictable workloads

## Conclusion

The Fraud Detection and Prevention (FDP) Agentic Platform has been designed with cost efficiency in mind, leveraging serverless technologies where possible to minimize fixed costs. The estimated monthly cost of $112.33 represents a baseline configuration that can scale with usage.

For high-volume deployments processing hundreds of thousands of documents monthly, costs could increase to $1,500 - $3,000 per month, with Amazon Bedrock being the primary cost driver. Implementing the recommended cost optimization strategies can help manage these costs effectively.

This cost calculation should be reviewed periodically as usage patterns evolve and AWS pricing changes.
