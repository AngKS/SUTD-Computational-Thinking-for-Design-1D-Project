import streamlit as st
import pandas as pd

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
