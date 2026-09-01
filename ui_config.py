"""
ClaimPilot Chatbot UI Configuration and Theme Settings
This module contains all configurable settings for the chatbot interface.
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum


class ColorScheme(Enum):
    """Available color schemes for the chatbot."""
    
    PROFESSIONAL = "professional"  # Blue and green
    DARK = "dark"                  # Dark mode
    LIGHT = "light"                # Light mode
    VIBRANT = "vibrant"            # Bold colors
    MINIMAL = "minimal"            # Subtle colors


@dataclass
class Color:
    """Color definition with hex code."""
    name: str
    hex: str
    
    def rgb(self) -> Tuple[int, int, int]:
        """Convert hex to RGB."""
        hex_color = self.hex.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def rgba(self, alpha: float = 1.0) -> str:
        """Get RGBA representation."""
        r, g, b = self.rgb()
        return f"rgba({r}, {g}, {b}, {alpha})"


class ThemeConfig:
    """Configuration for different color themes."""
    
    # Professional Theme (Default)
    PROFESSIONAL = {
        "name": "Professional",
        "primary": "#2563eb",
        "primary_dark": "#1e40af",
        "primary_light": "#dbeafe",
        "secondary": "#10b981",
        "secondary_dark": "#059669",
        "secondary_light": "#d1fae5",
        "success": "#10b981",
        "warning": "#f59e0b",
        "danger": "#ef4444",
        "info": "#2563eb",
        "bg_dark": "#0f172a",
        "bg_light": "#f8fafc",
        "bg_white": "#ffffff",
        "text_dark": "#0f172a",
        "text_light": "#64748b",
        "text_muted": "#94a3b8",
        "border_light": "#e2e8f0",
        "border_dark": "#cbd5e1",
    }
    
    # Dark Theme
    DARK = {
        "name": "Dark Mode",
        "primary": "#60a5fa",
        "primary_dark": "#3b82f6",
        "primary_light": "#1e3a8a",
        "secondary": "#34d399",
        "secondary_dark": "#10b981",
        "secondary_light": "#047857",
        "success": "#34d399",
        "warning": "#fbbf24",
        "danger": "#f87171",
        "info": "#60a5fa",
        "bg_dark": "#0f172a",
        "bg_light": "#1e293b",
        "bg_white": "#334155",
        "text_dark": "#f8fafc",
        "text_light": "#cbd5e1",
        "text_muted": "#94a3b8",
        "border_light": "#334155",
        "border_dark": "#475569",
    }
    
    # Light Theme
    LIGHT = {
        "name": "Light Mode",
        "primary": "#0ea5e9",
        "primary_dark": "#0284c7",
        "primary_light": "#e0f2fe",
        "secondary": "#06b6d4",
        "secondary_dark": "#0891b2",
        "secondary_light": "#cffafe",
        "success": "#10b981",
        "warning": "#f59e0b",
        "danger": "#ef4444",
        "info": "#0ea5e9",
        "bg_dark": "#f0f9ff",
        "bg_light": "#f8fafc",
        "bg_white": "#ffffff",
        "text_dark": "#0c4a6e",
        "text_light": "#475569",
        "text_muted": "#64748b",
        "border_light": "#e0e7ff",
        "border_dark": "#cbd5e1",
    }
    
    # Vibrant Theme
    VIBRANT = {
        "name": "Vibrant",
        "primary": "#7c3aed",
        "primary_dark": "#6d28d9",
        "primary_light": "#ede9fe",
        "secondary": "#ec4899",
        "secondary_dark": "#db2777",
        "secondary_light": "#fbcfe8",
        "success": "#06b6d4",
        "warning": "#f97316",
        "danger": "#dc2626",
        "info": "#7c3aed",
        "bg_dark": "#faf5ff",
        "bg_light": "#f5f3ff",
        "bg_white": "#ffffff",
        "text_dark": "#581c87",
        "text_light": "#7c3aed",
        "text_muted": "#a78bfa",
        "border_light": "#ede9fe",
        "border_dark": "#ddd6fe",
    }
    
    # Minimal Theme
    MINIMAL = {
        "name": "Minimal",
        "primary": "#424242",
        "primary_dark": "#212121",
        "primary_light": "#f5f5f5",
        "secondary": "#757575",
        "secondary_dark": "#424242",
        "secondary_light": "#e0e0e0",
        "success": "#388e3c",
        "warning": "#f57c00",
        "danger": "#d32f2f",
        "info": "#1976d2",
        "bg_dark": "#fafafa",
        "bg_light": "#f5f5f5",
        "bg_white": "#ffffff",
        "text_dark": "#212121",
        "text_light": "#616161",
        "text_muted": "#9e9e9e",
        "border_light": "#e0e0e0",
        "border_dark": "#bdbdbd",
    }


class UISettings:
    """General UI settings and configuration."""
    
    # Sidebar Configuration
    SIDEBAR = {
        "width": 300,
        "collapsible": True,
        "default_state": "collapsed",
        "show_status_indicator": True,
        "show_mode_switcher": True,
        "show_quick_actions": True,
    }
    
    # Chat Configuration
    CHAT = {
        "max_message_length": 4000,
        "max_history_visible": 100,
        "enable_message_timestamps": True,
        "enable_typing_indicator": True,
        "typing_animation_speed": 1.4,  # seconds
        "message_animation_duration": 0.3,  # seconds
        "auto_scroll_on_new_message": True,
        "enable_message_reactions": False,
        "max_visible_reactions": 6,
    }
    
    # Input Configuration
    INPUT = {
        "placeholder_text": "Type your question or request...",
        "max_height": 100,  # pixels
        "min_height": 40,   # pixels
        "show_char_count": True,
        "enable_markdown": True,
        "enable_code_blocks": True,
        "enable_formatting_toolbar": False,
    }
    
    # Display Configuration
    DISPLAY = {
        "card_border_radius": 12,
        "card_shadow": "0 4px 12px rgba(0,0,0,0.08)",
        "button_border_radius": 10,
        "message_bubble_max_width": 70,  # percentage
        "font_family": "'Inter', sans-serif",
        "font_size_base": 16,  # pixels
        "line_height": 1.6,
        "letter_spacing": -0.02,  # em
    }
    
    # Animation Configuration
    ANIMATIONS = {
        "enable_animations": True,
        "enable_transitions": True,
        "slide_in_duration": 0.3,  # seconds
        "fade_in_duration": 0.2,   # seconds
        "hover_transform": "translateY(-2px)",
        "button_animation_easing": "ease",
    }
    
    # Responsive Configuration
    RESPONSIVE = {
        "breakpoint_mobile": 480,
        "breakpoint_tablet": 768,
        "breakpoint_desktop": 1200,
        "mobile_max_width": 85,  # percentage
        "tablet_max_width": 80,  # percentage
        "mobile_message_width": 90,  # percentage
    }
    
    # Accessibility Configuration
    ACCESSIBILITY = {
        "enable_wcag_aa_compliance": True,
        "enable_focus_indicators": True,
        "enable_keyboard_navigation": True,
        "enable_high_contrast_mode": False,
        "enable_reduced_motion": False,
        "min_touch_target_size": 48,  # pixels
        "focus_outline_width": 3,  # pixels
    }


class MessageStyles:
    """Styles for different message types."""
    
    USER_MESSAGE = {
        "bg_color": "#2563eb",
        "text_color": "#ffffff",
        "border_radius": "12px",
        "border_bottom_right_radius": "4px",
        "avatar": "👤",
        "alignment": "right",
        "padding": "1rem 1.25rem",
        "max_width": "70%",
    }
    
    ASSISTANT_MESSAGE = {
        "bg_color": "#ffffff",
        "text_color": "#0f172a",
        "border": "1px solid #e2e8f0",
        "border_radius": "12px",
        "border_bottom_left_radius": "4px",
        "avatar": "🤖",
        "alignment": "left",
        "padding": "1rem 1.25rem",
        "max_width": "70%",
    }
    
    SYSTEM_MESSAGE = {
        "bg_color": "#f0f9ff",
        "text_color": "#0c4a6e",
        "border_left": "4px solid #0ea5e9",
        "border_radius": "8px",
        "avatar": "ℹ️",
        "alignment": "center",
        "padding": "1rem 1.25rem",
        "max_width": "80%",
    }
    
    ERROR_MESSAGE = {
        "bg_color": "#fef2f2",
        "text_color": "#7f1d1d",
        "border_left": "4px solid #ef4444",
        "border_radius": "8px",
        "avatar": "❌",
        "alignment": "center",
        "padding": "1rem 1.25rem",
        "max_width": "80%",
    }
    
    SUCCESS_MESSAGE = {
        "bg_color": "#f0fdf4",
        "text_color": "#15803d",
        "border_left": "4px solid #10b981",
        "border_radius": "8px",
        "avatar": "✅",
        "alignment": "center",
        "padding": "1rem 1.25rem",
        "max_width": "80%",
    }


class ButtonStyles:
    """Styles for different button types."""
    
    PRIMARY = {
        "bg_color": "#2563eb",
        "text_color": "#ffffff",
        "border": "none",
        "border_radius": 10,
        "padding": "0.75rem 1.5rem",
        "font_weight": 600,
        "shadow": "0 4px 12px rgba(37, 99, 235, 0.3)",
        "hover_transform": "translateY(-2px)",
        "hover_shadow": "0 6px 20px rgba(37, 99, 235, 0.4)",
    }
    
    SECONDARY = {
        "bg_color": "#f1f5f9",
        "text_color": "#0f172a",
        "border": "1px solid #e2e8f0",
        "border_radius": 10,
        "padding": "0.75rem 1.5rem",
        "font_weight": 600,
        "shadow": "none",
        "hover_bg": "#e2e8f0",
        "hover_transform": "translateY(-2px)",
    }
    
    SUCCESS = {
        "bg_color": "#10b981",
        "text_color": "#ffffff",
        "border": "none",
        "border_radius": 10,
        "padding": "0.75rem 1.5rem",
        "font_weight": 600,
        "shadow": "0 4px 12px rgba(16, 185, 129, 0.3)",
        "hover_bg": "#059669",
    }
    
    DANGER = {
        "bg_color": "#ef4444",
        "text_color": "#ffffff",
        "border": "none",
        "border_radius": 10,
        "padding": "0.75rem 1.5rem",
        "font_weight": 600,
        "shadow": "0 4px 12px rgba(239, 68, 68, 0.3)",
        "hover_bg": "#dc2626",
    }


class FontConfig:
    """Font configuration."""
    
    FONTS = {
        "primary": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
        "mono": "'Fira Code', 'Courier New', monospace",
        "display": "'Inter', sans-serif",
    }
    
    SIZES = {
        "xs": "0.75rem",      # 12px
        "sm": "0.875rem",     # 14px
        "base": "1rem",       # 16px
        "lg": "1.125rem",     # 18px
        "xl": "1.25rem",      # 20px
        "2xl": "1.5rem",      # 24px
        "3xl": "1.875rem",    # 30px
        "4xl": "2.25rem",     # 36px
        "5xl": "3rem",        # 48px
    }
    
    WEIGHTS = {
        "thin": 100,
        "extralight": 200,
        "light": 300,
        "normal": 400,
        "medium": 500,
        "semibold": 600,
        "bold": 700,
        "extrabold": 800,
        "black": 900,
    }


class SpacingConfig:
    """Spacing/padding configuration following 8px grid."""
    
    SCALE = {
        "0": "0",
        "1": "0.5rem",      # 8px
        "2": "1rem",        # 16px
        "3": "1.5rem",      # 24px
        "4": "2rem",        # 32px
        "5": "2.5rem",      # 40px
        "6": "3rem",        # 48px
        "8": "4rem",        # 64px
        "12": "6rem",       # 96px
        "16": "8rem",       # 128px
    }


class ShadowConfig:
    """Shadow configuration."""
    
    SHADOWS = {
        "none": "none",
        "xs": "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
        "sm": "0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)",
        "md": "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
        "lg": "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
        "xl": "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
        "2xl": "0 25px 50px -12px rgba(0, 0, 0, 0.25)",
        "inner": "inset 0 2px 4px 0 rgba(0, 0, 0, 0.05)",
    }


class BrandConfig:
    """Brand/product configuration."""
    
    PRODUCT_NAME = "ClaimPilot AI"
    PRODUCT_TAGLINE = "Insurance Claims Investigation Assistant"
    PRODUCT_VERSION = "1.0.0"
    
    LOGO_URL = "/path/to/logo.svg"  # Update this path
    FAVICON_URL = "/path/to/favicon.ico"
    
    CONTACT_EMAIL = "support@claimpilot.ai"
    SUPPORT_URL = "https://support.claimpilot.ai"
    DOCS_URL = "https://docs.claimpilot.ai"
    
    SOCIAL_LINKS = {
        "github": "https://github.com/claimpilot",
        "twitter": "https://twitter.com/claimpilot",
        "linkedin": "https://linkedin.com/company/claimpilot",
    }


# API Configuration
class APIConfig:
    """API configuration."""
    
    DEFAULT_BASE_URL = "http://localhost:8001"
    TIMEOUT = 180  # seconds
    RETRIES = 3
    RETRY_DELAY = 1  # seconds
    
    ENDPOINTS = {
        "health": "/health",
        "investigate": "/api/v1/investigate",
        "ask": "/api/v1/ask",
    }
    
    ERROR_MESSAGES = {
        "connection_error": "Unable to connect to the API server.",
        "timeout_error": "Request timed out. Please try again.",
        "invalid_response": "Invalid response from server.",
        "authentication_error": "Authentication failed.",
        "server_error": "Server encountered an error. Please try again.",
    }


# Export all configurations
__all__ = [
    "ColorScheme",
    "ThemeConfig",
    "UISettings",
    "MessageStyles",
    "ButtonStyles",
    "FontConfig",
    "SpacingConfig",
    "ShadowConfig",
    "BrandConfig",
    "APIConfig",
]
