/* Live Gate Monitor JavaScript Controller */

let currentMode = "ENTRY";

async function setCameraMode(mode) {
    try {
        const res = await apiFetch("/api/camera/mode", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ mode: mode })
        });
        currentMode = mode;
        updateModeUI(mode);
        showToast(`Gate Mode updated to ${mode}`, "success");
    } catch (err) {
        showToast("Failed to change camera mode: " + err.message, "error");
    }
}

function updateModeUI(mode) {
    const btnEntry = document.getElementById("btn-mode-entry");
    const btnExit = document.getElementById("btn-mode-exit");

    if (mode === "ENTRY") {
        btnEntry.className = "btn btn-success fw-bold px-3 btn-mode";
        btnExit.className = "btn btn-outline-danger fw-bold px-3 btn-mode";
    } else {
        btnEntry.className = "btn btn-outline-success fw-bold px-3 btn-mode";
        btnExit.className = "btn btn-danger fw-bold px-3 btn-mode";
    }
}

async function pollCameraStatus() {
    try {
        const status = await apiFetch("/api/camera/status");
        document.getElementById("stream-clock").innerText = status.timestamp || new Date().toLocaleTimeString();

        const statusText = document.getElementById("status-text");
        const residentInfoPanel = document.getElementById("resident-info-panel");

        if (status.recognized_resident) {
            const res = status.recognized_resident;
            statusText.innerText = `Recognized: ${res.name}`;
            statusText.className = "fw-bold text-success";

            document.getElementById("res-name").innerText = res.name;
            document.getElementById("res-id").innerText = res.student_id;
            document.getElementById("res-room").innerText = res.room_no;
            document.getElementById("res-dept").innerText = res.department;
            document.getElementById("res-conf").innerText = `${status.confidence.toFixed(0)}%`;

            residentInfoPanel.classList.remove("d-none");
        } else if (status.status && status.status.includes("UNKNOWN")) {
            statusText.innerText = "UNKNOWN PERSON DETECTED!";
            statusText.className = "fw-bold text-danger animate-pulse";
            residentInfoPanel.classList.add("d-none");
        } else {
            statusText.innerText = "Scanning webcam feed...";
            statusText.className = "fw-bold text-muted";
            residentInfoPanel.classList.add("d-none");
        }
    } catch (err) {
        // Silent polling fail
    }
}

async function loadRecentGateLogs() {
    try {
        const logs = await apiFetch("/api/access/logs?limit=5");
        const container = document.getElementById("recent-logs-list");
        if (logs.length === 0) {
            container.innerHTML = `<div class="text-muted small text-center py-3">No recent events logged.</div>`;
            return;
        }

        let html = "";
        logs.forEach(log => {
            const badgeClass = log.event_type === "ENTRY" ? "badge bg-success" : "badge bg-danger";
            const timeStr = new Date(log.event_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            html += `
                <div class="d-flex justify-content-between align-items-center p-2 border-bottom small">
                    <div>
                        <div class="fw-bold">${log.resident ? log.resident.name : 'Student ID ' + log.hosteler_id}</div>
                        <div class="text-muted text-truncate">${log.resident ? log.resident.room_no : ''} | ${timeStr}</div>
                    </div>
                    <span class="${badgeClass}">${log.event_type}</span>
                </div>
            `;
        });
        container.innerHTML = html;
    } catch (err) {
        console.error("Error loading recent gate logs", err);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    updateModeUI("ENTRY");
    setInterval(pollCameraStatus, 1000);
    setInterval(loadRecentGateLogs, 3000);
    loadRecentGateLogs();
});
