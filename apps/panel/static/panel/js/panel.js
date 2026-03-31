(function () {
  var SIDEBAR_STATE_KEY = "green-power-panel-sidebar-collapsed";
  var SIDEBAR_GROUP_STATE_KEY = "green-power-panel-sidebar-groups";

  function debounce(fn, delay) {
    var timeoutId;
    return function () {
      var context = this;
      var args = arguments;
      clearTimeout(timeoutId);
      timeoutId = setTimeout(function () {
        fn.apply(context, args);
      }, delay);
    };
  }

  function readStoredGroupState() {
    try {
      return JSON.parse(window.localStorage.getItem(SIDEBAR_GROUP_STATE_KEY) || "{}");
    } catch (error) {
      return {};
    }
  }

  function writeStoredGroupState(groupState) {
    window.localStorage.setItem(SIDEBAR_GROUP_STATE_KEY, JSON.stringify(groupState));
  }

  function setGroupOpenState(group, isOpen) {
    var toggle = group.querySelector("[data-panel-nav-group-toggle]");
    group.classList.toggle("is-open", isOpen);
    if (toggle) {
      toggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
    }
  }

  function wireSidebar() {
    var body = document.body;
    var toggle = document.querySelector("[data-panel-sidebar-toggle]");
    var groups = document.querySelectorAll("[data-panel-nav-group]");
    var storedGroupState = readStoredGroupState();
    var isCollapsed = window.localStorage.getItem(SIDEBAR_STATE_KEY) === "true";

    body.classList.toggle("panel-sidebar-collapsed", isCollapsed);
    if (toggle) {
      toggle.setAttribute("aria-expanded", isCollapsed ? "false" : "true");
      toggle.addEventListener("click", function () {
        isCollapsed = !body.classList.contains("panel-sidebar-collapsed");
        body.classList.toggle("panel-sidebar-collapsed", isCollapsed);
        window.localStorage.setItem(SIDEBAR_STATE_KEY, isCollapsed ? "true" : "false");
        toggle.setAttribute("aria-expanded", isCollapsed ? "false" : "true");
      });
    }

    groups.forEach(function (group) {
      var groupKey = group.dataset.groupKey;
      var button = group.querySelector("[data-panel-nav-group-toggle]");
      var hasActiveChild = Boolean(group.querySelector(".panel-nav-sublink.is-active"));
      var shouldOpen = Object.prototype.hasOwnProperty.call(storedGroupState, groupKey)
        ? Boolean(storedGroupState[groupKey])
        : hasActiveChild;

      setGroupOpenState(group, shouldOpen && !isCollapsed);

      if (!button) {
        return;
      }

      button.addEventListener("click", function () {
        if (body.classList.contains("panel-sidebar-collapsed")) {
          return;
        }
        var nextState = !group.classList.contains("is-open");
        setGroupOpenState(group, nextState);
        storedGroupState[groupKey] = nextState;
        writeStoredGroupState(storedGroupState);
      });
    });
  }

  function buildFormUrl(form) {
    var url = new URL(form.action || window.location.href, window.location.origin);
    url.search = "";

    var formData = new FormData(form);
    formData.forEach(function (value, key) {
      if (value !== "") {
        url.searchParams.append(key, value);
      }
    });

    return url;
  }

  function wireLiveFilterForm(form) {
    var targetSelector = form.dataset.liveFilterTarget;
    var target = targetSelector ? document.querySelector(targetSelector) : null;
    if (!target) {
      return;
    }

    var controller = null;
    var responseCache = new Map();
    var lastSubmittedUrl = window.location.href;
    var partialName = form.dataset.liveFilterPartial || target.id || "results";

    function renderResponse(urlString, html) {
      target.innerHTML = html;
      window.history.replaceState({}, "", urlString);
      lastSubmittedUrl = urlString;
    }

    function submitLiveForm() {
      var url = buildFormUrl(form);
      var urlString = url.toString();

      if (urlString === lastSubmittedUrl) {
        return;
      }

      if (responseCache.has(urlString)) {
        renderResponse(urlString, responseCache.get(urlString));
        return;
      }

      if (controller) {
        controller.abort();
      }

      controller = new AbortController();
      target.classList.add("panel-live-loading");

      fetch(url.toString(), {
        headers: {
          "X-Requested-With": "XMLHttpRequest",
          "X-Panel-Partial": partialName
        },
        signal: controller.signal
      })
        .then(function (response) {
          if (!response.ok) {
            throw new Error("Live filter request failed.");
          }
          return response.text();
        })
        .then(function (html) {
          responseCache.set(urlString, html);
          renderResponse(urlString, html);
        })
        .catch(function (error) {
          if (error.name !== "AbortError") {
            window.location.href = urlString;
          }
        })
        .finally(function () {
          target.classList.remove("panel-live-loading");
        });
    }

    var immediateFields = form.querySelectorAll("[data-auto-submit-immediate]");
    immediateFields.forEach(function (field) {
      field.addEventListener("change", submitLiveForm);
    });

    var debouncedFields = form.querySelectorAll("[data-auto-submit-debounce]");
    debouncedFields.forEach(function (field) {
      var delay = Number(field.dataset.autoSubmitDebounce || "250");
      field.addEventListener("input", debounce(submitLiveForm, delay));
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    wireSidebar();

    var liveFilterForms = document.querySelectorAll("[data-live-filter-form]");
    liveFilterForms.forEach(function (form) {
      wireLiveFilterForm(form);
    });
  });
})();
