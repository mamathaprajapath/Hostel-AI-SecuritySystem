/* Outing Requests JS Controller */

async function loadOutingRequests() {
    try {
        const filter = document.getElementById("outing-status-filter").value;
        let query = "/api/outing/requests";
        if (filter) query += `?status_filter=${filter}`;

        const requests = await apiFetch(query);
        const tbody = document.getElementById("outing-tbody");

        if (requests.length === 0) {
            tbody.innerHTML = `<tr><td colspan="8" class="text-center text-muted py-4">No outing/home leave requests found.</td></tr>`;
            return;
        }

        const residents = await apiFetch("/api/residents");
        const residentMap = {};
        residents.forEach(r => residentMap[r.id] = r);

        let html = "";
        requests.forEach(req => {
            const res = residentMap[req.hosteler_id];
            const hostelerStr = res ? `<span class="fw-bold">${res.name}</span><br><code class="small">${res.student_id} (${res.room_no})</code>` : `ID ${req.hosteler_id}`;

            const depTime = new Date(req.departure_time).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' });
            const retTime = new Date(req.expected_return).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' });

            let statusBadge = "";
            if (req.status === "APPROVED") statusBadge = `<span class="badge bg-success">APPROVED</span>`;
            else if (req.status === "PENDING") statusBadge = `<span class="badge bg-warning text-dark">PENDING</span>`;
            else if (req.status === "REJECTED") statusBadge = `<span class="badge bg-danger">REJECTED</span>`;
            else if (req.status === "EXITED") statusBadge = `<span class="badge bg-info text-dark">EXITED HOSTEL</span>`;
            else if (req.status === "RETURNED") statusBadge = `<span class="badge bg-secondary">RETURNED</span>`;

            let actionBtn = "";
            if (req.status === "PENDING") {
                actionBtn = `<button class="btn btn-sm btn-primary" onclick="openReviewModal(${req.id})"><i class="fa-solid fa-gavel me-1"></i> Review</button>`;
            } else {
                actionBtn = `<span class="small text-muted">Reviewed</span>`;
            }

            html += `
                <tr>
                    <td>${hostelerStr}</td>
                    <td><span class="badge bg-light text-dark border">${req.request_type}</span></td>
                    <td><strong>${req.destination}</strong><br><span class="small text-muted">${req.reason}</span></td>
                    <td class="small">${depTime}</td>
                    <td class="small">${retTime}</td>
                    <td><span class="small text-muted">${req.actual_exit_time ? 'Exited ' + new Date(req.actual_exit_time).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'}) : 'Not Exited'}</span></td>
                    <td>${statusBadge}</td>
                    <td class="text-end">${actionBtn}</td>
                </tr>
            `;
        });
        tbody.innerHTML = html;
    } catch (err) {
        showToast("Error loading outing requests: " + err.message, "error");
    }
}

async function populateOutingResidentDropdown() {
    try {
        const residents = await apiFetch("/api/residents");
        const select = document.getElementById("outing-resident-select");
        select.innerHTML = `<option value="">Select Resident Student...</option>`;
        residents.forEach(r => {
            select.innerHTML += `<option value="${r.id}">${r.name} (${r.student_id})</option>`;
        });
    } catch (err) {
        showToast("Could not load residents: " + err.message, "error");
    }
}

async function submitNewOuting(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);

    const payload = {
        hosteler_id: parseInt(formData.get("hosteler_id")),
        request_type: formData.get("request_type"),
        destination: formData.get("destination"),
        reason: formData.get("reason"),
        departure_time: new Date(formData.get("departure_time")).toISOString(),
        expected_return: new Date(formData.get("expected_return")).toISOString()
    };

    try {
        await apiFetch("/api/outing/request", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        showToast("Outing request submitted successfully!", "success");
        form.reset();
        bootstrap.Modal.getInstance(document.getElementById("newOutingModal")).hide();
        loadOutingRequests();
    } catch (err) {
        showToast("Error submitting request: " + err.message, "error");
    }
}

function openReviewModal(requestId) {
    document.getElementById("review-request-id").value = requestId;
    document.getElementById("review-remarks").value = "";
    new bootstrap.Modal(document.getElementById("reviewOutingModal")).show();
}

async function submitOutingReview(event) {
    event.preventDefault();
    const requestId = document.getElementById("review-request-id").value;
    const status = document.getElementById("review-status-select").value;
    const remarks = document.getElementById("review-remarks").value;

    try {
        await apiFetch(`/api/outing/request/${requestId}/status`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ status: status, remarks: remarks })
        });
        showToast(`Request marked as ${status}. Parent notified!`, "success");
        bootstrap.Modal.getInstance(document.getElementById("reviewOutingModal")).hide();
        loadOutingRequests();
    } catch (err) {
        showToast("Review submission failed: " + err.message, "error");
    }
}

document.addEventListener("DOMContentLoaded", loadOutingRequests);
