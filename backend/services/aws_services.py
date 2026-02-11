"""
AWS service integrations (S3, Textract, Bedrock)
"""
import boto3
import json
from typing import Dict, Optional, List
from datetime import datetime
import os


class S3Service:
    """AWS S3 service for file storage"""

    def __init__(self, bucket_name: str, region: str = "us-east-1"):
        self.bucket_name = bucket_name
        self.region = region
        self.s3_client = boto3.client('s3', region_name=region)

    def upload_file(self, file_content: bytes, key: str, metadata: Optional[Dict] = None) -> str:
        """
        Upload file to S3

        Args:
            file_content: File content as bytes
            key: S3 object key
            metadata: Optional metadata dict

        Returns:
            S3 object URL
        """
        extra_args = {}
        if metadata:
            extra_args['Metadata'] = metadata

        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=file_content,
            **extra_args
        )

        return f"s3://{self.bucket_name}/{key}"

    def download_file(self, key: str) -> bytes:
        """Download file from S3"""
        response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
        return response['Body'].read()

    def generate_presigned_url(self, key: str, expiration: int = 3600) -> str:
        """Generate presigned URL for file access"""
        url = self.s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket_name, 'Key': key},
            ExpiresIn=expiration
        )
        return url

    def delete_file(self, key: str):
        """Delete file from S3"""
        self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)


class TextractService:
    """AWS Textract service for OCR"""

    def __init__(self, region: str = "us-east-1"):
        self.region = region
        self.textract_client = boto3.client('textract', region_name=region)

    def extract_text(self, file_content: bytes, feature_types: Optional[List[str]] = None) -> Dict:
        """
        Extract text from document using Textract

        Args:
            file_content: Document content as bytes
            feature_types: Optional list of features to extract (TABLES, FORMS)

        Returns:
            Extraction results dict
        """
        if feature_types is None:
            feature_types = ['FORMS', 'TABLES']

        response = self.textract_client.analyze_document(
            Document={'Bytes': file_content},
            FeatureTypes=feature_types
        )

        return self._parse_textract_response(response)

    def _parse_textract_response(self, response: Dict) -> Dict:
        """
        Parse Textract response into structured format

        Returns:
            Dict with extracted text, forms, and tables
        """
        result = {
            'raw_text': '',
            'forms': {},
            'tables': [],
            'confidence': 0,
            'blocks': []
        }

        blocks = response.get('Blocks', [])

        # Extract raw text
        text_blocks = [block for block in blocks if block['BlockType'] == 'LINE']
        result['raw_text'] = '\n'.join([block.get('Text', '') for block in text_blocks])

        # Calculate average confidence
        confidences = [block.get('Confidence', 0) for block in blocks if 'Confidence' in block]
        if confidences:
            result['confidence'] = sum(confidences) / len(confidences)

        # Extract key-value pairs (forms)
        key_map = {}
        value_map = {}
        block_map = {block['Id']: block for block in blocks}

        for block in blocks:
            if block['BlockType'] == 'KEY_VALUE_SET':
                if 'KEY' in block.get('EntityTypes', []):
                    key_map[block['Id']] = block
                elif 'VALUE' in block.get('EntityTypes', []):
                    value_map[block['Id']] = block

        for key_id, key_block in key_map.items():
            key_text = self._get_text_from_block(key_block, block_map)

            # Find associated value
            if 'Relationships' in key_block:
                for relationship in key_block['Relationships']:
                    if relationship['Type'] == 'VALUE':
                        for value_id in relationship['Ids']:
                            if value_id in value_map:
                                value_text = self._get_text_from_block(value_map[value_id], block_map)
                                result['forms'][key_text] = value_text

        # Extract tables
        tables = [block for block in blocks if block['BlockType'] == 'TABLE']
        for table in tables:
            table_data = self._parse_table(table, block_map)
            result['tables'].append(table_data)

        return result

    def _get_text_from_block(self, block: Dict, block_map: Dict) -> str:
        """Extract text from a block"""
        text = ''
        if 'Relationships' in block:
            for relationship in block['Relationships']:
                if relationship['Type'] == 'CHILD':
                    for child_id in relationship['Ids']:
                        child = block_map.get(child_id)
                        if child and child.get('BlockType') == 'WORD':
                            text += child.get('Text', '') + ' '
        return text.strip()

    def _parse_table(self, table_block: Dict, block_map: Dict) -> List[List[str]]:
        """Parse table structure from Textract blocks"""
        rows = {}

        if 'Relationships' in table_block:
            for relationship in table_block['Relationships']:
                if relationship['Type'] == 'CHILD':
                    for cell_id in relationship['Ids']:
                        cell = block_map.get(cell_id)
                        if cell and cell.get('BlockType') == 'CELL':
                            row_index = cell.get('RowIndex', 0)
                            col_index = cell.get('ColumnIndex', 0)

                            if row_index not in rows:
                                rows[row_index] = {}

                            cell_text = self._get_text_from_block(cell, block_map)
                            rows[row_index][col_index] = cell_text

        # Convert to 2D array
        table_data = []
        for row_index in sorted(rows.keys()):
            row = rows[row_index]
            row_data = [row.get(col_index, '') for col_index in sorted(row.keys())]
            table_data.append(row_data)

        return table_data


class BedrockService:
    """AWS Bedrock service for AI processing"""

    def __init__(self, region: str = "us-east-1", model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0"):
        self.region = region
        self.model_id = model_id
        self.bedrock_runtime = boto3.client('bedrock-runtime', region_name=region)

    def invoke_claude(self, prompt: str, system_prompt: Optional[str] = None, max_tokens: int = 4096) -> str:
        """
        Invoke Claude model via Bedrock

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens to generate

        Returns:
            Model response text
        """
        messages = [{"role": "user", "content": prompt}]

        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "messages": messages
        }

        if system_prompt:
            body["system"] = system_prompt

        response = self.bedrock_runtime.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body)
        )

        response_body = json.loads(response['body'].read())
        return response_body['content'][0]['text']

    def extract_bill_data_from_image(self, image_bytes: bytes, bill_type: Optional[str] = None) -> Dict:
        """
        Extract bill data directly from image using Claude's vision capabilities

        Args:
            image_bytes: Image file content as bytes
            bill_type: Optional bill type hint

        Returns:
            Structured bill data
        """
        import base64
        from io import BytesIO
        from PIL import Image

        # Check if PDF and convert to image
        if image_bytes[:4] == b'%PDF':
            try:
                import fitz  # PyMuPDF
                # Open PDF from bytes
                pdf_document = fitz.open(stream=image_bytes, filetype="pdf")
                # Get first page
                page = pdf_document[0]
                # Render page to pixmap (image) at 300 DPI
                mat = fitz.Matrix(300/72, 300/72)  # 300 DPI scaling
                pix = page.get_pixmap(matrix=mat)
                # Convert to PNG bytes
                image_bytes = pix.tobytes("png")
                media_type = "image/png"
                pdf_document.close()
            except Exception as e:
                print(f"Error converting PDF to image: {e}")
                raise Exception(f"PDF conversion failed: {str(e)}")
        # Determine media type for images
        elif image_bytes[:4] == b'\x89PNG':
            media_type = "image/png"
        elif image_bytes[:3] == b'\xff\xd8\xff':
            media_type = "image/jpeg"
        elif image_bytes[:6] == b'GIF87a' or image_bytes[:6] == b'GIF89a':
            media_type = "image/gif"
        elif image_bytes[:4] == b'RIFF' and image_bytes[8:12] == b'WEBP':
            media_type = "image/webp"
        else:
            media_type = "image/jpeg"  # Default fallback

        # Encode image to base64
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')

        system_prompt = """You are an AI assistant specialized in extracting structured data from utility bills.
Your task is to analyze bill images and return structured JSON data."""

        prompt = f"""
Please analyze this utility bill image and extract the following information.

Bill Type Hint: {bill_type or 'Unknown - please determine from the image'}

Extract and return a JSON object with these fields (set to null if not found):
{{
  "bill_type": "electricity|water|gas|fuel|waste",
  "provider_name": "string",
  "account_number": "string",
  "billing_period_start": "YYYY-MM-DD",
  "billing_period_end": "YYYY-MM-DD",
  "consumption_amount": number,
  "consumption_unit": "string (kWh, m³, liters, etc.)",
  "total_amount": number,
  "currency": "string (USD, EUR, AED, etc.)",
  "additional_charges": {{
    "tax": number,
    "fees": number
  }},
  "confidence_notes": "string - any uncertainties"
}}

Return ONLY the JSON object, no additional text.
"""

        try:
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4096,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_b64
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ],
                "system": system_prompt
            }

            response = self.bedrock_runtime.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body)
            )

            response_body = json.loads(response['body'].read())
            response_text = response_body['content'][0]['text']

            # Clean and parse JSON
            response_clean = response_text.strip()
            if response_clean.startswith('```json'):
                response_clean = response_clean[7:]
            if response_clean.startswith('```'):
                response_clean = response_clean[3:]
            if response_clean.endswith('```'):
                response_clean = response_clean[:-3]

            extracted_data = json.loads(response_clean.strip())
            return extracted_data

        except Exception as e:
            print(f"Error extracting bill data from image: {e}")
            return {
                "bill_type": bill_type,
                "error": str(e),
                "provider_name": None
            }

    def extract_bill_data(self, raw_text: str, forms: Dict, bill_type: Optional[str] = None) -> Dict:
        """
        Use Claude to intelligently extract bill data

        Args:
            raw_text: Raw OCR text
            forms: Extracted key-value pairs
            bill_type: Optional bill type hint

        Returns:
            Structured bill data
        """
        system_prompt = """You are an AI assistant specialized in extracting structured data from utility bills.
Your task is to analyze OCR-extracted text and key-value pairs, then return a structured JSON object with the bill information."""

        prompt = f"""
Analyze the following utility bill data and extract structured information.

Bill Type Hint: {bill_type or 'Unknown - please determine from content'}

OCR Text:
{raw_text[:2000]}

Key-Value Pairs:
{json.dumps(forms, indent=2)[:1000]}

Please extract and return a JSON object with the following fields (set to null if not found):
{{
  "bill_type": "electricity|water|gas|fuel|waste",
  "provider_name": "string",
  "account_number": "string",
  "billing_period_start": "YYYY-MM-DD",
  "billing_period_end": "YYYY-MM-DD",
  "consumption_amount": number,
  "consumption_unit": "string (kWh, m³, liters, etc.)",
  "total_amount": number,
  "currency": "string (USD, EUR, AED, etc.)",
  "additional_charges": {{
    "tax": number,
    "fees": number
  }},
  "confidence_notes": "string - any uncertainties or assumptions"
}}

Return ONLY the JSON object, no additional text.
"""

        try:
            response = self.invoke_claude(prompt, system_prompt)

            # Parse JSON from response
            # Sometimes Claude adds markdown code blocks, so clean it
            response_clean = response.strip()
            if response_clean.startswith('```json'):
                response_clean = response_clean[7:]
            if response_clean.startswith('```'):
                response_clean = response_clean[3:]
            if response_clean.endswith('```'):
                response_clean = response_clean[:-3]

            extracted_data = json.loads(response_clean.strip())
            return extracted_data

        except Exception as e:
            print(f"Error extracting bill data with Claude: {e}")
            # Return default structure
            return {
                "bill_type": bill_type,
                "error": str(e),
                "raw_text": raw_text[:500]
            }


# Factory functions
def get_s3_service(bucket_name: Optional[str] = None) -> S3Service:
    """Get S3 service instance"""
    if bucket_name is None:
        bucket_name = os.getenv('S3_BUCKET_NAME', 'eco-accounting-bills')
    return S3Service(bucket_name)


def get_textract_service() -> TextractService:
    """Get Textract service instance"""
    return TextractService()


def get_bedrock_service() -> BedrockService:
    """Get Bedrock service instance"""
    return BedrockService()
