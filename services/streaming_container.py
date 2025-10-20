"""
Streaming Container for Incremental UI Rendering

Manages Streamlit UI placeholders for real-time component rendering.
"""

import streamlit as st


class StreamingContainer:
    """
    Manages Streamlit UI placeholders for incremental rendering.
    
    Creates and updates placeholders as streaming data arrives.
    """
    
    def __init__(self):
        """Initialize container with placeholders"""
        # Summary section
        self.summary_container = st.container()
        with self.summary_container:
            self.summary_placeholder = st.empty()
            # Start with empty - will show partial text as it streams
            self.summary_placeholder.markdown("**💡** ✍️ *Generating...*")
        
        # Components section
        st.divider()
        self.components_container = st.container()
        
        # Component placeholders (created dynamically)
        self.component_placeholders = []
        
        # Loading indicator
        with self.components_container:
            self.loading_placeholder = st.empty()
            self.loading_placeholder.info("📊 Preparing visualizations...")
        
        # Status bar
        self.status_placeholder = st.empty()
        
        # Track state
        self.summary_shown = False
        self.components_count = 0
        self.last_partial_summary = ""
    
    def update_summary_partial(self, partial_text):
        """Update summary with partial streaming content"""
        # Only update if text has changed
        if partial_text != self.last_partial_summary:
            self.last_partial_summary = partial_text
            with self.summary_container:
                # Show partial text with cursor to indicate streaming
                self.summary_placeholder.markdown(f"**💡** {partial_text}▌")
    
    def update_summary(self, summary_text):
        """Update summary with final complete content"""
        with self.summary_container:
            self.summary_placeholder.markdown(f"**💡 {summary_text}**")
        self.summary_shown = True
        self.last_partial_summary = summary_text
    
    def add_component(self, component_data, renderer):
        """
        Add a new component to the display.
        
        Args:
            component_data: Component configuration dict
            renderer: UIRenderer instance
        """
        # Remove loading indicator
        self.loading_placeholder.empty()
        
        # Create new placeholder for this component
        with self.components_container:
            component_placeholder = st.empty()
            self.component_placeholders.append(component_placeholder)
            
            # Render component using UIRenderer
            with component_placeholder.container():
                component_type = component_data.get("type")
                config = component_data.get("config", {})
                
                if component_type in renderer.component_map:
                    try:
                        renderer.component_map[component_type](config)
                    except Exception as e:
                        st.error(f"Error rendering {component_type}: {str(e)}")
                else:
                    st.warning(f"Unknown component type: {component_type}")
            
            # Add new loading indicator below
            self.loading_placeholder = st.empty()
            self.loading_placeholder.info(f"📊 Generating next visualization...")
        
        self.components_count += 1
    
    def update_status(self, message, status_type="info"):
        """Update status bar"""
        with self.status_placeholder:
            if status_type == "info":
                st.info(message)
            elif status_type == "success":
                st.success(message)
            elif status_type == "warning":
                st.warning(message)
            elif status_type == "error":
                st.error(message)
    
    def show_complete(self):
        """Show completion state"""
        self.loading_placeholder.empty()
        self.status_placeholder.empty()
        
        # Show completion message briefly
        if self.components_count > 0:
            with self.components_container:
                completion_msg = st.empty()
                completion_msg.success(f"✓ Analysis complete! Generated {self.components_count} visualization{'s' if self.components_count != 1 else ''}.")
    
    def show_error(self, error_message):
        """Show error state"""
        self.loading_placeholder.empty()
        with self.components_container:
            st.error(f"❌ {error_message}")
    
    def clear(self):
        """Clear all placeholders"""
        self.summary_placeholder.empty()
        for placeholder in self.component_placeholders:
            placeholder.empty()
        self.loading_placeholder.empty()
        self.status_placeholder.empty()
