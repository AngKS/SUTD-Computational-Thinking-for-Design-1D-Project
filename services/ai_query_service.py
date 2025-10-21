import json
import os
from openai import OpenAI
import config

class AIQueryService:
    def __init__(self):
        """Initialize OpenAI client and load component schema"""
        if not config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in environment variables. Please create a .env file with your API key.")
        
        self.client = OpenAI(
            api_key=config.OPENAI_API_KEY,
            base_url="https://api.groq.com/openai/v1"
        )
        self.model = config.OPENAI_MODEL
        self.max_tokens = config.MAX_TOKENS
        self.temperature = config.TEMPERATURE
        
        # Load system prompt
        self.system_prompt = self._load_system_prompt()
        
    def _load_system_prompt(self):
        """Load the system prompt from file"""
        prompt_path = os.path.join('assets', 'prompts', 'analytics_system_prompt.txt')
        try:
            with open(prompt_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"System prompt file not found at {prompt_path}")
    
    def prepare_data_context(self, data_dict):
        """Prepare and format data context for the API call"""
        context_parts = []
        
        if "transactions" in data_dict:
            transactions_data = data_dict["transactions"]
            # Summarize if too large
            transactions_summary = self._summarize_transactions(transactions_data)
            context_parts.append(f"TRANSACTIONS DATA:\n{json.dumps(transactions_summary, indent=2)}")
        
        if "inventory" in data_dict:
            inventory_data = data_dict["inventory"]
            # Simplify inventory data
            inventory_summary = self._format_inventory(inventory_data)
            context_parts.append(f"INVENTORY DATA:\n{json.dumps(inventory_summary, indent=2)}")
        
        if "promocodes" in data_dict:
            promo_data = data_dict["promocodes"]
            context_parts.append(f"PROMO CODES DATA:\n{json.dumps(promo_data, indent=2)}")
        
        return "\n\n".join(context_parts)
    
    def _summarize_transactions(self, transactions_data):
        """Summarize transaction data to reduce token usage"""
        if not transactions_data or "transactions" not in transactions_data:
            return {"transactions": []}
        
        transactions = transactions_data["transactions"]
        
        # If too many transactions, take a sample or aggregate
        if len(transactions) > 50:
            # Take most recent 50 transactions
            transactions = transactions[-50:]
        
        # Simplify transaction structure
        simplified = []
        for t in transactions:
            simplified.append({
                "transaction_id": t.get("transaction_id"),
                "date": t.get("date"),
                "total_amount": t.get("total_amount"),
                "promo_code": t.get("promo_code"),
                "customer": {
                    "name": t.get("customer", {}).get("name"),
                    "email": t.get("customer", {}).get("email"),
                    "country": t.get("customer", {}).get("country")
                },
                "items": [
                    {
                        "product_id": item.get("product_id"),
                        "name": item.get("name"),
                        "quantity": item.get("quantity"),
                        "price": item.get("price")
                    }
                    for item in t.get("items", [])
                ]
            })
        
        return {"transactions": simplified}
    
    def _format_inventory(self, inventory_data):
        """Format inventory data for API consumption"""
        if not inventory_data or "products" not in inventory_data:
            return {"products": []}
        
        # Remove image paths and other non-essential data
        products = []
        for p in inventory_data["products"]:
            products.append({
                "id": p.get("id"),
                "name": p.get("name"),
                "price": p.get("price"),
                "quantity": p.get("quantity"),
                "category": p.get("category"),
                "description": p.get("description")
            })
        
        return {"total": len(products), "products": products}
    
    def query(self, user_question, data_context):
        """Send query to OpenAI and return parsed response"""
        if not user_question or not user_question.strip():
            raise ValueError("Query cannot be empty")
        
        # Validate query length
        if len(user_question) > 500:
            raise ValueError("Query is too long. Please keep it under 500 characters.")
        
        # Prepare data context
        formatted_context = self.prepare_data_context(data_context)
        
        # Check if we have any data
        if not formatted_context or formatted_context.strip() == "":
            raise ValueError("No data available to query. Please select at least one data source.")
        
        # Build user message
        user_message = f"{user_question}\n\nDATA CONTEXT:\n{formatted_context}"
        
        # Call OpenAI API with retry logic
        max_retries = 3
        retry_count = 0
        last_error = None
        
        while retry_count < max_retries:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    max_completion_tokens=self.max_tokens,
                    # temperature=self.temperature,
                    response_format={"type": "json_object"}
                )
                
                # Parse response
                response_content = response.choices[0].message.content
                parsed_response = json.loads(response_content)
                
                # Validate response structure
                if not self._validate_response(parsed_response):
                    raise ValueError("Invalid response structure from AI")
                
                return parsed_response
                
            except json.JSONDecodeError as e:
                last_error = f"Failed to parse AI response as JSON: {str(e)}"
                retry_count += 1
            except Exception as e:
                error_msg = str(e)
                
                # Handle specific OpenAI errors
                if "rate_limit" in error_msg.lower():
                    raise Exception("Rate limit exceeded. Please try again in a moment.")
                elif "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
                    raise Exception("Invalid API key. Please check your .env file configuration.")
                elif "timeout" in error_msg.lower():
                    last_error = "Request timed out. Retrying..."
                    retry_count += 1
                else:
                    raise Exception(f"Error calling OpenAI API: {error_msg}")
        
        # If we exhausted retries
        if last_error:
            raise Exception(f"Failed after {max_retries} attempts: {last_error}")
        else:
            raise Exception("Failed to get response from AI service")
    
    def query_stream(self, user_question, data_context):
        """
        Stream query to OpenAI and yield components as they become complete.
        
        Args:
            user_question: Natural language query from user
            data_context: Dict with transactions, inventory, promocodes data
            
        Yields:
            Dict with type "summary", "component", "error", "warning", or "complete"
        """
        from services.streaming_json_parser import StreamingJSONParser
        
        if not user_question or not user_question.strip():
            yield {
                "type": "error",
                "message": "Query cannot be empty",
                "fatal": True
            }
            return
        
        # Validate query length
        if len(user_question) > 500:
            yield {
                "type": "error",
                "message": "Query is too long. Please keep it under 500 characters.",
                "fatal": True
            }
            return
        
        # Prepare data context
        formatted_context = self.prepare_data_context(data_context)
        
        if not formatted_context or formatted_context.strip() == "":
            yield {
                "type": "error",
                "message": "No data available to query. Please select at least one data source.",
                "fatal": True
            }
            return
        
        # Build user message
        user_message = f"{user_question}\n\nDATA CONTEXT:\n{formatted_context}"
        
        # Initialize parser
        parser = StreamingJSONParser()
        
        try:
            # Call OpenAI API with streaming
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_completion_tokens=self.max_tokens,
                response_format={"type": "json_object"},
                stream=True,
                stream_options={"include_usage": True}
            )
            
            # Process stream
            for chunk in response:
                # Get delta content
                delta = chunk.choices[0].delta if chunk.choices else None
                
                if delta and delta.content:
                    # Feed to parser
                    results = parser.feed(delta.content)
                    
                    # Yield any completed objects
                    for result in results:
                        if result["type"] == "fatal_error":
                            # Stop streaming on fatal error
                            yield result
                            return
                        else:
                            yield result
                
                # Check for finish reason
                if chunk.choices and chunk.choices[0].finish_reason:
                    finish_reason = chunk.choices[0].finish_reason
                    
                    if finish_reason == "stop":
                        # Normal completion
                        if not parser.is_complete():
                            # Stream ended but JSON incomplete
                            partial = parser.get_partial_result()
                            yield {
                                "type": "warning",
                                "message": "Stream ended with incomplete JSON",
                                "partial_result": partial
                            }
                    elif finish_reason == "length":
                        # Hit token limit
                        yield {
                            "type": "warning",
                            "message": "Response truncated due to length limit. Results may be incomplete."
                        }
                    elif finish_reason == "content_filter":
                        # Content filtered
                        yield {
                            "type": "error",
                            "message": "Response blocked by content filter",
                            "fatal": True
                        }
            
            # Stream complete - yield final stats
            yield {
                "type": "complete",
                "summary_extracted": parser.summary_extracted,
                "components_count": parser.components_yielded
            }
            
        except Exception as e:
            error_msg = str(e)
            
            # Handle specific OpenAI errors
            if "rate_limit" in error_msg.lower():
                yield {
                    "type": "error",
                    "message": "Rate limit exceeded. Please try again in a moment.",
                    "fatal": True
                }
            elif "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
                yield {
                    "type": "error",
                    "message": "Invalid API key. Please check your .env file configuration.",
                    "fatal": True
                }
            else:
                yield {
                    "type": "error",
                    "message": f"Error calling OpenAI API: {error_msg}",
                    "fatal": True
                }
    
    def query_stream_with_cancellation(self, user_question, data_context, stop_signal_callback):
        """
        Stream query with support for user cancellation.
        
        Args:
            user_question: Natural language query
            data_context: Data to analyze
            stop_signal_callback: Function that returns True if user wants to stop
            
        Yields:
            Stream results (same as query_stream)
        """
        for result in self.query_stream(user_question, data_context):
            # Check if user wants to stop
            if stop_signal_callback and stop_signal_callback():
                yield {
                    "type": "cancelled",
                    "message": "Generation stopped by user"
                }
                return
            
            yield result
    
    def _validate_response(self, response):
        """Validate that the response has the expected structure"""
        if not isinstance(response, dict):
            return False
        
        if "summary" not in response or "components" not in response:
            return False
        
        if not isinstance(response["components"], list):
            return False
        
        # Validate each component has type and config
        for component in response["components"]:
            if not isinstance(component, dict):
                return False
            if "type" not in component or "config" not in component:
                return False
        
        return True
