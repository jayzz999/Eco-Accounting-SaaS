# Enable AWS Bedrock Model Access

**Important**: You need to manually enable Bedrock model access through the AWS Console.

## Steps:

1. **Go to AWS Console**: https://console.aws.amazon.com/bedrock/

2. **Navigate to Model Access**:
   - Click "Model access" in the left sidebar
   - Or go directly to: https://us-east-1.console.aws.amazon.com/bedrock/home?region=us-east-1#/modelaccess

3. **Request Model Access**:
   - Click "Manage model access" (orange button)
   - Scroll down to "Anthropic" section
   - Check the box next to:
     - ✅ **Claude 3 Sonnet**
     - ✅ **Claude 3 Haiku** (optional, cheaper for simple tasks)
   - Click "Request model access" button

4. **Wait for Approval**:
   - Usually instant (< 1 minute)
   - Status will change from "Not available" to "Access granted"
   - You'll see a green checkmark

5. **Verify Access**:
   ```bash
   aws bedrock list-foundation-models --region us-east-1 --query 'modelSummaries[?contains(modelId, `anthropic.claude-3-sonnet`)]'
   ```

## Alternative: Use AWS CLI (if permissions allow)

If you have admin access, you can try this command:
```bash
aws bedrock-runtime invoke-model \
  --model-id anthropic.claude-3-sonnet-20240229-v1:0 \
  --region us-east-1 \
  --body '{"anthropic_version":"bedrock-2023-05-31","max_tokens":100,"messages":[{"role":"user","content":"Hello"}]}' \
  output.txt
```

If this works without permission errors, you're all set!

## Troubleshooting

**Error: AccessDeniedException**
- Your IAM user needs the `AmazonBedrockFullAccess` policy
- Or add this inline policy to your user:
  ```json
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream",
          "bedrock:ListFoundationModels"
        ],
        "Resource": "*"
      }
    ]
  }
  ```

**Model not available in your region**
- Bedrock Claude is available in: us-east-1, us-west-2, eu-west-1, ap-southeast-1
- Make sure you're checking the correct region in the console

## Once Enabled

Come back and restart your backend server:
```bash
cd backend
source venv/bin/activate
python main.py
```

The application will now have full AI capabilities! 🎉
