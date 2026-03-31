from apps.panel.permissions import get_accessible_clients_for_panel, resolve_panel_client


def build_client_selector_context(user, client_id=None):
    accessible_clients = get_accessible_clients_for_panel(user)
    selected_client = resolve_panel_client(user, client_id=client_id)
    return {
        "accessible_clients": accessible_clients,
        "selected_client": selected_client,
        "requires_client_selection": user.role == "OM" and accessible_clients.count() > 1 and not selected_client,
    }
