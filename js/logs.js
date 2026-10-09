/* Access & Notification Logs JS Controller */

async function loadAccessLogs() {
    try {
        const filter = document.getElementById("log-event-filter").value;
        let query = "/api/access/logs?limit=100";
        if (filter) query += `&event_type=${filter}`;

        const logs = await apiFetch(query);
        const tbody = document.getElementById("logs-tbody");

        if (logs.length === 0) {
            tbody.innerHTML = `<tr><td colspan="8" class="text-center text-muted py-4">No gate access logs recorded yet.</td></tr>`;
            return;
        }

        let html = "";
        logs.forEach(log => {
            const timeStr = new Date(log.event_time).toLocaleString([], { dateStyle: 'short', timeStyle: 'medium' });
            const badgeClass = log.event_type === "ENTRY" ? "badge bg-success" : "badge bg-danger";
            const res = log.resident;

            html += `
                <tr>
                    <td class="small fw-bold">${timeStr}</td>
                    <td class="fw-bold">${res ? res.name : 'Unknown Hosteler'}</td>
                    <td><code>${res ? res.student_id : log.hosteler_id}</code></td>
                    <td>${res ? res.room_no : '-'}</td>
                    <td><span class="${badgeClass}">${log.event_type}</span></td>
                    <td>${log.gate}</td>
                    <td><span class="badge bg-light text-dark border">${log.confidence.toFixed(0)}%</span></td>
                    <td><span class="small text-muted">${log.source}</span></td>
                </tr>
            `;
        });
        tbody.innerHTML = html;
    } catch (err) {
        showToast("Error loading access logs: " + err.message, "error");
    }
}

async function loadNotificationLogs() {
    try {
        const records = await apiFetch("/api/notifications/logs");
        const tbody = document.getElementById("notif-tbody");

        if (records.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" class="text-center text-muted py-4">No notification delivery records found.</td></tr>`;
            return;
        }

        let html = "";
        records.forEach(rec => {
            const timeStr = new Date(rec.sent_at).toLocaleString([], { dateStyle: 'short', timeStyle: 'medium' });
            const channelBadge = rec.channel === "WHATSAPP" ? "badge bg-success" : "badge bg-primary";
            const statusBadge = rec.status === "SENT" ? "badge bg-success" : "badge bg-danger";

            html += `
                <tr>
                    <td class="small">${timeStr}</td>
                    <td><span class="badge bg-light text-dark border">${rec.event_type}</span></td>
                    <td><span class="${channelBadge}">${rec.channel}</span></td>
                    <td>${rec.recipient}</td>
                    <td class="small text-truncate" style="max-width: 280px;" title="${rec.message}">${rec.message}</td>
                    <td><span class="${statusBadge}">${rec.status}</span></td>
                </tr>
            `;
        });
        tbody.innerHTML = html;
    } catch (err) {
        showToast("Error loading notification logs: " + err.message, "error");
    }
}

document.addEventListener("DOMContentLoaded", loadAccessLogs);
