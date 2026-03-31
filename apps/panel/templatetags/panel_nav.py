from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def panel_active(active_key, expected_key):
    return "is-active" if active_key == expected_key else ""


SIDEBAR_ICONS = {
    "dashboard": """
        <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
          <rect x="3.5" y="3.5" width="7" height="7" rx="1.5"></rect>
          <rect x="13.5" y="3.5" width="7" height="4.5" rx="1.5"></rect>
          <rect x="13.5" y="11.5" width="7" height="9" rx="1.5"></rect>
          <rect x="3.5" y="13.5" width="7" height="7" rx="1.5"></rect>
        </svg>
    """,
    "client": """
        <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
          <path d="M4.5 6.5h9a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-9a2 2 0 0 1-2-2v-9a2 2 0 0 1 2-2Z"></path>
          <path d="M8 10.25h8.5"></path>
          <path d="M8 14h8.5"></path>
          <path d="M8 17.75h5.5"></path>
          <path d="M15.5 7V5.75A1.75 1.75 0 0 1 17.25 4h1A1.75 1.75 0 0 1 20 5.75v12.5A1.75 1.75 0 0 1 18.25 20h-1"></path>
        </svg>
    """,
    "device": """
        <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
          <rect x="5" y="4" width="14" height="16" rx="3"></rect>
          <path d="M9 8h6"></path>
          <path d="M9 12h6"></path>
          <circle cx="12" cy="16.5" r="1"></circle>
        </svg>
    """,
    "thresholds": """
        <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
          <path d="M5 18.5h14"></path>
          <path d="M8 18.5V8.5"></path>
          <path d="M12 18.5V5.5"></path>
          <path d="M16 18.5v-7"></path>
          <circle cx="8" cy="8.5" r="1.5"></circle>
          <circle cx="12" cy="5.5" r="1.5"></circle>
          <circle cx="16" cy="11.5" r="1.5"></circle>
        </svg>
    """,
    "access-control": """
        <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
          <circle cx="8" cy="8" r="3"></circle>
          <circle cx="16.5" cy="9.5" r="2.5"></circle>
          <path d="M3.5 19a4.5 4.5 0 0 1 9 0"></path>
          <path d="M13.5 19a3.5 3.5 0 0 1 7 0"></path>
        </svg>
    """,
    "audit-logs": """
        <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
          <path d="M7 4.5h8l3 3v12a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2v-13a2 2 0 0 1 2-2Z"></path>
          <path d="M15 4.5v3h3"></path>
          <path d="M8.5 12h7"></path>
          <path d="M8.5 15.5h7"></path>
        </svg>
    """,
}


@register.simple_tag
def panel_icon(icon_name):
    return mark_safe(SIDEBAR_ICONS.get(icon_name, ""))
