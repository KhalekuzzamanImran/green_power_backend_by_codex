(function () {
  function buildOption(value, label, selected) {
    var option = document.createElement("option");
    option.value = value;
    option.textContent = label;
    if (selected) {
      option.selected = true;
    }
    return option;
  }

  function updateDashboardScopes() {
    var clientTypeSelect = document.getElementById("id_client_type");
    var scopeSelect = document.getElementById("id_dashboard_scope");

    if (!clientTypeSelect || !scopeSelect) {
      return;
    }

    var endpoint = scopeSelect.dataset.scopeOptionsUrl;
    if (!endpoint) {
      return;
    }

    var selectedScope = scopeSelect.value;
    var clientTypeId = clientTypeSelect.value;

    scopeSelect.innerHTML = "";
    scopeSelect.appendChild(buildOption("", "---------", !selectedScope));

    if (!clientTypeId) {
      return;
    }

    var url = new URL(endpoint, window.location.origin);
    url.searchParams.set("client_type_id", clientTypeId);

    fetch(url, {
      headers: {
        "X-Requested-With": "XMLHttpRequest"
      }
    })
      .then(function (response) {
        if (!response.ok) {
          throw new Error("Failed to load dashboard scopes.");
        }
        return response.json();
      })
      .then(function (payload) {
        payload.results.forEach(function (item) {
          scopeSelect.appendChild(buildOption(item.id, item.name, item.id === selectedScope));
        });
      })
      .catch(function () {
        scopeSelect.innerHTML = "";
        scopeSelect.appendChild(buildOption("", "---------", true));
      });
  }

  document.addEventListener("DOMContentLoaded", function () {
    var clientTypeSelect = document.getElementById("id_client_type");
    if (!clientTypeSelect) {
      return;
    }

    clientTypeSelect.addEventListener("change", updateDashboardScopes);
    updateDashboardScopes();
  });
})();
