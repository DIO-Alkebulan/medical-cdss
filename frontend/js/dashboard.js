const API_URL = "http://localhost:8000";

// Check Authentication
function checkAuth() {
  const token = localStorage.getItem("token");
  if (!token) {
    window.location.href = "index.html";
    return false;
  }
  return token;
}

// Get Auth Headers
function getAuthHeaders() {
  return {
    Authorization: `Bearer ${localStorage.getItem("token")}`,
    "Content-Type": "application/json",
  };
}

// Initialize Theme
function initTheme() {
  const theme = localStorage.getItem("theme") || "light";
  document.documentElement.setAttribute("data-theme", theme);

  const themeToggle = document.getElementById("themeToggle");
  if (themeToggle) {
    themeToggle.addEventListener("click", toggleTheme);
  }
}

function toggleTheme() {
  const current = document.documentElement.getAttribute("data-theme");
  const next = current === "light" ? "dark" : "light";
  document.documentElement.setAttribute("data-theme", next);
  localStorage.setItem("theme", next);
}

// Initialize Dashboard
async function initDashboard() {
  const token = checkAuth();
  if (!token) return;

  // Set doctor name
  const doctorName = localStorage.getItem("doctorName");
  const userNameEl = document.querySelector(".user-info h4");
  const userAvatarEl = document.querySelector(".user-avatar");

  if (userNameEl) {
    userNameEl.textContent = doctorName || "Doctor";
  }

  if (userAvatarEl && doctorName) {
    userAvatarEl.textContent = doctorName.charAt(0).toUpperCase();
  }

  // Load statistics
  await loadStatistics();

  // Load recent analyses
  await loadRecentAnalyses();
}

// Load Statistics
async function loadStatistics() {
  try {
    const response = await fetch(`${API_URL}/api/stats`, {
      headers: getAuthHeaders(),
    });

    if (response.ok) {
      const data = await response.json();

      // Update stat cards
      const totalEl = document.getElementById("totalAnalyses");
      const recentEl = document.getElementById("recentCount");
      const accuracyEl = document.getElementById("avgAccuracy");

      if (totalEl) totalEl.textContent = data.total_analyses;
      if (recentEl) recentEl.textContent = data.recent_count;

      // Calculate accuracy (mock for now)
      const accuracy =
        data.total_analyses > 0 ? Math.round(85 + Math.random() * 10) : 0;
      if (accuracyEl) accuracyEl.textContent = `${accuracy}%`;

      // Update disease distribution chart
      updateDiseaseChart(data.disease_distribution);
    }
  } catch (error) {
    console.error("Error loading statistics:", error);
  }
}

// Update Disease Distribution Chart
function updateDiseaseChart(distribution) {
  const chartContainer = document.getElementById("diseaseChart");
  if (!chartContainer) return;

  chartContainer.innerHTML = "";

  const diseases = Object.keys(distribution);
  if (diseases.length === 0) {
    chartContainer.innerHTML =
      '<p style="color: var(--text-secondary); text-align: center;">No data yet</p>';
    return;
  }

  const maxCount = Math.max(...Object.values(distribution));

  diseases.forEach((disease) => {
    const count = distribution[disease];
    const percentage = (count / maxCount) * 100;

    const bar = document.createElement("div");
    bar.style.marginBottom = "1rem";
    bar.innerHTML = `
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
                <span style="font-size: 0.9rem; color: var(--text-primary);">${disease}</span>
                <span style="font-size: 0.9rem; font-weight: 600; color: var(--text-primary);">${count}</span>
            </div>
            <div style="width: 100%; height: 8px; background: var(--bg-tertiary); border-radius: 4px; overflow: hidden;">
                <div style="width: ${percentage}%; height: 100%; background: linear-gradient(90deg, var(--primary), var(--primary-light)); border-radius: 4px;"></div>
            </div>
        `;

    chartContainer.appendChild(bar);
  });
}

// Load Recent Analyses
async function loadRecentAnalyses() {
  try {
    const response = await fetch(`${API_URL}/api/records`, {
      headers: getAuthHeaders(),
    });

    if (response.ok) {
      const data = await response.json();
      displayRecentAnalyses(data.records.slice(0, 5));
    }
  } catch (error) {
    console.error("Error loading recent analyses:", error);
  }
}

// Display Recent Analyses
function displayRecentAnalyses(records) {
  const tbody = document.getElementById("recentAnalyses");
  if (!tbody) return;

  tbody.innerHTML = "";

  if (records.length === 0) {
    tbody.innerHTML = `
            <tr>
                <td colspan="5" style="text-align: center; padding: 2rem; color: var(--text-secondary);">
                    No analyses yet. Start by analyzing your first X-ray!
                </td>
            </tr>
        `;
    return;
  }

  records.forEach((record) => {
    const row = document.createElement("tr");

    const severityClass =
      record.severity === "Severe"
        ? "danger"
        : record.severity === "Moderate"
        ? "warning"
        : record.severity === "Mild"
        ? "success"
        : "info";

    const date = new Date(record.timestamp).toLocaleDateString();

    row.innerHTML = `
            <td>${record.patient_name}</td>
            <td>${record.disease}</td>
            <td><span class="badge badge-${severityClass}">${
      record.severity
    }</span></td>
            <td>${record.confidence.toFixed(1)}%</td>
            <td>${date}</td>
        `;

    row.style.cursor = "pointer";
    row.addEventListener("click", () => {
      window.location.href = `records.html?id=${record.id}`;
    });

    tbody.appendChild(row);
  });
}

// Logout
function handleLogout() {
  localStorage.removeItem("token");
  localStorage.removeItem("doctorName");
  localStorage.removeItem("doctorId");
  window.location.href = "index.html";
}

// Mobile Menu Toggle
function setupMobileMenu() {
  const menuBtn = document.getElementById("mobileMenuBtn");
  const sidebar = document.querySelector(".sidebar");
  const overlay = document.querySelector(".mobile-overlay");

  if (menuBtn) {
    menuBtn.addEventListener("click", () => {
      sidebar.classList.add("mobile-open");
      if (overlay) overlay.classList.add("active");
    });
  }

  if (overlay) {
    overlay.addEventListener("click", () => {
      sidebar.classList.remove("mobile-open");
      overlay.classList.remove("active");
    });
  }
}

// Show Alert
function showAlert(message, type = "info") {
  const alert = document.createElement("div");
  alert.className = `alert alert-${type}`;
  alert.style.cssText = `
        position: fixed;
        top: 2rem;
        right: 2rem;
        z-index: 9999;
        max-width: 400px;
        animation: slideIn 0.3s ease-out;
    `;
  alert.textContent = message;
  document.body.appendChild(alert);

  setTimeout(() => {
    alert.style.animation = "slideOut 0.3s ease-out";
    setTimeout(() => alert.remove(), 300);
  }, 5000);
}

// Initialize
document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  initDashboard();
  setupMobileMenu();

  // Logout button
  const logoutBtn = document.getElementById("logoutBtn");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", (e) => {
      e.preventDefault();
      handleLogout();
    });
  }
});
