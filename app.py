import boto3
import botocore.config
import json
from datetime import datetime

def blog_generate_using_bedrock(blogtopic: str) -> str:
    """
    Generates a 200-word blog using Amazon Titan Text Lite on AWS Bedrock.
    """
    body = {
        "inputText": f"Write a 200-word blog on the topic: {blogtopic}.",
        "textGenerationConfig": {
            "maxTokenCount": 512,
            "temperature": 0.7,
            "topP": 0.9
        }
    }

    try:
        print("🔹 Initializing Bedrock client...")
        bedrock = boto3.client(
            "bedrock-runtime",
            region_name="us-east-1",
            config=botocore.config.Config(
                read_timeout=30,      # Increase read timeout
                connect_timeout=10,   # Reasonable connect timeout
                retries={'max_attempts': 3}
            )
        )

        print("🔹 Sending request to Amazon Titan Text Lite model...")
        response = bedrock.invoke_model(
            modelId="amazon.titan-text-lite-v1",  # On-demand model
            contentType="application/json",
            accept="application/json",
            body=json.dumps(body)
        )

        print("✅ Response received from Bedrock. Parsing...")
        response_content = response.get('body').read()
        response_data = json.loads(response_content)
        print("🔹 Full response data:", response_data)

        # Extract generated text
        blog_details = response_data.get('results', [{}])[0].get('outputText', "")
        return blog_details

    except Exception as e:
        print(f"❌ Error generating the blog: {e}")
        return ""

def save_blog_details_s3(s3_key, s3_bucket, generate_blog):
    """
    Saves the generated blog to an S3 bucket.
    """
    s3 = boto3.client('s3')
    try:
        print("🔹 Uploading blog to S3...")
        response = s3.put_object(Bucket=s3_bucket, Key=s3_key, Body=generate_blog)
        print(f"✅ Blog saved to S3. Response: {response}")
    except Exception as e:
        print(f"❌ Error saving blog to S3: {e}")

def lambda_handler(event, context):
    """
    AWS Lambda handler to generate a blog and store it in S3.
    Expects a JSON body with "blog_topic".
    """
    try:
        print("🔹 Parsing event body...")
        event_body = json.loads(event['body'])
        blogtopic = event_body.get('blog_topic', '')

        if not blogtopic:
            print("❌ Missing 'blog_topic' in request")
            return {
                'statusCode': 400,
                'body': json.dumps("Missing 'blog_topic' in request")
            }

        print(f"🔹 Received blog topic: {blogtopic}")
        generate_blog = blog_generate_using_bedrock(blogtopic)

        if generate_blog:
            current_time = datetime.now().strftime('%H%M%S')
            s3_key = f"blog-output/{current_time}.txt"
            s3_bucket = 'awsbedrockhardik'
            save_blog_details_s3(s3_key, s3_bucket, generate_blog)
        else:
            print("⚠ No blog was generated")

        return {
            'statusCode': 200,
            'body': json.dumps('✅ Blog Generation is completed')
        }

    except Exception as e:
        print(f"❌ Lambda function error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps("Internal Server Error")
        }
