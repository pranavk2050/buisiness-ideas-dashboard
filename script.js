(() => {
    const grid = document.getElementById("issues-grid");
    const searchInput = document.getElementById("search");
    const datePicker = document.getElementById("date-picker");
    const prevBtn = document.getElementById("prev-date");
    const nextBtn = document.getElementById("next-date");
    const lastUpdatedEl = document.getElementById("last-updated");
    const tabs = document.querySelectorAll(".tab");

    let allIssues = [];
    let activeCategory = "all";

    // Load data
    async function loadData() {
        try {
            const res = await fetch("data/issues.json");
            if (!res.ok) throw new Error("Failed to load data");
            const data = await res.json();
            allIssues = data.issues || [];
            lastUpdatedEl.textContent = `Last updated: ${data.last_updated || "—"}`;
            if (data.last_updated) {
                datePicker.value = data.last_updated;
            }
            render();
        } catch (err) {
            grid.innerHTML = `<p class="loading">Could not load issues. Make sure data/issues.json exists.</p>`;
            console.error(err);
        }
    }

    function getFilteredIssues() {
        const query = searchInput.value.toLowerCase().trim();
        const selectedDate = datePicker.value;

        return allIssues.filter(issue => {
            if (activeCategory !== "all" && issue.category !== activeCategory) return false;
            if (selectedDate && issue.date !== selectedDate) return false;
            if (query) {
                const text = `${issue.title} ${issue.summary} ${issue.business_opportunity} ${issue.solution}`.toLowerCase();
                if (!text.includes(query)) return false;
            }
            return true;
        });
    }

    function render() {
        const filtered = getFilteredIssues();
        updateStats(filtered);

        if (filtered.length === 0) {
            grid.innerHTML = `<p class="loading">No issues found for the current filters.</p>`;
            return;
        }

        grid.innerHTML = filtered.map(issue => `
            <article class="issue-card">
                <div class="card-header">
                    <span class="category-badge ${issue.category}">${issue.category}</span>
                    <span class="market-badge ${issue.market_potential}">${issue.market_potential} potential</span>
                </div>
                <div class="card-body">
                    <h3>${escapeHtml(issue.title)}</h3>
                    <p class="summary">${escapeHtml(issue.summary)}</p>
                    <div class="opportunity">
                        <strong>Business Opportunity</strong>
                        ${escapeHtml(issue.business_opportunity)}
                    </div>
                    <div class="solution">
                        <strong>Suggested Solution</strong>
                        ${escapeHtml(issue.solution)}
                    </div>
                </div>
                <div class="card-footer">
                    <span>${issue.source || "Google News"}</span>
                    <span>${issue.date}</span>
                </div>
            </article>
        `).join("");
    }

    function updateStats(filtered) {
        document.getElementById("total-count").textContent = filtered.length;
        document.getElementById("high-count").textContent = filtered.filter(i => i.market_potential === "high").length;
        document.getElementById("medium-count").textContent = filtered.filter(i => i.market_potential === "medium").length;
        document.getElementById("low-count").textContent = filtered.filter(i => i.market_potential === "low").length;
    }

    function escapeHtml(str) {
        if (!str) return "";
        const div = document.createElement("div");
        div.textContent = str;
        return div.innerHTML;
    }

    function shiftDate(days) {
        const current = datePicker.value ? new Date(datePicker.value) : new Date();
        current.setDate(current.getDate() + days);
        datePicker.value = current.toISOString().split("T")[0];
        render();
    }

    // Event listeners
    tabs.forEach(tab => {
        tab.addEventListener("click", () => {
            tabs.forEach(t => t.classList.remove("active"));
            tab.classList.add("active");
            activeCategory = tab.dataset.category;
            render();
        });
    });

    searchInput.addEventListener("input", render);
    datePicker.addEventListener("change", render);
    prevBtn.addEventListener("click", () => shiftDate(-1));
    nextBtn.addEventListener("click", () => shiftDate(1));

    loadData();
})();
