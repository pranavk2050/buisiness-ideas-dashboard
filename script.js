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
    let chartInstances = {};

    // Category colors matching CSS vars
    const categoryColors = {
        health: "#e74c3c",
        nutrition: "#27ae60",
        education: "#2980b9",
        technology: "#8e44ad",
        agriculture: "#d35400",
        environment: "#16a085",
        infrastructure: "#2c3e50",
        finance: "#f39c12"
    };

    // Resources data
    const resourcesData = {
        govt: [
            { name: "Startup India", category: "general", description: "Government initiative for startup ecosystem support — tax benefits, funding, and incubation.", url: "https://www.startupindia.gov.in/" },
            { name: "Ayushman Bharat", category: "health", description: "National health protection scheme covering 50 crore beneficiaries for secondary and tertiary care.", url: "https://pmjay.gov.in/" },
            { name: "PM-KISAN", category: "agriculture", description: "Income support of Rs.6000/year to farmer families through direct benefit transfer.", url: "https://pmkisan.gov.in/" },
            { name: "PMFBY", category: "agriculture", description: "Pradhan Mantri Fasal Bima Yojana — crop insurance scheme for farmers against crop failure.", url: "https://pmfby.gov.in/" },
            { name: "Digital India", category: "technology", description: "Umbrella programme to transform India into a digitally empowered society and knowledge economy.", url: "https://www.digitalindia.gov.in/" },
            { name: "Atal Innovation Mission", category: "technology", description: "Promotes innovation and entrepreneurship through Atal Tinkering Labs and Atal Incubation Centers.", url: "https://aim.gov.in/" },
            { name: "MUDRA Yojana", category: "finance", description: "Micro Units Development & Refinance Agency — loans up to Rs.10 lakh for non-corporate, non-farm small enterprises.", url: "https://www.mudra.org.in/" },
            { name: "Smart Cities Mission", category: "infrastructure", description: "Urban renewal programme to develop 100 smart cities with core infrastructure and technology.", url: "https://smartcities.gov.in/" },
            { name: "NABARD Programs", category: "agriculture", description: "National Bank for Agriculture and Rural Development — rural infrastructure and agriculture credit.", url: "https://www.nabard.org/" },
            { name: "FSSAI Initiatives", category: "nutrition", description: "Food Safety and Standards Authority of India — Eat Right India movement and food safety grants.", url: "https://www.fssai.gov.in/" },
            { name: "NEP 2020", category: "education", description: "National Education Policy 2020 — transformative reforms in school and higher education systems.", url: "https://www.education.gov.in/nep" },
            { name: "NSDC Skill Programs", category: "education", description: "National Skill Development Corporation — training and certification in 37+ sectors.", url: "https://nsdcindia.org/" },
            { name: "Swachh Bharat Mission", category: "environment", description: "Clean India initiative focused on sanitation, waste management, and environmental cleanliness.", url: "https://swachhbharatmission.gov.in/" },
            { name: "SIDBI Fund of Funds", category: "finance", description: "Rs.10,000 crore fund to support startups through AIFs and venture capital funds.", url: "https://www.sidbi.in/" },
            { name: "National Health Mission", category: "health", description: "Strengthening healthcare delivery across rural and urban India — infrastructure and human resources.", url: "https://nhm.gov.in/" },
            { name: "Poshan Abhiyaan", category: "nutrition", description: "National Nutrition Mission to reduce malnutrition with a multi-ministerial convergence approach.", url: "https://poshanabhiyaan.gov.in/" }
        ],
        funding: [
            { name: "Sequoia Surge", category: "general", description: "Early-stage startup programme by Sequoia Capital — $1-2M seed funding with mentorship.", url: "https://www.surgeahead.com/" },
            { name: "Indian Angel Network", category: "general", description: "India's leading angel investor network with 500+ members funding seed to pre-Series A startups.", url: "https://www.indianangelnetwork.com/" },
            { name: "100X.VC", category: "general", description: "India-focused micro VC fund investing via iSAFE notes in early-stage startups.", url: "https://www.100x.vc/" },
            { name: "Bharat Innovation Fund", category: "technology", description: "Deep-tech focused fund investing in IP-led startups from India's research ecosystem.", url: "https://bharatinnovationfund.com/" },
            { name: "Atal Incubation Centers", category: "technology", description: "Government-backed incubators providing world-class support for startups across India.", url: "https://aim.gov.in/atal-incubation-centres.php" },
            { name: "T-Hub", category: "technology", description: "India's largest technology incubator based in Hyderabad — mentorship, funding, and corporate connections.", url: "https://t-hub.co/" },
            { name: "NASSCOM 10K Startups", category: "technology", description: "Programme to incubate, fund, and support 10,000 technology startups in India.", url: "https://nasscom.in/" },
            { name: "Omnivore Partners", category: "agriculture", description: "VC firm focused on agritech and food innovation startups in India.", url: "https://www.omnivore.vc/" },
            { name: "Aavishkaar Capital", category: "general", description: "Impact investment group backing enterprises in agriculture, health, education, and financial inclusion.", url: "https://www.aavishkaar.in/" },
            { name: "Villgro", category: "health", description: "Social enterprise incubator focused on health, agriculture, and clean energy innovations.", url: "https://villgro.org/" },
            { name: "Central Square Foundation", category: "education", description: "Non-profit focused on improving learning outcomes — supports edtech and education ventures.", url: "https://www.centralsquarefoundation.org/" },
            { name: "Ankur Capital", category: "environment", description: "Early-stage VC investing in sustainable development — climate, agriculture, and healthcare.", url: "https://ankurcapital.com/" },
            { name: "Unitus Ventures", category: "finance", description: "Impact VC investing in fintech, healthtech, and edtech serving India's mass market.", url: "https://unitus.vc/" },
            { name: "Social Alpha", category: "environment", description: "Platform incubating science and technology enterprises solving critical social and environmental challenges.", url: "https://socialalpha.org/" },
            { name: "Caspian Debt", category: "finance", description: "Impact-focused debt financing for social enterprises in financial inclusion, health, and energy.", url: "https://www.caspian.in/" }
        ]
    };

    let activeResourceTab = "govt";

    // Load data — uses XHR to support file:// protocol
    function loadData() {
        const xhr = new XMLHttpRequest();
        xhr.open("GET", "data/issues.json", true);
        xhr.onreadystatechange = function () {
            if (xhr.readyState !== 4) return;
            if (xhr.status === 200 || (xhr.status === 0 && xhr.responseText)) {
                try {
                    const data = JSON.parse(xhr.responseText);
                    allIssues = data.issues || [];
                    lastUpdatedEl.textContent = `Last updated: ${data.last_updated || "—"}`;
                    if (data.last_updated) {
                        datePicker.value = data.last_updated;
                    }
                    render();
                } catch (e) {
                    grid.innerHTML = `<p class="loading">Error parsing issues data.</p>`;
                    console.error(e);
                }
            } else {
                grid.innerHTML = `<p class="loading">Could not load issues. Make sure data/issues.json exists.</p>`;
            }
        };
        xhr.onerror = function () {
            grid.innerHTML = `<p class="loading">Could not load issues. Make sure data/issues.json exists.</p>`;
        };
        xhr.send();
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

    // Chart rendering
    function renderCharts(issues) {
        if (typeof Chart === "undefined") return;

        // Destroy existing charts
        Object.values(chartInstances).forEach(c => c.destroy());
        chartInstances = {};

        if (!issues.length) return;

        // 1. Category distribution (doughnut)
        const catCounts = {};
        issues.forEach(i => { catCounts[i.category] = (catCounts[i.category] || 0) + 1; });
        const catLabels = Object.keys(catCounts);
        const catData = Object.values(catCounts);
        const catColors = catLabels.map(c => categoryColors[c] || "#95a5a6");

        chartInstances.category = new Chart(document.getElementById("category-chart"), {
            type: "doughnut",
            data: { labels: catLabels.map(l => l.charAt(0).toUpperCase() + l.slice(1)), datasets: [{ data: catData, backgroundColor: catColors, borderWidth: 2, borderColor: "#fff" }] },
            options: { responsive: true, plugins: { legend: { position: "bottom", labels: { boxWidth: 12, padding: 8, font: { size: 11 } } } } }
        });

        // 2. Market potential (bar)
        const potCounts = { high: 0, medium: 0, low: 0 };
        issues.forEach(i => { if (potCounts[i.market_potential] !== undefined) potCounts[i.market_potential]++; });

        chartInstances.potential = new Chart(document.getElementById("potential-chart"), {
            type: "bar",
            data: {
                labels: ["High", "Medium", "Low"],
                datasets: [{ label: "Issues", data: [potCounts.high, potCounts.medium, potCounts.low], backgroundColor: ["#e74c3c", "#f39c12", "#95a5a6"], borderRadius: 6 }]
            },
            options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } } }
        });

        // 3. Daily trend (line)
        const dateCounts = {};
        issues.forEach(i => { if (i.date) dateCounts[i.date] = (dateCounts[i.date] || 0) + 1; });
        const sortedDates = Object.keys(dateCounts).sort();

        chartInstances.trend = new Chart(document.getElementById("trend-chart"), {
            type: "line",
            data: {
                labels: sortedDates,
                datasets: [{ label: "Issues per day", data: sortedDates.map(d => dateCounts[d]), borderColor: "#3498db", backgroundColor: "rgba(52,152,219,0.1)", fill: true, tension: 0.3, pointRadius: 4, pointBackgroundColor: "#3498db" }]
            },
            options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } } }
        });

        // 4. Category-wise opportunities (horizontal bar)
        chartInstances.opportunity = new Chart(document.getElementById("opportunity-chart"), {
            type: "bar",
            data: {
                labels: catLabels.map(l => l.charAt(0).toUpperCase() + l.slice(1)),
                datasets: [{ label: "Opportunities", data: catData, backgroundColor: catColors, borderRadius: 6 }]
            },
            options: { indexAxis: "y", responsive: true, plugins: { legend: { display: false } }, scales: { x: { beginAtZero: true, ticks: { stepSize: 1 } } } }
        });
    }

    // Resources rendering
    function renderResources() {
        const container = document.getElementById("resources-content");
        const items = resourcesData[activeResourceTab] || [];

        container.innerHTML = items.map(r => {
            const bgColor = categoryColors[r.category] || "#3498db";
            return `
                <div class="resource-card ${r.category}">
                    <span class="resource-category" style="background:${bgColor}">${r.category}</span>
                    <h4>${r.name}</h4>
                    <p>${r.description}</p>
                    <a href="${r.url}" target="_blank" rel="noopener noreferrer" class="resource-link">Visit Website &#8599;</a>
                </div>
            `;
        }).join("");
    }

    function render() {
        const filtered = getFilteredIssues();
        updateStats(filtered);
        renderCharts(filtered);

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

    // Resource tabs
    document.querySelectorAll(".resource-tab").forEach(tab => {
        tab.addEventListener("click", () => {
            document.querySelectorAll(".resource-tab").forEach(t => t.classList.remove("active"));
            tab.classList.add("active");
            activeResourceTab = tab.dataset.resource;
            renderResources();
        });
    });

    loadData();
    renderResources();
})();
