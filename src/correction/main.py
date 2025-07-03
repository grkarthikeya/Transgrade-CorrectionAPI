

#!/usr/bin/env python
import sys
import os
import warnings
import logging
import requests
import json 
from flask import Flask, jsonify
from flask_cors import CORS
from correction.crew import Correction
from crewai.crews.crew_output import CrewOutput

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress warnings
warnings.filterwarnings("ignore", category=SyntaxWarning)

# Django API configuration
DJANGO_API_BASE_URL = "http://65.1.121.100:8000"

# ---
# ### 🔍 Function to Retrieve Combined Data
# ---
def get_combined_data(subject_id: str, script_id: str):
    """Retrieve ocr_json, textract_json and context data from Django API using combined-data endpoint."""
    try:
        # Log the parameters for debugging
        logger.info(f"Requesting data for subject_id: {subject_id}, script_id: {script_id}")
        
        url = f"{DJANGO_API_BASE_URL}/combined-data/?subject_id={subject_id}&script_id={script_id}"
        logger.info(f"API URL: {url}")
        
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            logger.info(f"API Response keys: {list(data.keys())}")
            
            # Handle the actual response structure with keys: ['context', 'structured_json', 'ocr_json', 'textract_json']
            if 'ocr_json' in data:
                ocr_json_data = data['ocr_json']
                textract_json_data = data['textract_results']  # Changed from 'textract_json' to 'textract_results'
                context_data = data.get('context')
                
                # Log what we received
                logger.info(f"OCR data type: {type(ocr_json_data)}")
                if isinstance(ocr_json_data, (list, dict, str)):
                    logger.info(f"OCR data length: {len(ocr_json_data)}")
                else:
                    logger.info(f"OCR data value: {ocr_json_data}")
                
                logger.info(f"Textract data type: {type(textract_json_data)}")
                if isinstance(textract_json_data, (list, dict, str)):
                    logger.info(f"Textract data length: {len(textract_json_data)}")
                else:
                    logger.info(f"Textract data value: {textract_json_data}")
                
                # Check if ocr_json is empty or None
                if not ocr_json_data:
                    return None, None, None, f"No OCR data found for subject_id: {subject_id}, script_id: {script_id}"
                
                # Return the ocr_json, textract_json and context
                return ocr_json_data, textract_json_data, context_data, None
            
            else:
                return None, None, None, f"No valid data found in response. Available keys: {list(data.keys())}"
        else:
            logger.error(f"API error: {response.status_code} - {response.text}")
            return None, None, None, f"API error: {response.status_code} - {response.text}"
    except requests.exceptions.RequestException as e:
        logger.error(f"API request error: {str(e)}")
        return None, None, None, f"API request error: {str(e)}"

# ---
# ### ✂️ Function to Extract Textract Text - COMPLETELY FIXED VERSION
# ---
def extract_textract_text(textract_json_data):
    """Extract and combine text from textract_json data with proper structure handling."""
    if not textract_json_data:
        logger.warning("No textract data provided")
        return ""
    
    textract_text = []
    
    try:
        # Handle different possible data structures
        if isinstance(textract_json_data, str):
            # If it's already a string, return it
            logger.info("Textract data is already a string")
            return textract_json_data
            
        elif isinstance(textract_json_data, list):
            logger.info(f"Processing textract data as list with {len(textract_json_data)} items")
            
            # This handles your actual data structure: list of page objects
            for page_idx, page in enumerate(textract_json_data):
                logger.info(f"Processing page {page_idx + 1}")
                
                if isinstance(page, dict):
                    # Handle the structure from your test data
                    if 'extracted_text' in page and isinstance(page['extracted_text'], dict):
                        extracted_text = page['extracted_text']
                        if 'extracted_lines' in extracted_text and isinstance(extracted_text['extracted_lines'], list):
                            logger.info(f"Found {len(extracted_text['extracted_lines'])} lines in page {page_idx + 1}")
                            
                            for line in extracted_text['extracted_lines']:
                                if isinstance(line, dict) and 'text' in line:
                                    text_content = line['text'].strip()
                                    if text_content:  # Only add non-empty text
                                        textract_text.append(text_content)
                    
                    # Handle direct extracted_lines in page (alternative structure)
                    elif 'extracted_lines' in page and isinstance(page['extracted_lines'], list):
                        logger.info(f"Found {len(page['extracted_lines'])} lines in page {page_idx + 1}")
                        
                        for line in page['extracted_lines']:
                            if isinstance(line, dict) and 'text' in line:
                                text_content = line['text'].strip()
                                if text_content:
                                    textract_text.append(text_content)
                    
                    # Handle single text field in page
                    elif 'text' in page:
                        text_content = page['text'].strip()
                        if text_content:
                            textract_text.append(text_content)
                            
                elif isinstance(page, str):
                    # If it's a list of strings
                    text_content = page.strip()
                    if text_content:
                        textract_text.append(text_content)
                        
        elif isinstance(textract_json_data, dict):
            logger.info("Processing textract data as dict")
            
            # Handle the main textract_results structure (nested case)
            if 'textract_results' in textract_json_data:
                logger.info("Found textract_results key")
                textract_results = textract_json_data['textract_results']
                
                if isinstance(textract_results, list):
                    # Recursively call this function with the list
                    return extract_textract_text(textract_results)
                elif 'pages' in textract_results and isinstance(textract_results['pages'], list):
                    logger.info(f"Found {len(textract_results['pages'])} pages in textract_results")
                    
                    for page_idx, page in enumerate(textract_results['pages']):
                        logger.info(f"Processing page {page_idx + 1}")
                        
                        if 'extracted_lines' in page and isinstance(page['extracted_lines'], list):
                            logger.info(f"Found {len(page['extracted_lines'])} lines in page {page_idx + 1}")
                            
                            for line in page['extracted_lines']:
                                if isinstance(line, dict) and 'text' in line:
                                    text_content = line['text'].strip()
                                    if text_content:  # Only add non-empty text
                                        textract_text.append(text_content)
                                        
            # Handle direct pages structure
            elif 'pages' in textract_json_data and isinstance(textract_json_data['pages'], list):
                logger.info("Found direct pages structure")
                
                for page_idx, page in enumerate(textract_json_data['pages']):
                    logger.info(f"Processing direct page {page_idx + 1}")
                    
                    if 'extracted_lines' in page and isinstance(page['extracted_lines'], list):
                        for line in page['extracted_lines']:
                            if isinstance(line, dict) and 'text' in line:
                                text_content = line['text'].strip()
                                if text_content:
                                    textract_text.append(text_content)
                                    
            # Handle single dict object with text
            elif 'text' in textract_json_data:
                logger.info("Found direct text in dict")
                return textract_json_data['text']
        
        # Join all extracted text
        final_text = " ".join(textract_text)
        logger.info(f"Extracted textract text length: {len(final_text)}")
        logger.info(f"Number of text segments: {len(textract_text)}")
        
        # Log first few segments for debugging
        if textract_text:
            logger.info(f"First few text segments: {textract_text[:3]}")
        
        return final_text
        
    except Exception as e:
        logger.error(f"Error extracting textract text: {str(e)}")
        return ""

def extract_ocr_text(ocr_json_data):
    """Extract and combine OCR text from ocr_json data."""
    if not ocr_json_data:
        return ""
    
    ocr_text = []
    
    # Handle different possible data structures
    if isinstance(ocr_json_data, str):
        # If it's already a string, return it
        return ocr_json_data
    elif isinstance(ocr_json_data, list):
        # If it's a list of blocks (AWS Textract format)
        for block in ocr_json_data:
            if isinstance(block, dict):
                # AWS Textract format
                if block.get('BlockType') == 'LINE' and 'Text' in block:
                    ocr_text.append(block['Text'])
                # Generic text extraction
                elif 'text' in block:
                    ocr_text.append(block['text'])
                elif 'Text' in block:
                    ocr_text.append(block['Text'])
            elif isinstance(block, str):
                # If it's a list of strings
                ocr_text.append(block)
    elif isinstance(ocr_json_data, dict):
        # If it's a single dict object
        if 'text' in ocr_json_data:
            return ocr_json_data['text']
        elif 'Text' in ocr_json_data:
            return ocr_json_data['Text']
    
    return " ".join(ocr_text)

# ---
# ### 📊 Function to Get Textract Statistics - COMPLETELY UPDATED
# ---
def get_textract_statistics(textract_json_data):
    """Extract statistics from textract data for debugging purposes."""
    stats = {
        'total_pages': 0,
        'total_lines': 0,
        'total_blocks': 0,
        'confidence_scores': [],
        'page_details': []
    }
    
    if not textract_json_data:
        return stats
    
    try:
        # Handle list structure (your actual data format)
        if isinstance(textract_json_data, list):
            stats['total_pages'] = len(textract_json_data)
            
            for page in textract_json_data:
                if isinstance(page, dict):
                    # Handle the structure from your test data
                    if 'extracted_text' in page and isinstance(page['extracted_text'], dict):
                        extracted_text = page['extracted_text']
                        
                        page_info = {
                            'page_number': page.get('page_number', 'unknown'),
                            'total_lines': extracted_text.get('total_lines', 0),
                            'total_blocks': extracted_text.get('total_blocks', 0),
                            's3_key': extracted_text.get('s3_key', 'unknown'),
                            'job_id': extracted_text.get('job_id', 'unknown'),
                            'confidence_score': page.get('confidence_score', 0),
                            'processing_status': page.get('processing_status', 'unknown')
                        }
                        stats['page_details'].append(page_info)
                        stats['total_lines'] += extracted_text.get('total_lines', 0)
                        stats['total_blocks'] += extracted_text.get('total_blocks', 0)
                        
                        # Extract confidence scores from extracted_lines
                        if 'extracted_lines' in extracted_text and isinstance(extracted_text['extracted_lines'], list):
                            for line in extracted_text['extracted_lines']:
                                if isinstance(line, dict) and 'confidence' in line:
                                    stats['confidence_scores'].append(line['confidence'])
                    
                    # Handle direct structure (alternative)
                    elif 'extracted_lines' in page:
                        page_info = {
                            'page_number': page.get('page_number', 'unknown'),
                            'total_lines': len(page.get('extracted_lines', [])),
                            'total_blocks': page.get('total_blocks', 0),
                            'confidence_score': page.get('confidence_score', 0)
                        }
                        stats['page_details'].append(page_info)
                        stats['total_lines'] += len(page.get('extracted_lines', []))
                        stats['total_blocks'] += page.get('total_blocks', 0)
                        
                        # Extract confidence scores
                        for line in page.get('extracted_lines', []):
                            if isinstance(line, dict) and 'confidence' in line:
                                stats['confidence_scores'].append(line['confidence'])
        
        # Handle the nested textract_results structure
        elif isinstance(textract_json_data, dict) and 'textract_results' in textract_json_data:
            # Recursively call with the nested structure
            return get_textract_statistics(textract_json_data['textract_results'])
            
        elif isinstance(textract_json_data, dict) and 'pages' in textract_json_data:
            textract_results = textract_json_data
            
            if isinstance(textract_results['pages'], list):
                stats['total_pages'] = len(textract_results['pages'])
                
                for page in textract_results['pages']:
                    page_info = {
                        'page_number': page.get('page_number', 'unknown'),
                        'total_lines': page.get('total_lines', 0),
                        'total_blocks': page.get('total_blocks', 0),
                        'image_filename': page.get('image_filename', 'unknown'),
                        'average_confidence': page.get('average_confidence', 0)
                    }
                    stats['page_details'].append(page_info)
                    stats['total_lines'] += page.get('total_lines', 0)
                    stats['total_blocks'] += page.get('total_blocks', 0)
                    
                    # Extract confidence scores from extracted_lines
                    if 'extracted_lines' in page and isinstance(page['extracted_lines'], list):
                        for line in page['extracted_lines']:
                            if isinstance(line, dict) and 'confidence' in line:
                                stats['confidence_scores'].append(line['confidence'])
        
        # Calculate average confidence if available
        if stats['confidence_scores']:
            stats['average_confidence'] = sum(stats['confidence_scores']) / len(stats['confidence_scores'])
            stats['min_confidence'] = min(stats['confidence_scores'])
            stats['max_confidence'] = max(stats['confidence_scores'])
            
    except Exception as e:
        logger.warning(f"Error extracting textract statistics: {str(e)}")
    
    return stats


# ---
# ### 💾 Function to Save Correction Data to Django API (Preserving vlmdesc)
# ---
def get_existing_vlmdesc(script_id: str):
    """Retrieve existing vlmdesc data for a script_id to preserve it."""
    try:
        # Try multiple possible endpoints to get existing data
        possible_urls = [
            f"{DJANGO_API_BASE_URL}/compare-text/{script_id}/",
            f"{DJANGO_API_BASE_URL}/compare-text/?script_id={script_id}",
            f"{DJANGO_API_BASE_URL}/compare-text/"
        ]
        
        for url in possible_urls:
            try:
                logger.info(f"Trying to retrieve existing vlmdesc data from: {url}")
                response = requests.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"Response data type: {type(data)}")
                    logger.info(f"Response data preview: {str(data)[:200]}...")
                    
                    # Handle different response formats
                    if isinstance(data, dict):
                        # Single object response
                        existing_vlmdesc = data.get('vlmdesc', {})
                        logger.info(f"Retrieved existing vlmdesc from dict: {existing_vlmdesc}")
                        return existing_vlmdesc
                        
                    elif isinstance(data, list):
                        # List response - find matching script_id
                        logger.info(f"Response is a list with {len(data)} items")
                        for item in data:
                            if isinstance(item, dict):
                                # Check if this item matches our script_id
                                if (item.get('script_id') == script_id or 
                                    item.get('script_id') == int(script_id) if script_id.isdigit() else False):
                                    existing_vlmdesc = item.get('vlmdesc', {})
                                    logger.info(f"Found matching script_id in list, vlmdesc: {existing_vlmdesc}")
                                    return existing_vlmdesc
                        
                        # If no exact match found, try to get the most recent one
                        if data and isinstance(data[0], dict):
                            existing_vlmdesc = data[0].get('vlmdesc', {})
                            logger.info(f"No exact match found, using first item vlmdesc: {existing_vlmdesc}")
                            return existing_vlmdesc
                    
                    else:
                        logger.warning(f"Unexpected data type: {type(data)}")
                        continue
                        
                else:
                    logger.warning(f"API returned status {response.status_code} for {url}")
                    continue
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed for {url}: {str(e)}")
                continue
        
        logger.warning(f"Could not retrieve existing vlmdesc from any endpoint for script_id: {script_id}")
        return {}
    
    except Exception as e:
        logger.warning(f"Error retrieving existing vlmdesc: {str(e)}")
        return {}


# ---
# ### 💾 Function to Save Correction Data to Django API
# ---
def save_correction_data(script_id: str, result: str,):
    """Save the correction data to the Django API compare-text endpoint."""
    try:
        url = f"{DJANGO_API_BASE_URL}/compare-text/"
        logger.info(f"Saving correction data to: {url}")

        # Get existing vlmdesc data to preserve it
        existing_vlmdesc = get_existing_vlmdesc(script_id)
        
        
        
        # Prepare the payload
        payload = {
            "script_id": script_id,
            "restructured": {
                "final_text": " ",  # Full corrected text
            },
            "vlmdesc": {
                "vlm_desc": existing_vlmdesc ,  # Flagged corrected text
            },
            "final_corrected_text" : {
                "result" : result,
            }
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            logger.info(f"Successfully saved correction data for script_id: {script_id}")
            return True, response.json()
        else:
            logger.error(f"Failed to save correction data: {response.status_code} - {response.text}")
            return False, f"API error: {response.status_code} - {response.text}"
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error saving correction data: {str(e)}")
        return False, f"API request error: {str(e)}"

# ---
# ### 🧠 Core OCR Correction Logic
# ---
def run_ocr_correction(subject_id: str, script_id: str):
    """Run OCR correction pipeline using subject_id and script_id."""
    try:
        # Retrieve combined data
        ocr_json_data, textract_json_data, context_data, error = get_combined_data(subject_id, script_id)
        if error:
            return False, error

        if not ocr_json_data:
            return False, f"No OCR data found for subject_id: {subject_id}, script_id: {script_id}"

        # Extract OCR text
        ocr_text = extract_ocr_text(ocr_json_data)
        if not ocr_text:
            return False, f"No OCR text could be extracted for script_id: {script_id}"

        # Extract Textract text
        textract_text = extract_textract_text(textract_json_data)
        logger.info(f"Extracted textract text preview: {textract_text[:200]}...")

        # Get textract statistics
        textract_stats = get_textract_statistics(textract_json_data)
        logger.info(f"Textract statistics: {textract_stats}")

        # Use context data or fallback
        context = context_data if context_data else f"Subject ID: {subject_id}, Script ID: {script_id}"

        # Prepare inputs for the agent
        inputs = {
            "ocr1": ocr_text,
            "ocr2": textract_text,
            "context": context
        }

        # Log inputs
        logger.info(f"OCR Text length: {len(ocr_text)}")
        logger.info(f"Textract Text length: {len(textract_text)}")
        logger.info(f"Context: {str(context)[:100]}...")
        logger.info(f"OCR JSON data type: {type(ocr_json_data)}")
        logger.info(f"Textract JSON data type: {type(textract_json_data)}")

        # Print extracted texts
        print("\n" + "="*80)
        print("📄 EXTRACTED OCR TEXT:")
        print("="*80)
        print(ocr_text)
        print("\n" + "="*80)
        print("📄 EXTRACTED TEXTRACT TEXT:")
        print("="*80)
        print(textract_text)
        print("\n" + "="*80)
        print("📝 CONTEXT:")
        print("="*80)
        print(context)
        print("="*80 + "\n")

        # Run the agent
        result = Correction().crew().kickoff(inputs=inputs)
        
        # Token Usage
        print(f"\nToken Usage:\n{result.token_usage}\n")
        
        # Convert result to string
        result = str(result)
        
        # Handle string result as plain text
        logger.info("Crew result is a string")
        


        # Save to Django API
        save_success, save_message = save_correction_data(script_id, result)
        if not save_success:
            logger.error(f"Failed to save correction data: {save_message}")
            return False, f"OCR correction completed but failed to save: {save_message}"

        logger.info(f"OCR correction completed successfully for script_id: {script_id}")
        return True, f"Success: OCR corrected and saved for script_id {script_id}."

    except Exception as e:
        logger.error(f"OCR correction failed: {str(e)}")
        return False, f"Error: {str(e)}"


# ---
# ### 🚀 Flask Application
# ---
def run():
    """Start the Flask application for OCR correction."""
    app = Flask(__name__)
    app.secret_key = 'super_secret_key'
    CORS(app, origins=['http://localhost:3000'])  # Enable CORS for frontend

    @app.route('/')
    def index():
        """Root endpoint with API information."""
        return jsonify({
            "message": "OCR Correction API is running",
            "endpoints": {
                "correct_ocr": "/correct_ocr/<subject_id>/<script_id>",
                "test_data": "/test_data/<subject_id>/<script_id>",
                "test_django": "/test_django_api/<subject_id>/<script_id>",
                "health_check": "/health"
            }
        })

    @app.route('/correct_ocr/<subject_id>/<script_id>', methods=['GET'])
    def correct_ocr_route(subject_id, script_id):
        """Endpoint to run OCR correction for a given subject_id and script_id."""
        if not subject_id or not script_id:
            return jsonify({
                "status": "error", 
                "message": "Subject ID and Script ID are required"
            }), 400

        logger.info(f"Processing OCR correction for subject_id: {subject_id}, script_id: {script_id}")
        success, message = run_ocr_correction(subject_id, script_id)

        return jsonify({
            "status": "success" if success else "error",
            "subject_id": str(subject_id),
            "script_id": str(script_id),
            "message": message
        }), 200 if success else 500

    @app.route('/health')
    def health_check():
        """Health check endpoint to verify Django API connectivity."""
        try:
            response = requests.get(f"{DJANGO_API_BASE_URL}/", timeout=5)
            if response.status_code == 200:
                return jsonify({
                    "status": "healthy", 
                    "django_api": "connected",
                    "django_url": DJANGO_API_BASE_URL
                })
            else:
                return jsonify({
                    "status": "unhealthy", 
                    "django_api": "error", 
                    "details": f"Status: {response.status_code}"
                })
        except Exception as e:
            return jsonify({
                "status": "unhealthy", 
                "django_api": "disconnected", 
                "error": str(e)
            })

    @app.route('/test_data/<subject_id>/<script_id>')
    def test_data_route(subject_id, script_id):
        """Test endpoint to check data retrieval with detailed debugging."""
        logger.info(f"Testing data retrieval for subject_id: {subject_id}, script_id: {script_id}")
        
        try:
            # Test the Django API call directly
            url = f"{DJANGO_API_BASE_URL}/combined-data/?subject_id={subject_id}&script_id={script_id}"
            logger.info(f"Calling Django API: {url}")
            
            response = requests.get(url)
            logger.info(f"Django API Response Status: {response.status_code}")
            
            if response.status_code == 200:
                raw_data = response.json()
                logger.info(f"Raw API Response keys: {list(raw_data.keys())}")
                
                # Now test our parsing function
                ocr_json_data, textract_json_data, context_data, error = get_combined_data(subject_id, script_id)
                
                # Extract text previews
                ocr_preview = extract_ocr_text(ocr_json_data)[:200] if ocr_json_data else None
                textract_preview = extract_textract_text(textract_json_data)[:200] if textract_json_data else None
                
                # Get textract statistics
                textract_stats = get_textract_statistics(textract_json_data)
                
                return jsonify({
                    "subject_id": str(subject_id),
                    "script_id": str(script_id),
                    "django_api_status": response.status_code,
                    "raw_api_response": raw_data,
                    "parsed_results": {
                        "ocr_json_blocks_count": len(ocr_json_data) if isinstance(ocr_json_data, (list, dict, str)) else 0,
                        "ocr_json_type": str(type(ocr_json_data)),
                        "ocr_json_preview": str(ocr_json_data)[:300] if ocr_json_data else "None/Empty",
                        "textract_json_blocks_count": len(textract_json_data) if isinstance(textract_json_data, (list, dict, str)) else 0,
                        "textract_json_type": str(type(textract_json_data)),
                        "textract_json_preview": str(textract_json_data)[:300] if textract_json_data else "None/Empty",
                        "context_data": str(context_data)[:200] if context_data else None,
                        "parsing_error": error,
                        "ocr_text_preview": ocr_preview,
                        "textract_text_preview": textract_preview,
                        "textract_text_full_length": len(extract_textract_text(textract_json_data)) if textract_json_data else 0,
                        "textract_statistics": textract_stats,
                        "sample_ocr_block": ocr_json_data[0] if isinstance(ocr_json_data, list) and len(ocr_json_data) > 0 else None,
                        "sample_textract_structure": {
                            "has_textract_results": 'textract_results' in textract_json_data if isinstance(textract_json_data, dict) else False,
                            "textract_keys": list(textract_json_data.keys()) if isinstance(textract_json_data, dict) else None
                        }
                    }
                })
            else:
                return jsonify({
                    "subject_id": str(subject_id),
                    "script_id": str(script_id),
                    "django_api_status": response.status_code,
                    "django_api_error": response.text,
                    "error": f"Django API returned status {response.status_code}"
                })
                
        except Exception as e:
            logger.error(f"Error in test_data_route: {str(e)}")
            return jsonify({
                "subject_id": str(subject_id),
                "script_id": str(script_id),
                "error": f"Exception occurred: {str(e)}"
            })

    @app.route('/test_django_api/<subject_id>/<script_id>')
    def test_django_direct(subject_id, script_id):
        """Test Django API directly without any parsing."""
        try:
            url = f"{DJANGO_API_BASE_URL}/combined-data/?subject_id={subject_id}&script_id={script_id}"
            response = requests.get(url)
            
            return jsonify({
                "url_called": url,
                "status_code": response.status_code,
                "response_headers": dict(response.headers),
                "response_body": response.json() if response.status_code == 200 else response.text,
                "subject_id": str(subject_id),
                "script_id": str(script_id)
            })
        except Exception as e:
            return jsonify({
                "error": str(e),
                "url_attempted": f"{DJANGO_API_BASE_URL}/combined-data/?subject_id={subject_id}&script_id={script_id}",
                "subject_id": str(subject_id),
                "script_id": str(script_id)
            })

    # Run Flask app
    port = int(os.environ.get('PORT', 5055))
    app.run(host='0.0.0.0', port=port, debug=True)

# ---
# ### 🧭 Main Entry Point
# ---
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].lower() == "run":
        run()
    else:
        print("Usage: python main.py run")