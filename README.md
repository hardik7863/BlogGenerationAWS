# Blog Generation using AWS Lambda, Bedrock, and S3

## 📌 Overview
This project is an **end-to-end Generative AI application** that generates blog posts using **AWS Bedrock (Amazon Titan Text Lite model)**, **AWS Lambda**, and **Amazon S3**. The API is exposed through **Amazon API Gateway**, and Postman is used for testing API requests.

## 🔧 Tech Stack
- **AWS Lambda**: Executes the blog generation logic.
- **Amazon Bedrock**: Provides the foundation model (**Amazon Titan Text Lite**) for text generation.
- **Amazon S3**: Stores the generated blog text files.
- **Amazon API Gateway**: Exposes a REST API to trigger the Lambda function.
- **Postman**: Used for testing the API requests.
- **Python (Boto3 SDK)**: Used to interact with AWS services.

---

### 🔹 Flow Explanation
1. **User sends a POST request** to the API Gateway endpoint with a JSON body containing a blog topic.
2. **API Gateway triggers AWS Lambda**, which processes the request.
3. **Lambda invokes Amazon Bedrock’s Titan Text Lite model**, passing the blog topic as input.
4. **Bedrock returns a generated blog** based on the input topic.
5. **Lambda saves the generated blog text in Amazon S3**.
6. **Lambda responds to API Gateway**, which then returns a success message to Postman.

---

## 🚀 Getting Started

### 1️⃣ **Set Up AWS Services**
Before running the project, ensure the following AWS services are set up:
- **Create an API Gateway**:
  - **Method:** `POST`
  - **Endpoint:** `/blog-generation`
  - **Integration:** AWS Lambda
- **Create a Lambda Function**:
  - Attach **Boto3 layer**
  - Use the provided Python script
- **Configure S3 Bucket**:
  - Create a bucket named `awsbedrockhardik`
  - Ensure your Lambda has `s3:PutObject` permissions
- **Enable Amazon Bedrock**:
  - Use the **Amazon Titan Text Lite** model (`amazon.titan-text-lite-v1`)

### 2️⃣ **Deploy Lambda Code**
- Install AWS CLI & configure credentials:
  ```sh
  aws configure
  ```
- Deploy the Python code to your Lambda function.

### 3️⃣ **Test API with Postman**
- **Endpoint:** `https://your-api-id.execute-api.us-east-1.amazonaws.com/dev/blog-generation`
- **Method:** `POST`
- **Headers:**
  ```json
  { "Content-Type": "application/json" }
  ```
- **Body (Raw JSON):**
  ```json
  {
    "blog_topic": "Generative AI"
  }
  ```
- **Expected Response:**
  ```json
  "✅ Blog Generation is completed"
  ```
- Check **S3 Bucket (`awsbedrockhardik`)** to find the generated blog.

---

## 📜 Lambda Code
```python
import boto3
import botocore.config
import json
from datetime import datetime

def blog_generate_using_bedrock(blogtopic: str) -> str:
    body = {
        "inputText": f"Write a 200-word blog on the topic: {blogtopic}.",
        "textGenerationConfig": {
            "maxTokenCount": 512,
            "temperature": 0.7,
            "topP": 0.9
        }
    }
    
    try:
        bedrock = boto3.client("bedrock-runtime", region_name="us-east-1",
            config=botocore.config.Config(read_timeout=30, connect_timeout=10, retries={'max_attempts': 3}))
        response = bedrock.invoke_model(
            modelId="amazon.titan-text-lite-v1",
            contentType="application/json",
            accept="application/json",
            body=json.dumps(body)
        )
        response_content = response.get('body').read()
        response_data = json.loads(response_content)
        return response_data.get('results', [{}])[0].get('outputText', "")
    except Exception as e:
        print(f"❌ Error generating blog: {e}")
        return ""

def save_blog_details_s3(s3_key, s3_bucket, generate_blog):
    s3 = boto3.client('s3')
    try:
        s3.put_object(Bucket=s3_bucket, Key=s3_key, Body=generate_blog)
        print("✅ Blog saved to S3")
    except Exception as e:
        print(f"❌ Error saving blog to S3: {e}")

def lambda_handler(event, context):
    try:
        event_body = json.loads(event['body'])
        blogtopic = event_body.get('blog_topic', '')
        if not blogtopic:
            return {'statusCode': 400, 'body': json.dumps("Missing 'blog_topic' in request")}
        generate_blog = blog_generate_using_bedrock(blogtopic)
        if generate_blog:
            current_time = datetime.now().strftime('%H%M%S')
            s3_key = f"blog-output/{current_time}.txt"
            s3_bucket = 'awsbedrockhardik'
            save_blog_details_s3(s3_key, s3_bucket, generate_blog)
        return {'statusCode': 200, 'body': json.dumps('✅ Blog Generation is completed')}
    except Exception as e:
        print(f"❌ Lambda function error: {e}")
        return {'statusCode': 500, 'body': json.dumps("Internal Server Error")}
```

---

## 🔥 Key Features
✅ **Serverless & Scalable**: No infrastructure management required. Pay only for execution time.  
✅ **On-Demand AI Content Generation**: Uses **Amazon Titan Text Lite** for high-quality text.  
✅ **Secure Storage**: Blogs are automatically stored in **Amazon S3** for retrieval.  
✅ **Easy API Integration**: API Gateway allows seamless integration with web apps.  
✅ **Low Latency**: Optimized with a proper timeout and retry mechanism.

---

