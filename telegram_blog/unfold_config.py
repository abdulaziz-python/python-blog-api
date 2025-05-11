# telegram_blog/unfold_config.py
"""
Unfold admin configuration
"""
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

# Import the dashboard callback
from dashboard import dashboard_callback

# Unfold configuration
UNFOLD = {
    # Appearance settings
    "SITE_TITLE": "Telegram Blog",
    "SITE_HEADER": "Telegram Blog Admin",
    "SITE_LOGO": None,  # Can be replaced with a custom logo path
    "SITE_ICON": None,  # Favicon path
    "SITE_SYMBOL": "description",  # Material icon name
    
    # Theme colors and modes
    "COLORS": {
        "primary": {
            "50": "239, 246, 255",  # Lightest blue
            "100": "219, 234, 254",
            "200": "191, 219, 254",
            "300": "147, 197, 253",
            "400": "96, 165, 250",
            "500": "28, 126, 214",  # Primary blue (custom)
            "600": "37, 99, 235",
            "700": "29, 78, 216",
            "800": "30, 64, 175",
            "900": "30, 58, 138",  # Darkest blue
        }
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": _("Dashboard"),
                "icon": "dashboard",
                "url": reverse("admin:index"),
            },
            {
                "type": "title",
                "title": _("Content"),
            },
            {
                "title": _("Posts"),
                "icon": "description",
                "url": reverse("admin:blog_post_changelist"),
            },
            {
                "title": _("Comments"),
                "icon": "comment",
                "url": reverse("admin:blog_comment_changelist"),
            },
            {
                "title": _("Categories"),
                "icon": "category",
                "url": reverse("admin:blog_category_changelist"),
            },
            {
                "title": _("Tags"),
                "icon": "label",
                "url": reverse("admin:blog_tag_changelist"),
            },
            {
                "type": "title",
                "title": _("Advertising"),
            },
            {
                "title": _("Advertisements"),
                "icon": "campaign",
                "url": reverse("admin:ads_advertisement_changelist"),
            },
            {
                "title": _("Placements"),
                "icon": "grid_view",
                "url": reverse("admin:ads_adplacement_changelist"),
            },
            {
                "title": _("Clicks"),
                "icon": "touch_app",
                "url": reverse("admin:ads_adclick_changelist"),
            },
            {
                "title": _("Impressions"),
                "icon": "visibility",
                "url": reverse("admin:ads_adimpression_changelist"),
            },
            {
                "type": "title",
                "title": _("Statistics"),
            },
            {
                "title": _("Popular Posts"),
                "icon": "trending_up",
                "url": reverse("admin:stats_popularpost_changelist"),
            },
            {
                "title": _("Visitors"),
                "icon": "person",
                "url": reverse("admin:stats_visitor_changelist"),
            },
            {
                "title": _("Page Views"),
                "icon": "pageview",
                "url": reverse("admin:stats_pageview_changelist"),
            },
            {
                "title": _("Daily Stats"),
                "icon": "insert_chart",
                "url": reverse("admin:stats_dailystatistic_changelist"),
            },
        ],
    },
    
    # Enable dark mode toggle
    "DARK_MODE_THEME": True,
    
    # Dashboard callback
    "DASHBOARD_CALLBACK": dashboard_callback,
}