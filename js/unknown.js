/* Unknown Person Security Review JS Controller */

async function loadUnknownEvents() {
    try {
        const filter = document.getElementById("unknown-status-filter").value;
        let query = "/api/unknown/events";
        if (filter) query += `?status_filter=${filter}`;

        const events = await apiFetch(query);
        const tbody = document.getElementById("unknown-tbody");

        if (events.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" class="text-center text-muted py-4">No unknown person security events found.</td></tr>`;
            return;
        }

        let html = "";
        events.forEach(evt => {
            const timeStr = new Date(evt.captured_at).toLocaleString([], { dateStyle: 'short', timeStyle: 'medium' });
            
            let statusBadge = "";
            if (evt.review_status === "PENDING") statusBadge = `<span class="badge bg-danger">PENDING REVIEW</span>`;
            else if (evt.review_status === "REVIEWED") statusBadge = `<span class="badge bg-warning text-dark">REVIEWED</span>`;
            else if (evt.review_status === "RESOLVED") statusBadge = `<span class="badge bg-success">RESOLVED</span>`;
            else if (evt.review_status === "DISMISSED") statusBadge = `<span class="badge bg-secondary">DISMISSED</span>`;

            html += `
                <tr>
                    <td><img src="${evt.image_path}" class="snapshot-img" alt="Unknown Evidence" onclick="window.open('${evt.image_path}', '_blank')"></td>
                    <td class="small fw-bold">${timeStr}</td>
                    <td>${evt.gate}</td>
                    <td>${statusBadge}</td>
                    <td class="small text-muted">${evt.remarks || 'No remarks added yet.'}</td>
                    <td class="text-end">
                        <button class="btn btn-sm btn-outline-primary" onclick="openUnknownReviewModal(${evt.id}, '${evt.image_path}')">
                            <i class="fa-solid fa-user-shield me-1"></i> Review
                        </button>
                    </td>
                </tr>
            `;
        });
        tbody.innerHTML = html;
    } catch (err) {
        showToast("Error loading unknown alerts: " + err.message, "error");
    }
}

function openUnknownReviewModal(id, imgPath) {
    document.getElementById("review-unknown-id").value = id;
    document.getElementById("review-unknown-img").src = imgPath;
    document.getElementById("review-unknown-remarks").value = "";
    new bootstrap.Modal(document.getElementById("reviewUnknownModal")).show();
}

async function submitUnknownReview(event) {
    event.preventDefault();
    const eventId = document.getElementById("review-unknown-id").value;
    const status = document.getElementById("review-unknown-status").value;
    const remarks = document.getElementById("review-unknown-remarks").value;

    try {
        await apiFetch(`/api/unknown/event/${eventId}/review`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ review_status: status, remarks: remarks })
        });
        showToast("Security review updated successfully!", "success");
        bootstrap.Modal.getInstance(document.getElementById("reviewUnknownModal")).hide();
        loadUnknownEvents();
    } catch (err) {
        showToast("Error updating review: " + err.message, "error");
    }
}

document.addEventListener("DOMContentLoaded", loadUnknownEvents);
