const TAB_BUTTON_SELECTOR = "[data-tab-target]";
const TAB_PANEL_SELECTOR = ".tab_panel";

function activateTab(tabButtons, tabPanels, activeButton) {
    const targetTabId = activeButton.dataset.tabTarget;

    tabButtons.forEach(button => {
        const isActive = button === activeButton;

        button.classList.toggle("active", isActive);
        button.setAttribute("aria-selected", String(isActive));
        button.tabIndex = isActive ? 0 : -1;
    });

    tabPanels.forEach(panel => {
        const isActive = panel.id === targetTabId;

        panel.classList.toggle("active", isActive);
        panel.hidden = !isActive;
    });
}

function moveTabFocus(tabButtons, currentIndex, direction) {
    const nextIndex = (currentIndex + direction + tabButtons.length) % tabButtons.length;
    const nextButton = tabButtons[nextIndex];

    activateTab(tabButtons, document.querySelectorAll(TAB_PANEL_SELECTOR), nextButton);
    nextButton.focus();
}

function handleTabKeydown(event, tabButtons, currentIndex) {
    if (event.key === "ArrowRight") {
        event.preventDefault();
        moveTabFocus(tabButtons, currentIndex, 1);
        return;
    }

    if (event.key === "ArrowLeft") {
        event.preventDefault();
        moveTabFocus(tabButtons, currentIndex, -1);
        return;
    }

    if (event.key === "Home") {
        event.preventDefault();
        activateTab(tabButtons, document.querySelectorAll(TAB_PANEL_SELECTOR), tabButtons[0]);
        tabButtons[0].focus();
        return;
    }

    if (event.key === "End") {
        event.preventDefault();
        const lastButton = tabButtons[tabButtons.length - 1];

        activateTab(tabButtons, document.querySelectorAll(TAB_PANEL_SELECTOR), lastButton);
        lastButton.focus();
    }
}

function initializeLiveTabs() {
    const tabButtons = Array.from(document.querySelectorAll(TAB_BUTTON_SELECTOR));
    const tabPanels = Array.from(document.querySelectorAll(TAB_PANEL_SELECTOR));

    if (tabButtons.length === 0 || tabPanels.length === 0) {
        return;
    }

    tabButtons.forEach((button, index) => {
        button.addEventListener("click", () => {
            activateTab(tabButtons, tabPanels, button);
        });

        button.addEventListener("keydown", event => {
            handleTabKeydown(event, tabButtons, index);
        });
    });

    const initialButton = tabButtons.find(button => {
        return button.getAttribute("aria-selected") === "true";
    }) || tabButtons[0];

    activateTab(tabButtons, tabPanels, initialButton);
}

initializeLiveTabs();
