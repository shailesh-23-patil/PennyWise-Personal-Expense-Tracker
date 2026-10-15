
"use strict";

document.addEventListener("DOMContentLoaded", () => {

    /* =========================================
       1. THEME MANAGEMENT
       ========================================= */

    const root = document.documentElement;
    const themeToggle = document.getElementById("themeToggle");
    const themeIcon = document.getElementById("themeIcon");

    function getCurrentTheme() {
        return root.dataset.theme === "dark" ? "dark" : "light";
    }

    function applyTheme(theme) {
        const selectedTheme = theme === "dark" ? "dark" : "light";

        root.dataset.theme = selectedTheme;

        if (themeIcon) {
            themeIcon.textContent =
                selectedTheme === "dark" ? "☀" : "☾";
        }

        if (themeToggle) {
            const nextTheme =
                selectedTheme === "dark" ? "light" : "dark";

            themeToggle.setAttribute(
                "aria-label",
                `Switch to ${nextTheme} mode`
            );

            themeToggle.setAttribute(
                "title",
                `Switch to ${nextTheme} mode`
            );
        }

        const themeColor = document.querySelector(
            'meta[name="theme-color"]'
        );

        if (themeColor) {
            themeColor.content =
                selectedTheme === "dark" ? "#151722" : "#f7f8fc";
        }
    }

    // The base.html script loads the saved theme first.
    applyTheme(getCurrentTheme());

    if (themeToggle) {
        themeToggle.addEventListener("click", () => {
            const nextTheme =
                getCurrentTheme() === "dark" ? "light" : "dark";

            applyTheme(nextTheme);

            try {
                localStorage.setItem("pennywise-theme", nextTheme);
            } catch (error) {
                console.warn("Theme preference could not be saved.");
            }
        });
    }


    /* =========================================
       2. TRANSACTION CATEGORY SWITCHING
       ========================================= */

    const transactionForm =
        document.getElementById("transactionForm");

    const categorySelect =
        document.getElementById("categorySelect");

    if (transactionForm && categorySelect) {

        const typeRadios = transactionForm.querySelectorAll(
            'input[name="transaction_type"]'
        );

        const updateCategories = () => {
            const selectedRadio = transactionForm.querySelector(
                'input[name="transaction_type"]:checked'
            );

            if (!selectedRadio) return;

            const selectedType = selectedRadio.value;
            let firstAvailable = "";

            Array.from(categorySelect.options).forEach((option) => {

                if (!option.value) {
                    option.hidden = false;
                    option.disabled = false;
                    return;
                }

                const matches = option.dataset.type === selectedType;

                option.hidden = !matches;
                option.disabled = !matches;

                if (matches && !firstAvailable) {
                    firstAvailable = option.value;
                }
            });

            const currentOption =
                categorySelect.options[categorySelect.selectedIndex];

            if (
                !currentOption ||
                currentOption.dataset.type !== selectedType
            ) {
                categorySelect.value = firstAvailable;
            }
        };

        typeRadios.forEach((radio) => {
            radio.addEventListener("change", updateCategories);
        });

        updateCategories();
    }


    /* =========================================
       3. TRANSACTION DATE VALIDATION
       ========================================= */

    const filters = document.querySelector(".filters-grid");

    if (filters) {

        const startInput =
            filters.querySelector('[name="start_date"]');

        const endInput =
            filters.querySelector('[name="end_date"]');

        const validateDateRange = () => {
            if (!startInput || !endInput) return true;

            const start = startInput.value;
            const end = endInput.value;

            const invalidRange =
                start !== "" && end !== "" && start > end;

            endInput.setCustomValidity(
                invalidRange
                    ? "End date must be on or after the start date."
                    : ""
            );

            return !invalidRange;
        };

        if (startInput && endInput) {
            startInput.addEventListener("change", validateDateRange);
            endInput.addEventListener("change", validateDateRange);
        }

        filters.addEventListener("submit", (event) => {
            if (!validateDateRange()) {
                event.preventDefault();
                alert(
                    "The start date must be on or before the end date."
                );
                endInput.reportValidity();
            }
        });
    }


    /* =========================================
       4. DISMISSIBLE FLASH NOTIFICATIONS
       ========================================= */

    document.querySelectorAll(".flash-close").forEach((button) => {
        button.addEventListener("click", () => {
            const message = button.closest(".flash");

            if (message) {
                message.remove();
            }
        });
    });


    /* =========================================
       5. FORM SUBMISSION FEEDBACK
       ========================================= */

    document.querySelectorAll("form").forEach((form) => {

        // Leave logout, delete and filter forms unchanged.
        // Only provide feedback for forms that create records.
        const isTransactionForm =
            form.id === "transactionForm";

        const isBudgetForm =
            form.action.includes("/budget");

        if (!isTransactionForm && !isBudgetForm) return;

        form.addEventListener("submit", () => {
            if (!form.checkValidity()) return;

            const submitButton = form.querySelector(
                'button[type="submit"]'
            );

            if (submitButton) {
                submitButton.dataset.originalText =
                    submitButton.textContent;

                submitButton.disabled = true;
                submitButton.textContent = "Saving...";
            }
        });
    });


    /* =========================================
       6. MOBILE-FRIENDLY TABLES
       ========================================= */

    document.querySelectorAll(".table-scroll").forEach((container) => {
        container.setAttribute("tabindex", "0");
        container.setAttribute("role", "region");
        container.setAttribute(
            "aria-label",
            "Scrollable transaction table"
        );
    });

});
