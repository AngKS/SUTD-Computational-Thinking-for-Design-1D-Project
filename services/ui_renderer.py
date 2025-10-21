import streamlit as st
import pandas as pd
import traceback

class UIRenderer:
    def __init__(self):
        """Initialize the UI renderer with component mapping"""
        self.component_map = {
            'metric': self._render_metric,
            'markdown': self._render_markdown,
            'dataframe': self._render_dataframe,
            'bar_chart': self._render_bar_chart,
            'line_chart': self._render_line_chart,
            'area_chart': self._render_area_chart,
            'scatter_chart': self._render_scatter_chart
        }
    
    def render(self, gpt_response):
        """Render the complete response from GPT"""
        if not gpt_response:
            st.error("No response to render")
            return
        
        # Display summary
        if "summary" in gpt_response:
            st.markdown(f"**💡 {gpt_response['summary']}**")
            st.divider()
        
        # Render components
        components = gpt_response.get("components", [])
        if not components:
            st.info("No visualizations to display")
            return
        
        for idx, component in enumerate(components):
            try:
                component_type = component.get("type")
                config = component.get("config", {})
                
                if component_type in self.component_map:
                    self.component_map[component_type](config)
                else:
                    st.warning(f"Unknown component type: {component_type}")
            
            except Exception as e:
                st.error(f"Error rendering component {idx + 1}: {str(e)}")
    
    def render_streaming(self, stream_generator):
        """
        Render components incrementally as they arrive from stream.
        
        Args:
            stream_generator: Generator yielding stream results
            
        Returns:
            Dict with final response data (for caching)
        """
        from services.streaming_container import StreamingContainer
        
        # Create streaming container
        container = StreamingContainer()
        
        # Track final response for caching
        final_response = {
            "summary": None,
            "components": []
        }
        
        try:
            for result in stream_generator:
                result_type = result.get("type")
                
                if result_type == "summary_partial":
                    # Display partial summary as it streams
                    partial_text = result.get("content", "")
                    container.update_summary_partial(partial_text)
                
                elif result_type == "summary":
                    # Display complete summary
                    summary_text = result.get("content", "")
                    container.update_summary(summary_text)
                    final_response["summary"] = summary_text
                    
                elif result_type == "component":
                    # Display component
                    component_data = result.get("data", {})
                    component_index = result.get("index", 0)
                    
                    container.add_component(component_data, self)
                    final_response["components"].append(component_data)
                    
                    # Update status (silent - no visible update to avoid clutter)
                    # container.update_status(
                    #     f"Rendered component {component_index}",
                    #     status_type="info"
                    # )
                    
                elif result_type == "error":
                    # Display error
                    error_msg = result.get("message", "Unknown error")
                    is_fatal = result.get("fatal", False)
                    
                    container.show_error(error_msg)
                    
                    if is_fatal:
                        break
                        
                elif result_type == "warning":
                    # Display warning
                    warning_msg = result.get("message", "")
                    container.update_status(warning_msg, status_type="warning")
                    
                elif result_type == "complete":
                    # Stream complete
                    container.show_complete()
                    
                elif result_type == "cancelled":
                    # User cancelled
                    container.update_status(
                        "⏸️ Generation stopped by user",
                        status_type="warning"
                    )
                    break
            
            return final_response
            
        except Exception as e:
            container.show_error(f"Rendering error: {str(e)}")
            with st.expander("Error Details"):
                st.code(traceback.format_exc())
            return final_response
    
    def _render_metric(self, config):
        """Render a metric component"""
        label = config.get("label", "Metric")
        value = config.get("value")
        delta = config.get("delta")
        delta_color = config.get("delta_color", "normal")
        
        # Create columns for better layout
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.metric(
                label=label,
                value=value,
                delta=delta,
                delta_color=delta_color
            )
    
    def _render_markdown(self, config):
        """Render markdown content"""
        content = config.get("content", "")
        st.markdown(content)
    
    def _render_dataframe(self, config):
        """Render a dataframe"""
        title = config.get("title")
        data = config.get("data")
        hide_index = config.get("hide_index", True)
        
        if title:
            st.subheader(title)
        
        if not data:
            st.info("No data to display")
            return
        
        # Convert to DataFrame
        try:
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                df = pd.DataFrame(data)
            else:
                st.error("Invalid data format for dataframe")
                return
            
            st.dataframe(df, use_container_width=True, hide_index=hide_index)
        
        except Exception as e:
            st.error(f"Error creating dataframe: {str(e)}")
    
    def _render_bar_chart(self, config):
        """Render a bar chart using Streamlit's native st.bar_chart()"""
        title = config.get("title")
        data = config.get("data")
        x = config.get("x")
        y = config.get("y")
        color = config.get("color")
        x_label = config.get("x_label")
        y_label = config.get("y_label")
        horizontal = config.get("horizontal", False)
        stack = config.get("stack")
        
        if title:
            st.subheader(title)
        
        if not data:
            st.info("No data to display")
            return
        
        try:
            # Convert to DataFrame
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                df = pd.DataFrame(data)
            else:
                st.error("Invalid data format for bar chart")
                return
            
            # Use Streamlit's native bar chart with parameters
            st.bar_chart(
                df,
                x=x,
                y=y,
                color=color,
                x_label=x_label,
                y_label=y_label,
                horizontal=horizontal,
                stack=stack,
                use_container_width=True
            )
        
        except Exception as e:
            st.error(f"Error creating bar chart: {str(e)}")
    
    def _render_line_chart(self, config):
        """Render a line chart using Streamlit's native st.line_chart()"""
        title = config.get("title")
        data = config.get("data")
        x = config.get("x")
        y = config.get("y")
        color = config.get("color")
        x_label = config.get("x_label")
        y_label = config.get("y_label")
        
        if title:
            st.subheader(title)
        
        if not data:
            st.info("No data to display")
            return
        
        try:
            # Convert to DataFrame
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                df = pd.DataFrame(data)
            else:
                st.error("Invalid data format for line chart")
                return
            
            # Use Streamlit's native line chart with parameters
            st.line_chart(
                df,
                x=x,
                y=y,
                color=color,
                x_label=x_label,
                y_label=y_label,
                use_container_width=True
            )
        
        except Exception as e:
            st.error(f"Error creating line chart: {str(e)}")
    
    def _render_area_chart(self, config):
        """Render an area chart using Streamlit's native st.area_chart()"""
        title = config.get("title")
        data = config.get("data")
        x = config.get("x")
        y = config.get("y")
        color = config.get("color")
        x_label = config.get("x_label")
        y_label = config.get("y_label")
        stack = config.get("stack")
        
        if title:
            st.subheader(title)
        
        if not data:
            st.info("No data to display")
            return
        
        try:
            # Convert to DataFrame
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                df = pd.DataFrame(data)
            else:
                st.error("Invalid data format for area chart")
                return
            
            # Use Streamlit's native area chart with parameters
            st.area_chart(
                df,
                x=x,
                y=y,
                color=color,
                x_label=x_label,
                y_label=y_label,
                stack=stack,
                use_container_width=True
            )
        
        except Exception as e:
            st.error(f"Error creating area chart: {str(e)}")
    
    def _render_scatter_chart(self, config):
        """Render a scatter chart using Streamlit's native st.scatter_chart()"""
        title = config.get("title")
        data = config.get("data")
        x = config.get("x")
        y = config.get("y")
        color = config.get("color")
        size = config.get("size")
        x_label = config.get("x_label")
        y_label = config.get("y_label")
        
        if title:
            st.subheader(title)
        
        if not data:
            st.info("No data to display")
            return
        
        try:
            # Convert to DataFrame
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                df = pd.DataFrame(data)
            else:
                st.error("Invalid data format for scatter chart")
                return
            
            # Use Streamlit's native scatter chart with parameters
            st.scatter_chart(
                df,
                x=x,
                y=y,
                color=color,
                size=size,
                x_label=x_label,
                y_label=y_label,
                use_container_width=True
            )
        
        except Exception as e:
            st.error(f"Error creating scatter chart: {str(e)}")
