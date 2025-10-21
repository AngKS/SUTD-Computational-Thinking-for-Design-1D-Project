"""
Streaming JSON Parser for GPT Responses

Robust state machine for parsing streaming JSON responses from OpenAI GPT.
Handles character-by-character input and detects complete JSON objects.
"""

from enum import Enum, auto
import json
import re


class ParserState(Enum):
    """Parser states for robust JSON streaming"""
    INIT = auto()                    # Initial state
    IN_ROOT_OBJECT = auto()          # Inside root { }
    PARSING_SUMMARY = auto()         # Inside "summary" value
    IN_COMPONENTS_ARRAY = auto()     # Inside "components" array
    IN_COMPONENT_OBJECT = auto()     # Inside a component { }
    IN_STRING = auto()               # Inside a string value
    ESCAPE_SEQUENCE = auto()         # Next char is escaped
    COMPLETE = auto()                # Parsing complete


class StreamingJSONParser:
    """
    Robust state machine for parsing streaming JSON responses from GPT.
    
    Handles:
    - Character-by-character streaming input
    - Nested object and array structures
    - String escape sequences
    - Partial JSON recovery
    - Complete object detection
    
    Expected JSON structure:
    {
        "summary": "Text summary here...",
        "components": [
            {"type": "metric", "config": {...}},
            {"type": "chart", "config": {...}},
            ...
        ]
    }
    """
    
    def __init__(self):
        self.buffer = ""                    # Accumulates incoming characters
        self.state = ParserState.INIT
        
        # Depth tracking
        self.root_depth = 0                 # Depth in root object
        self.component_depth = 0            # Depth within current component
        self.array_depth = 0                # Depth in arrays
        
        # String state tracking
        self.in_string = False              # Are we inside a string?
        self.escape_next = False            # Is next char escaped?
        self.current_string_start = -1      # Start position of current string
        
        # Component tracking
        self.summary_extracted = False      # Have we yielded summary?
        self.in_summary_value = False       # Are we currently in summary string?
        self.summary_start_pos = -1         # Start position of summary value
        self.component_start_pos = -1       # Start of current component
        self.components_yielded = 0         # Number of components yielded
        
        # Position tracking for error reporting
        self.position = 0                   # Current character position
        self.line = 1                       # Current line number
        self.column = 0                     # Current column number
        
        # Recovery state
        self.last_valid_state = None        # For error recovery
        self.error_count = 0                # Track parsing errors
        
    def feed(self, chunk: str) -> list:
        """
        Feed new chunk of data and return list of completed objects.
        
        Args:
            chunk: String chunk from OpenAI stream
            
        Returns:
            List of dicts with:
            - {"type": "summary", "content": "..."}  # Complete summary
            - {"type": "summary_partial", "content": "..."}  # Partial summary
            - {"type": "component", "data": {...}}
            - {"type": "error", "message": "..."}
        """
        results = []
        
        for char in chunk:
            self.position += 1
            self.column += 1
            
            if char == '\n':
                self.line += 1
                self.column = 0
            
            self.buffer += char
            
            try:
                # Process character based on current state
                completed = self._process_char(char)
                if completed:
                    results.append(completed)
                    
            except Exception as e:
                self.error_count += 1
                results.append({
                    "type": "error",
                    "message": f"Parse error at line {self.line}, col {self.column}: {str(e)}",
                    "recoverable": self.error_count < 5
                })
                
                # Attempt recovery
                if self.error_count < 5:
                    self._attempt_recovery()
                else:
                    # Too many errors, give up
                    results.append({
                        "type": "fatal_error",
                        "message": "Too many parsing errors, aborting stream"
                    })
                    break
        
        return results
    
    def _process_char(self, char: str):
        """
        Process a single character and return completed object if any.
        
        Returns:
            Dict with completed object or None
        """
        # Handle escape sequences first
        if self.escape_next:
            self.escape_next = False
            return None
        
        if char == '\\' and self.in_string:
            self.escape_next = True
            return None
        
        # Handle string boundaries
        if char == '"' and not self.escape_next:
            if self.in_string:
                # Exiting string
                self.in_string = False
                
                # Check if we were in the summary value
                if self.in_summary_value:
                    self.in_summary_value = False
                
                return self._check_summary_complete()
            else:
                # Entering string - check if it's the summary value
                self.in_string = True
                self.current_string_start = self.position
                
                # Check if this is the start of the summary value
                if not self.summary_extracted and '"summary"' in self.buffer[-20:]:
                    # Look back to see if we just passed "summary":
                    context = self.buffer[-30:]
                    if ':' in context and context.rindex(':') > context.rfind('"summary"'):
                        self.in_summary_value = True
                        self.summary_start_pos = self.position
            return None
        
        # If we're inside a string, check if we should yield partial summary
        if self.in_string:
            if self.in_summary_value and not self.summary_extracted:
                # Yield partial summary every ~20 characters or on punctuation
                if (self.position - self.summary_start_pos) % 20 == 0 or char in '.!?,;':
                    return self._extract_partial_summary()
            return None
        
        # Process structural characters
        if char == '{':
            return self._handle_open_brace()
        elif char == '}':
            return self._handle_close_brace()
        elif char == '[':
            return self._handle_open_bracket()
        elif char == ']':
            return self._handle_close_bracket()
        elif char == ',':
            return self._handle_comma()
        
        return None
    
    def _handle_open_brace(self):
        """Handle opening brace {"""
        if self.state == ParserState.INIT:
            self.state = ParserState.IN_ROOT_OBJECT
            self.root_depth = 1
            
        elif self.state == ParserState.IN_ROOT_OBJECT:
            self.root_depth += 1
            
        elif self.state == ParserState.IN_COMPONENTS_ARRAY:
            if self.component_depth == 0:
                # Starting a new component
                self.component_start_pos = self.position - 1
                self.state = ParserState.IN_COMPONENT_OBJECT
            self.component_depth += 1
            
        elif self.state == ParserState.IN_COMPONENT_OBJECT:
            self.component_depth += 1
        
        return None
    
    def _handle_close_brace(self):
        """Handle closing brace }"""
        if self.state == ParserState.IN_ROOT_OBJECT:
            self.root_depth -= 1
            if self.root_depth == 0:
                self.state = ParserState.COMPLETE
                
        elif self.state == ParserState.IN_COMPONENT_OBJECT:
            self.component_depth -= 1
            if self.component_depth == 0:
                # Component complete!
                return self._extract_component()
        
        return None
    
    def _handle_open_bracket(self):
        """Handle opening bracket ["""
        if self.state == ParserState.IN_ROOT_OBJECT:
            # Check if this is the components array
            if '"components"' in self.buffer[-30:]:
                self.state = ParserState.IN_COMPONENTS_ARRAY
                self.array_depth = 1
        
        elif self.state in [ParserState.IN_COMPONENTS_ARRAY, ParserState.IN_COMPONENT_OBJECT]:
            self.array_depth += 1
        
        return None
    
    def _handle_close_bracket(self):
        """Handle closing bracket ]"""
        if self.state == ParserState.IN_COMPONENTS_ARRAY:
            self.array_depth -= 1
            if self.array_depth == 0:
                # Exited components array
                self.state = ParserState.IN_ROOT_OBJECT
        
        elif self.state == ParserState.IN_COMPONENT_OBJECT:
            self.array_depth -= 1
        
        return None
    
    def _handle_comma(self):
        """Handle comma ,"""
        # Commas between components in array
        if self.state == ParserState.IN_COMPONENTS_ARRAY and self.component_depth == 0:
            # Ready for next component
            pass
        
        return None
    
    def _extract_partial_summary(self):
        """Extract partial summary text from buffer"""
        if self.summary_extracted or self.summary_start_pos < 0:
            return None
        
        # Extract text from summary start to current position
        # Look for the opening quote of the summary value
        pattern = r'"summary"\s*:\s*"([^"]*)'
        match = re.search(pattern, self.buffer)
        
        if match:
            partial_text = match.group(1)
            # Basic unescape
            try:
                partial_text = partial_text.replace('\\n', '\n')
                partial_text = partial_text.replace('\\t', '\t')
                partial_text = partial_text.replace('\\"', '"')
                partial_text = partial_text.replace('\\\\', '\\')
            except Exception:
                pass
            
            # Only yield if we have meaningful content (more than just whitespace)
            if partial_text.strip():
                return {
                    "type": "summary_partial",
                    "content": partial_text
                }
        
        return None
    
    def _check_summary_complete(self):
        """Check if we just completed the summary string"""
        if self.summary_extracted:
            return None
        
        # Look for pattern: "summary": "text content"
        # We just closed a string, check if it's the summary value
        pattern = r'"summary"\s*:\s*"([^"\\]*(?:\\.[^"\\]*)*)"'
        match = re.search(pattern, self.buffer)
        
        if match:
            summary_text = match.group(1)
            # Unescape the string
            try:
                # Handle common escape sequences
                summary_text = summary_text.replace('\\n', '\n')
                summary_text = summary_text.replace('\\t', '\t')
                summary_text = summary_text.replace('\\"', '"')
                summary_text = summary_text.replace('\\\\', '\\')
            except Exception:
                # If unescaping fails, use as-is
                pass
            
            self.summary_extracted = True
            self.in_summary_value = False  # Reset flag
            return {
                "type": "summary",
                "content": summary_text
            }
        
        return None
    
    def _extract_component(self):
        """Extract a complete component object"""
        if self.component_start_pos < 0:
            return None
        
        # Extract component JSON from buffer
        component_json = self.buffer[self.component_start_pos:self.position]
        
        try:
            component_data = json.loads(component_json)
            
            # Validate component structure
            if not isinstance(component_data, dict):
                raise ValueError("Component is not an object")
            
            if "type" not in component_data or "config" not in component_data:
                raise ValueError("Component missing 'type' or 'config'")
            
            self.components_yielded += 1
            self.component_start_pos = -1
            self.state = ParserState.IN_COMPONENTS_ARRAY
            
            return {
                "type": "component",
                "data": component_data,
                "index": self.components_yielded
            }
            
        except json.JSONDecodeError as e:
            # Component JSON is invalid, log but don't fail
            return {
                "type": "error",
                "message": f"Invalid component JSON: {str(e)}",
                "component_json": component_json[:100] + "..." if len(component_json) > 100 else component_json,
                "recoverable": True
            }
    
    def _attempt_recovery(self):
        """Attempt to recover from parsing error"""
        # Strategy: Look for the next structural marker
        # Find next unescaped {, }, [, or ]
        recovery_pos = self.position
        
        # Skip ahead to next likely boundary
        for i in range(self.position, len(self.buffer)):
            if self.buffer[i] in '{[':
                # Reset to this position
                self.buffer = self.buffer[i:]
                self.position = i
                break
    
    def get_partial_result(self) -> dict:
        """
        Attempt to extract partial result from incomplete stream.
        Used when stream ends unexpectedly.
        """
        result = {
            "summary_extracted": self.summary_extracted,
            "components_count": self.components_yielded,
            "buffer_size": len(self.buffer),
            "state": self.state.name
        }
        
        # Attempt to extract summary if not yet extracted
        if not self.summary_extracted:
            pattern = r'"summary"\s*:\s*"([^"]*)'
            match = re.search(pattern, self.buffer)
            if match:
                result["partial_summary"] = match.group(1)
        
        return result
    
    def is_complete(self) -> bool:
        """Check if parsing is complete"""
        return self.state == ParserState.COMPLETE
    
    def reset(self):
        """Reset parser for new stream"""
        self.__init__()
