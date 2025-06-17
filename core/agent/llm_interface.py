from typing import Dict, Any, List, Optional
import os
import json
from openai import OpenAI
from pydantic import BaseModel
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from settings_config import Settings
from rich.markdown import Markdown

console = Console()

class LLMResponse(BaseModel):
    """Structured response from the LLM"""
    content: str
    usage: Dict[str, int]
    metadata: Dict[str, Any] = {}

class LLMInterface:
    def __init__(self):
        """Initialize the LM Studio interface with configuration"""
        settings = Settings()
        self.base_url = settings.llm.base_url
        self.api_key = settings.llm.api_key
        self.model = settings.llm.model
        self.temperature = settings.llm.temperature
        self.max_tokens = settings.llm.max_tokens
        self.context_window = settings.llm.context_window
        
        # Initialize the OpenAI-compatible client
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key
        )
        
    def generate_response(
        self, 
        prompt: str,
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> LLMResponse:
        """Generate a response from the LLM"""
        console.print(f"[bold green]🚀 Prompt Sent:[/bold green] {prompt}")
        try:
            messages = []
            
            # Add system message if provided
            if system_message:
                messages.append({"role": "system", "content": system_message})
                
            # Add user prompt
            messages.append({"role": "user", "content": prompt})
            
            # Set default parameters if not specified
            temp = temperature if temperature is not None else self.temperature
            max_tokens = max_tokens if max_tokens is not None else self.max_tokens
            
            # Call the API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temp,
                max_tokens=max_tokens
            )
            
            # Extract content and usage
            content = response.choices[0].message.content
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }

            # Create a panel for the response
            response_panel = Panel(
                Markdown(content),
                title="[bold green]🤖 LLM Response[/bold green]",
                border_style="green",
                expand=False
            )
            console.print(response_panel)

            # Create a table for usage statistics
            usage_table = Table(
                title="[bold blue]📊 Token Usage[/bold blue]",
                show_header=True,
                header_style="bold magenta",
                border_style="blue"
            )
            usage_table.add_column("Metric", style="cyan")
            usage_table.add_column("Value", style="yellow")

            usage_table.add_row("Prompt Tokens", str(usage["prompt_tokens"]))
            usage_table.add_row("Completion Tokens", str(usage["completion_tokens"]))
            usage_table.add_row("Total Tokens", str(usage["total_tokens"]))

            console.print(usage_table)
            
            return LLMResponse(
                content=content,
                usage=usage,
                metadata={"model": self.model}
            )
            
        except Exception as e:
            # Handle errors gracefully
            error_message = f"Error generating LLM response: {str(e)}"
            return LLMResponse(
                content=error_message,
                usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                metadata={"error": str(e)}
            )
    
    def generate_structured_output(
        self,
        prompt: str,
        output_schema: Dict[str, Any],
        system_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a structured JSON response according to schema"""
        try:
            # Build schema instruction
            schema_instruction = (
                f"You must format your response as a JSON object with the following structure:\n"
                f"{json.dumps(output_schema, indent=2)}\n\n"
                f"Ensure your response is valid JSON that follows this schema exactly."
            )
            
            # Combine prompt with schema instruction
            combined_prompt = f"{prompt}\n\n{schema_instruction}"
            
            # Generate response
            response = self.generate_response(
                prompt=combined_prompt,
                system_message=system_message
            )
            
            # Parse JSON from response
            json_str = response.content
            # Find JSON block if it's wrapped in markdown
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0].strip()
                
            # Parse the JSON
            result = json.loads(json_str)
            return result
            
        except json.JSONDecodeError as e:
            # Handle JSON parsing errors
            return {
                "error": "Failed to parse structured output",
                "details": str(e),
                "raw_response": response.content if 'response' in locals() else "No response generated"
            }
        except Exception as e:
            # Handle other errors
            return {
                "error": "Error generating structured output",
                "details": str(e)
            }
    
    def check_connectivity(self) -> bool:
        """Test connectivity to LM Studio server"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            return True
        except Exception:
            return False