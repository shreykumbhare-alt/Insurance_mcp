"""
Advanced UI Components and Styling Utilities for ClaimPilot Chatbot
This module provides reusable components and styling functions for enhanced UI.
"""

from typing import Dict, List, Optional, Tuple
import streamlit as st


class UITheme:
    """Color theme manager for the chatbot UI."""
    
    # Primary Colors
    PRIMARY = "#2563eb"
    PRIMARY_DARK = "#1e40af"
    PRIMARY_LIGHT = "#dbeafe"
    
    # Secondary Colors
    SECONDARY = "#10b981"
    SECONDARY_DARK = "#059669"
    SECONDARY_LIGHT = "#d1fae5"
    
    # Status Colors
    SUCCESS = "#10b981"
    WARNING = "#f59e0b"
    DANGER = "#ef4444"
    INFO = "#2563eb"
    
    # Backgrounds
    BG_DARK = "#0f172a"
    BG_LIGHT = "#f8fafc"
    BG_WHITE = "#ffffff"
    
    # Text Colors
    TEXT_DARK = "#0f172a"
    TEXT_LIGHT = "#64748b"
    TEXT_MUTED = "#94a3b8"
    
    # Borders
    BORDER_LIGHT = "#e2e8f0"
    BORDER_DARK = "#cbd5e1"
    
    @classmethod
    def get_status_color(cls, status: str) -> str:
        """Get color for status badge."""
        status_map = {
            "success": cls.SUCCESS,
            "warning": cls.WARNING,
            "danger": cls.DANGER,
            "info": cls.INFO,
            "online": cls.SUCCESS,
            "offline": cls.DANGER,
        }
        return status_map.get(status.lower(), cls.TEXT_MUTED)


class UIComponents:
    """Reusable UI components for the chatbot."""
    
    @staticmethod
    def render_status_badge(status: str, text: str = "") -> None:
        """Render a status badge with icon and text."""
        color = UITheme.get_status_color(status)
        display_text = text or status.upper()
        icon = "🟢" if "online" in status.lower() else "🔴"
        
        st.markdown(f"""
        <span class="status-badge {status.lower()}">
            {icon} {display_text}
        </span>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_metric_card(label: str, value: str, icon: str = "📊") -> None:
        """Render a metric card."""
        st.markdown(f"""
        <div style="background: #f8fafc; padding: 1.5rem; border-radius: 12px; 
                    border: 1px solid #e2e8f0; text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
            <div style="color: #94a3b8; font-size: 0.85rem; font-weight: 600; 
                        text-transform: uppercase; margin-bottom: 0.75rem;">
                {label}
            </div>
            <div style="font-size: 2rem; font-weight: 700; color: #2563eb;">
                {value}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_info_box(title: str, content: str, box_type: str = "info") -> None:
        """Render an information box."""
        type_colors = {
            "info": "#2563eb",
            "success": "#10b981",
            "warning": "#f59e0b",
            "error": "#ef4444",
        }
        
        color = type_colors.get(box_type, type_colors["info"])
        type_icons = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌",
        }
        icon = type_icons.get(box_type, "ℹ️")
        
        st.markdown(f"""
        <div style="background: rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.1);
                    border-left: 4px solid {color};
                    border-radius: 8px;
                    padding: 1rem 1.25rem;">
            <div style="font-weight: 700; color: #0f172a; margin-bottom: 0.5rem;">
                {icon} {title}
            </div>
            <div style="color: #475569; line-height: 1.6;">
                {content}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_divider() -> None:
        """Render a section divider."""
        st.markdown("""
        <div style="height: 1px; background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
                    margin: 2rem 0;"></div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_code_block(code: str, language: str = "json") -> None:
        """Render a formatted code block."""
        st.markdown(f"""
        <pre style="background: #f8fafc; padding: 1rem; border-radius: 8px;
                    border: 1px solid #e2e8f0; overflow-x: auto;
                    font-family: 'Fira Code', monospace; font-size: 0.9rem;
                    color: #0f172a; line-height: 1.5;">
        <code>{code}</code>
        </pre>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_progress_bar(value: float, label: str = "", max_value: float = 100) -> None:
        """Render a progress bar."""
        percentage = (value / max_value) * 100
        color = "#10b981" if percentage >= 70 else "#f59e0b" if percentage >= 40 else "#ef4444"
        
        st.markdown(f"""
        <div style="margin-bottom: 1rem;">
            {'<div style="color: #0f172a; font-weight: 600; margin-bottom: 0.5rem;">' + label + '</div>' if label else ''}
            <div style="background: #e2e8f0; border-radius: 8px; height: 8px; overflow: hidden;">
                <div style="background: {color}; width: {percentage}%; height: 100%; 
                            transition: width 0.3s ease; border-radius: 8px;"></div>
            </div>
            <div style="color: #94a3b8; font-size: 0.85rem; margin-top: 0.5rem;">
                {percentage:.0f}% Complete
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_tag_list(tags: List[str], tag_type: str = "default") -> None:
        """Render a list of tags/chips."""
        type_colors = {
            "default": ("#2563eb", "#dbeafe"),
            "success": ("#10b981", "#d1fae5"),
            "warning": ("#f59e0b", "#fef3c7"),
            "error": ("#ef4444", "#fee2e2"),
        }
        
        bg_color, text_color = type_colors.get(tag_type, type_colors["default"])
        
        tags_html = ""
        for tag in tags:
            tags_html += f"""
            <span style="display: inline-block; background: {text_color}; color: {bg_color};
                        padding: 0.35rem 0.75rem; border-radius: 20px; font-size: 0.85rem;
                        font-weight: 600; margin-right: 0.5rem; margin-bottom: 0.5rem;">
                {tag}
            </span>
            """
        
        st.markdown(f"""<div style="margin: 1rem 0;">{tags_html}</div>""", unsafe_allow_html=True)
    
    @staticmethod
    def render_loading_spinner(text: str = "Processing...") -> None:
        """Render a loading spinner animation."""
        st.markdown(f"""
        <div style="text-align: center; padding: 2rem;">
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
            <div style="color: #94a3b8; font-weight: 500; margin-top: 1rem;">
                {text}
            </div>
        </div>
        """, unsafe_allow_html=True)


class ChatUtilities:
    """Utility functions for chat operations."""
    
    @staticmethod
    def format_message_timestamp(timestamp: Optional[str] = None) -> str:
        """Format a message timestamp."""
        from datetime import datetime
        if timestamp:
            return timestamp
        return datetime.now().strftime("%H:%M")
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 100) -> str:
        """Truncate text with ellipsis."""
        if len(text) > max_length:
            return text[:max_length] + "..."
        return text
    
    @staticmethod
    def format_investigation_summary(result: Dict) -> str:
        """Format investigation result summary."""
        triage = result.get("triage", {})
        score = triage.get("fraud_score", "N/A")
        risk = triage.get("risk_level", "Unknown")
        action = triage.get("triage_action", "No recommendation")
        
        return f"""
        **Claim**: {result.get('claim_id', 'Unknown')}
        **Fraud Score**: {score}
        **Risk Level**: {risk}
        **Recommended Action**: {action}
        """
    
    @staticmethod
    def get_message_role_icon(role: str) -> str:
        """Get appropriate icon for message role."""
        icons = {
            "user": "👤",
            "assistant": "🤖",
            "system": "⚙️",
            "error": "❌",
            "success": "✅",
        }
        return icons.get(role, "💬")


class ValidationHelpers:
    """Input validation helpers."""
    
    @staticmethod
    def validate_claim_json(json_str: str) -> Tuple[bool, str]:
        """Validate claim JSON format."""
        import json
        try:
            data = json.loads(json_str)
            if not isinstance(data, dict):
                return False, "Claim data must be a JSON object"
            return True, ""
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {str(e)}"
    
    @staticmethod
    def validate_api_url(url: str) -> Tuple[bool, str]:
        """Validate API URL format."""
        import re
        url_pattern = r"^https?://[^\s/$.?#].[^\s]*$"
        if re.match(url_pattern, url):
            return True, ""
        return False, "Invalid URL format"
    
    @staticmethod
    def validate_claim_id(claim_id: str) -> Tuple[bool, str]:
        """Validate claim ID format."""
        if not claim_id or len(claim_id) < 3:
            return False, "Claim ID must be at least 3 characters"
        if len(claim_id) > 50:
            return False, "Claim ID must be less than 50 characters"
        return True, ""


class StyleInjector:
    """Inject custom CSS for advanced styling."""
    
    @staticmethod
    def inject_custom_scrollbar() -> None:
        """Inject custom scrollbar styling."""
        st.markdown("""
        <style>
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: #f1f5f9; }
        ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
        </style>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def inject_animations() -> None:
        """Inject animation keyframes."""
        st.markdown("""
        <style>
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        @keyframes shimmer {
            0% { background-position: -1000px 0; }
            100% { background-position: 1000px 0; }
        }
        </style>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def inject_responsive_styles() -> None:
        """Inject responsive design styles."""
        st.markdown("""
        <style>
        @media (max-width: 768px) {
            .message-bubble { max-width: 85%; }
            .stButton button { width: 100%; }
            .metric-grid { grid-template-columns: 1fr; }
        }
        
        @media (max-width: 480px) {
            .chat-container { padding: 0.5rem; }
            .message-bubble { max-width: 90%; }
            .header-title { font-size: 1.5rem; }
        }
        </style>
        """, unsafe_allow_html=True)


# Example usage documentation
"""
USAGE EXAMPLES:

# Render a status badge
UIComponents.render_status_badge("online", "API Connection Active")

# Render metric cards
col1, col2, col3 = st.columns(3)
with col1:
    UIComponents.render_metric_card("Fraud Score", "87.5", "🚨")
with col2:
    UIComponents.render_metric_card("Risk Level", "HIGH", "⚠️")
with col3:
    UIComponents.render_metric_card("Action", "Review", "👁️")

# Render info boxes
UIComponents.render_info_box("Investigation Complete", 
                             "The claim has been analyzed and flagged for review.",
                             "success")

# Render dividers
UIComponents.render_divider()

# Render progress bar
UIComponents.render_progress_bar(75, "Investigation Progress", 100)

# Render tags
UIComponents.render_tag_list(["High Risk", "Auto Insurance", "Needs Review"], "warning")

# Format investigation summary
summary = ChatUtilities.format_investigation_summary(investigation_result)

# Validate inputs
is_valid, error_msg = ValidationHelpers.validate_claim_json(json_string)
if not is_valid:
    st.error(error_msg)

# Inject custom styles
StyleInjector.inject_custom_scrollbar()
StyleInjector.inject_animations()
StyleInjector.inject_responsive_styles()
"""
