import streamlit as st
import pandas as pd
import traceback
from models.Page import Page
from models.App import MultiPageApp
from utils import read_data, write_data
import auth

class AdminPage(Page):
    def __init__(self, _app: MultiPageApp):
        super().__init__(title="Admin", icon="🛠️")
        self.app = _app
        self.transactions = read_data('transactions.json')
        self.inventory = read_data('inventory.json')
        self.promocodes = read_data('promocodes.json')
        
        # Initialize AI services
        try:
            from services.ai_query_service import AIQueryService
            from services.ui_renderer import UIRenderer
            self.ai_service = AIQueryService()
            self.ui_renderer = UIRenderer()
            self.ai_enabled = True
        except Exception as e:
            self.ai_enabled = False
            self.ai_error = str(e)

    @property
    def logged_in(self):
        """Check if user is logged in using auth module"""
        return auth.is_logged_in()

    def login_form(self):
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            if submitted:
                if auth.login(username, password):
                    st.success("Logged in successfully!")
                    st.rerun()  # Refresh the page to show admin content
                else:
                    st.error("Invalid credentials. Please try again.")

    def logout_button(self):
        """Display logout button"""
        if st.button("Logout", key="admin_logout"):
            auth.logout()
            st.success("Logged out successfully!")
            st.rerun()


    def inventory_management(self):
        st.header("Inventory Management")
        # create a dataframe from inventory
        if not self.inventory:
            st.info("No inventory data available.")
            return
        df = st.data_editor(self.inventory["products"])
        # check for changes and update inventory
        if df != self.inventory["products"]:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.info("Changes detected in inventory.")
            with col2:
                if st.button("Save Changes"):
                    self.inventory["products"] = df
                    success = write_data('inventory.json', self.inventory)
                    if success:
                        st.success("Inventory updated successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to update inventory.")

    def transaction_management(self):
        
        st.header("Transaction Management")
        if not self.transactions or "transactions" not in self.transactions:
            st.info("No transaction data available.")
            return

        transactions_list = self.transactions["transactions"]

        if not transactions_list:
            st.info("No transactions recorded yet.")
            return

        st.subheader("Summary Statistics")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Transactions", len(transactions_list))
        with col2:
            total_revenue = sum(t.get("total_amount", 0) for t in transactions_list)
            st.metric("Total Revenue", f"${total_revenue:.2f}")
        with col3:
            avg_order = total_revenue / len(transactions_list) if transactions_list else 0
            st.metric("Average Order", f"${avg_order:.2f}")
        # Search and filter options
        col1, col2 = st.columns(2)
        with col1:
            search_term = st.text_input("Search by Transaction ID, Customer Email, or Name", "")


        # Filter transactions based on search
        filtered_transactions = transactions_list
        if search_term:
            search_term_lower = search_term.lower()
            filtered_transactions = [
                t for t in filtered_transactions
                if search_term_lower in t.get("transaction_id", "").lower()
                or search_term_lower in t.get("customer", {}).get("email", "").lower()
                or search_term_lower in t.get("customer", {}).get("name", "").lower()
            ]
        st.info(f"Showing {len(filtered_transactions)} of {len(transactions_list)} transactions")

        st.divider()

        # Display transactions
        if not filtered_transactions:
            st.warning("No transactions match your search criteria.")
            return
        
        # sort transactions by date descending
        filtered_transactions.sort(key=lambda x: x.get('date', ''), reverse=True)
        

        container = st.container(height=1000)
        with container:
            for idx, transaction in enumerate(filtered_transactions):
                transaction_id = transaction.get('transaction_id', 'N/A')
                with st.expander(
                    f"🧾 Transaction<{transaction_id}> - ${transaction.get('total_amount', 0):.2f}",
                    expanded=(idx == 0)  # Expand first transaction by default
                ):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**📋 Transaction Details**")
                        st.write(f"**ID:** `{transaction_id}`")
                        st.write(f"**Date:** {transaction.get('date', 'N/A')}")
                        promo_code = transaction.get('promo_code')
                        if promo_code:
                            st.write(f"**Promo Code:** {promo_code}")
                        else:
                            st.write("**Promo Code:** None")
                        st.write(f"**Total Amount:** ${transaction.get('total_amount', 0):.2f}")
                    
                    with col2:
                        st.markdown("**👤 Customer Information**")
                        customer = transaction.get('customer', {})
                        st.write(f"**Name:** {customer.get('name', 'N/A')}")
                        st.write(f"**Email:** {customer.get('email', 'N/A')}")
                        st.write(f"**Address:** {customer.get('address', 'N/A')}")
                        st.write(f"**Country:** {customer.get('country', 'N/A')}")
                    
                    st.markdown("---")
                    st.markdown("**🛒 Items Purchased**")
                    
                    items = transaction.get('items', [])
                    if items:
                        # Create a table view of items
                        items_df = pd.DataFrame(items)
                        # Reorder columns for better display
                        if not items_df.empty:
                            column_order = ['product_id', 'name', 'quantity', 'price']
                            items_df = items_df[[col for col in column_order if col in items_df.columns]]
                            # Format price column
                            if 'price' in items_df.columns:
                                items_df['price'] = items_df['price'].apply(lambda x: f"${x:.2f}")
                            st.dataframe(items_df, use_container_width=True, hide_index=True)
                            
                            # Calculate subtotal
                            subtotal = sum(item.get('price', 0) * item.get('quantity', 0) for item in items)
                            st.write(f"**Subtotal:** ${subtotal:.2f}")
                    else:
                        st.info("No items in this transaction.")
                    
                    # Delete button for this transaction
                    st.markdown("---")
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col3:
                        if st.button(f"🗑️ Delete Transaction", key=f"delete_{transaction_id}", type="secondary"):
                            # Confirm deletion
                            st.session_state[f"confirm_delete_{transaction_id}"] = True
                            st.rerun()
                    
                    # Confirmation dialog
                    if st.session_state.get(f"confirm_delete_{transaction_id}", False):
                        st.warning("⚠️ Are you sure you want to delete this transaction? This action cannot be undone!")
                        col1, col2, col3 = st.columns([2, 1, 1])
                        with col2:
                            if st.button("Cancel", key=f"cancel_{transaction_id}"):
                                del st.session_state[f"confirm_delete_{transaction_id}"]
                                st.rerun()
                        with col3:
                            if st.button("✓ Confirm Delete", key=f"confirm_{transaction_id}", type="primary"):
                                # Delete the transaction
                                self.transactions["transactions"] = [
                                    t for t in self.transactions["transactions"]
                                    if t.get('transaction_id') != transaction_id
                                ]
                                if write_data('transactions.json', self.transactions):
                                    del st.session_state[f"confirm_delete_{transaction_id}"]
                                    st.success(f"Transaction {transaction_id[:8]}... deleted successfully!")
                                    st.rerun()
                                else:
                                    st.error("Failed to delete transaction. Please try again.")

        st.divider()

        # Export option
        if st.button("📥 Export All Transactions to CSV"):
            # Flatten transactions for export
            export_data = []
            for t in transactions_list:
                customer = t.get('customer', {})
                for item in t.get('items', []):
                    export_data.append({
                        'Transaction ID': t.get('transaction_id', ''),
                        'Date': t.get('date', ''),
                        'Customer Name': customer.get('name', ''),
                        'Customer Email': customer.get('email', ''),
                        'Customer Address': customer.get('address', ''),
                        'Country': customer.get('country', ''),
                        'Product ID': item.get('product_id', ''),
                        'Product Name': item.get('name', ''),
                        'Quantity': item.get('quantity', 0),
                        'Unit Price': item.get('price', 0),
                        'Promo Code': t.get('promo_code', ''),
                        'Total Amount': t.get('total_amount', 0)
                    })

            if export_data:
                df_export = pd.DataFrame(export_data)
                csv = df_export.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="transactions_export.csv",
                    mime="text/csv"
                )
                st.success("Ready to download!")

    def promocode_management(self):
        st.header("Promotional Code Management")
        if not self.promocodes:
            st.info("No promotional code data available.")
            return
        df = st.data_editor(self.promocodes["codes"])
        if df != self.promocodes["codes"]:
            if st.button("Save Promo Code Changes"):
                self.promocodes["codes"] = df
                write_data('promocodes.json', self.promocodes)
                st.success("Promotional codes updated successfully!")

    def main_dashboard(self):
        # AI Analytics Section
        self._render_ai_analytics()
    
    def _render_ai_analytics(self):
        """Render the generative UI analytics section with streaming support"""
        st.subheader("🤖 AI Analytics Assistant")
        st.caption("Ask questions about your store data in natural language")
        
        # Check if AI is enabled
        if not self.ai_enabled:
            st.warning(f"⚠️ AI Analytics is currently unavailable: {self.ai_error}")
            with st.expander("ℹ️ How to enable AI Analytics"):
                st.markdown("""
                1. Create a `.env` file in the project root
                2. Add your OpenAI API key: `OPENAI_API_KEY=your_key_here`
                3. Get an API key from [platform.openai.com](https://platform.openai.com)
                4. Restart the application
                """)
            return
        
        # Initialize session state for streaming
        if 'streaming_active' not in st.session_state:
            st.session_state.streaming_active = False
        if 'stop_stream' not in st.session_state:
            st.session_state.stop_stream = False
        
        # Data source selector and examples toggle
        col1, col2 = st.columns([3, 1])
        with col1:
            data_sources = st.multiselect(
                "Data sources to query:",
                ["Transactions", "Inventory", "Promo Codes"],
                default=["Transactions"],
                key="ai_data_sources",
                disabled=st.session_state.streaming_active  # Disable during streaming
            )
        with col2:
            st.write("")  # Spacing
            show_examples = st.toggle(
                "Show examples",
                value=False,
                key="show_examples",
                disabled=st.session_state.streaming_active
            )
        
        # Example queries (collapsible)
        if show_examples and not st.session_state.streaming_active:
            with st.expander("📝 Example Questions", expanded=True):
                example_queries = [
                    "What are the top 5 best-selling products?",
                    "Show me total revenue by product category",
                    "Which customers spent the most?",
                    "Which products are low in stock?",
                    "How many times was each promo code used?",
                    "What is the average order value?"
                ]
                cols = st.columns(2)
                for i, example in enumerate(example_queries):
                    with cols[i % 2]:
                        if st.button(f"💡 {example}", key=f"example_{i}", use_container_width=True):
                            # Delete the key first, then let the widget recreate it with the new value
                            if 'ai_query_input' in st.session_state:
                                del st.session_state['ai_query_input']
                            # Store the example to be used as default value
                            st.session_state.ai_query_prefill = example
                            st.rerun()
        
        # Query input - use prefill value if available
        prefill_value = st.session_state.pop('ai_query_prefill', '')
        user_query = st.text_area(
            "Your question:",
            value=prefill_value,
            placeholder="e.g., What are the top 5 best-selling products?",
            height=100,
            key="ai_query_input",
            disabled=st.session_state.streaming_active
        )
        
        # Submit and clear buttons
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if not st.session_state.streaming_active:
                analyze_button = st.button(
                    "🔍 Analyze",
                    type="primary",
                    use_container_width=True
                )
            else:
                analyze_button = False
                
        with col2:
            if st.session_state.streaming_active:
                # Show stop button during streaming
                if st.button("⏹️ Stop", type="secondary", use_container_width=True):
                    st.session_state.stop_stream = True
                    st.session_state.streaming_active = False
                    st.rerun()
            else:
                # Show clear button when not streaming
                if st.button("🗑️ Clear", use_container_width=True):
                    # Delete the session state key to clear the widget
                    if 'ai_query_input' in st.session_state:
                        del st.session_state['ai_query_input']
                    if 'ai_response' in st.session_state:
                        del st.session_state['ai_response']
                    if 'ai_cache' in st.session_state:
                        st.session_state.ai_cache = {}
                    st.rerun()
        
        # Process query with streaming
        if analyze_button and user_query.strip():
            st.session_state.streaming_active = True
            st.session_state.stop_stream = False
            self._process_ai_query_streaming(user_query, data_sources)
            st.session_state.streaming_active = False
    
    def _process_ai_query(self, query, data_sources):
        """Process AI query and store results in session state (non-streaming fallback)"""
        if not data_sources:
            st.warning("⚠️ Please select at least one data source to query.")
            return
        
        # Check for cached response
        cache_key = f"{query}_{'-'.join(sorted(data_sources))}"
        if 'ai_cache' not in st.session_state:
            st.session_state.ai_cache = {}
        
        # Use cached response if available
        if cache_key in st.session_state.ai_cache:
            st.session_state.ai_response = st.session_state.ai_cache[cache_key]
            st.info("📦 Loaded from cache")
            return  # Don't rerun, just display the cached result
        
        with st.spinner("🤔 Analyzing your data..."):
            try:
                # Prepare data context from already-loaded data
                data_context = self._prepare_data_for_ai(data_sources)
                
                # Query AI service
                response = self.ai_service.query(query, data_context)
                
                # Store in session state and cache
                st.session_state.ai_response = response
                st.session_state.ai_cache[cache_key] = response
                
                # Limit cache size to 10 entries
                if len(st.session_state.ai_cache) > 10:
                    # Remove oldest entry
                    oldest_key = next(iter(st.session_state.ai_cache))
                    del st.session_state.ai_cache[oldest_key]
                
                st.success("✓ Analysis complete!")
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                with st.expander("Error Details"):
                    st.code(traceback.format_exc())
    
    def _process_ai_query_streaming(self, query, data_sources):
        """Process AI query with streaming and real-time UI updates"""
        if not data_sources:
            st.warning("⚠️ Please select at least one data source to query.")
            return
        
        # Check cache
        cache_key = f"{query}_{'-'.join(sorted(data_sources))}"
        if 'ai_cache' not in st.session_state:
            st.session_state.ai_cache = {}
        
        # Use cached response if available
        if cache_key in st.session_state.ai_cache:
            st.session_state.ai_response = st.session_state.ai_cache[cache_key]
            st.info("📦 Loaded from cache")
            st.session_state.streaming_active = False
            st.rerun()
            return
        
        # Show streaming indicator
        st.divider()
        st.subheader("📊 Live Analysis")
        
        # Prepare data context
        data_context = self._prepare_data_for_ai(data_sources)
        
        # Create stop signal callback
        def check_stop_signal():
            return st.session_state.get('stop_stream', False)
        
        try:
            # Start streaming
            stream_generator = self.ai_service.query_stream_with_cancellation(
                query,
                data_context,
                check_stop_signal
            )
            
            # Render streaming results
            final_response = self.ui_renderer.render_streaming(stream_generator)
            
            # Cache the result if complete
            if final_response.get("summary") and final_response.get("components"):
                st.session_state.ai_response = final_response
                st.session_state.ai_cache[cache_key] = final_response
                
                # Limit cache size
                if len(st.session_state.ai_cache) > 10:
                    oldest_key = next(iter(st.session_state.ai_cache))
                    del st.session_state.ai_cache[oldest_key]
                
                # Show raw JSON response in expander
                with st.expander("🔍 View Raw JSON Response"):
                    st.json(final_response)
        
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            with st.expander("Error Details"):
                st.code(traceback.format_exc())
        
        finally:
            st.session_state.streaming_active = False
            st.session_state.stop_stream = False
    
    def _prepare_data_for_ai(self, sources):
        """Prepare data context from selected sources"""
        data_context = {}
        
        if "Transactions" in sources:
            data_context["transactions"] = self.transactions
        if "Inventory" in sources:
            data_context["inventory"] = self.inventory
        if "Promo Codes" in sources:
            data_context["promocodes"] = self.promocodes
        
        return data_context

    def display(self):
        if not self.logged_in:
            st.warning("Please log in to access admin features.")
            self.login_form()
        else:
            # Display logout button in sidebar or at top
            col1, col2 = st.columns([5, 1])
            with col1:
                st.title("Admin Panel")
            with col2:
                self.logout_button()
            user_info = auth.get_current_user()
            if user_info:
                st.info(f"Logged in as: {user_info.get('username', 'Unknown')}")
            # Summary statistics
            tab1, tab2, tab3, tab4 = st.tabs(["♾️ Generative Analytics", "🧾 Transactions", "📦 Inventory", "🎁 Discount Codes"])
            with tab1:
                self.main_dashboard()
            with tab2:
                self.transaction_management()
            with tab3:
                self.inventory_management()
            with tab4:
                self.promocode_management()
