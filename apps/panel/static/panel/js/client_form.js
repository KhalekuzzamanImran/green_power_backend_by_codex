(function () {
  function debounce(fn, delay) {
    var timeoutId;
    return function () {
      var args = arguments;
      clearTimeout(timeoutId);
      timeoutId = setTimeout(function () {
        fn.apply(null, args);
      }, delay);
    };
  }

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

    fetch(url, {headers: {"X-Requested-With": "XMLHttpRequest"}})
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

  function wireClientCodeAutomation() {
    var siteNameInput = document.getElementById("id_site_name");
    var codeInput = document.getElementById("id_code");

    if (!siteNameInput || !codeInput) {
      return;
    }

    var suggestionUrl = codeInput.dataset.codeSuggestionUrl;
    var validationUrl = codeInput.dataset.codeValidationUrl;
    var clientId = codeInput.dataset.clientId;
    var autoGenerationEnabled = !Boolean(codeInput.value);

    function setValidationMessage(message) {
      codeInput.setCustomValidity(message || "");
    }

    function validateCodeAvailability() {
      if (!validationUrl || !codeInput.value) {
        setValidationMessage("");
        return;
      }

      var url = new URL(validationUrl, window.location.origin);
      url.searchParams.set("code", codeInput.value);
      if (clientId) {
        url.searchParams.set("client_id", clientId);
      }

      fetch(url, {headers: {"X-Requested-With": "XMLHttpRequest"}})
        .then(function (response) {
          if (!response.ok) {
            throw new Error("Failed to validate code.");
          }
          return response.json();
        })
        .then(function (payload) {
          codeInput.value = payload.normalized_code;
          setValidationMessage(payload.is_available ? "" : payload.message);
        })
        .catch(function () {
          setValidationMessage("");
        });
    }

    var updateCodeSuggestion = debounce(function () {
      if (!autoGenerationEnabled || !suggestionUrl || !siteNameInput.value.trim()) {
        return;
      }

      var url = new URL(suggestionUrl, window.location.origin);
      url.searchParams.set("site_name", siteNameInput.value);
      if (clientId) {
        url.searchParams.set("client_id", clientId);
      }

      fetch(url, {headers: {"X-Requested-With": "XMLHttpRequest"}})
        .then(function (response) {
          if (!response.ok) {
            throw new Error("Failed to generate code.");
          }
          return response.json();
        })
        .then(function (payload) {
          codeInput.value = payload.code;
          setValidationMessage("");
        })
        .catch(function () {
          setValidationMessage("");
        });
    }, 200);

    siteNameInput.addEventListener("input", updateCodeSuggestion);
    codeInput.addEventListener("input", function () {
      autoGenerationEnabled = false;
      if (!codeInput.value) {
        setValidationMessage("");
        return;
      }
      validateCodeAvailability();
    });
    codeInput.addEventListener("blur", validateCodeAvailability);

    updateCodeSuggestion();
    if (codeInput.value) {
      validateCodeAvailability();
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    var clientTypeSelect = document.getElementById("id_client_type");
    if (clientTypeSelect) {
      clientTypeSelect.addEventListener("change", updateDashboardScopes);
      updateDashboardScopes();
    }

    wireClientCodeAutomation();
  });
})();
