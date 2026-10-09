/* Parents Management JS Controller */

async function loadParents() {
    try {
        const parents = await apiFetch("/api/parents");
        const tbody = document.getElementById("parents-tbody");

        if (parents.length === 0) {
            tbody.innerHTML = `<tr><td colspan="8" class="text-center text-muted py-4">No parent/guardian details registered yet.</td></tr>`;
            return;
        }

        // Fetch residents map to resolve student names
        const residents = await apiFetch("/api/residents");
        const residentMap = {};
        residents.forEach(r => residentMap[r.id] = r);

        let html = "";
        parents.forEach(p => {
            const res = residentMap[p.hosteler_id];
            const hostelerStr = res ? `<span class="fw-bold">${res.name}</span> <code class="ms-1">${res.student_id}</code>` : `ID ${p.hosteler_id}`;

            html += `
                <tr>
                    <td>${hostelerStr}</td>
                    <td class="fw-bold">${p.name}</td>
                    <td><span class="badge bg-light text-dark border">${p.relationship}</span></td>
                    <td>${p.phone}</td>
                    <td>${p.email}</td>
                    <td>${p.whatsapp_number || '-'}</td>
                    <td><span class="badge bg-info text-dark">${p.notification_preference.toUpperCase()}</span></td>
                    <td class="text-end">
                        <button class="btn btn-sm btn-outline-danger" onclick="deleteParent(${p.id})">
                            <i class="fa-solid fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `;
        });
        tbody.innerHTML = html;
    } catch (err) {
        showToast("Error loading parent records: " + err.message, "error");
    }
}

async function populateResidentDropdown() {
    try {
        const residents = await apiFetch("/api/residents");
        const select = document.getElementById("resident-select");
        select.innerHTML = `<option value="">Select Resident Student...</option>`;
        residents.forEach(r => {
            select.innerHTML += `<option value="${r.id}">${r.name} (${r.student_id} - Room ${r.room_no})</option>`;
        });
    } catch (err) {
        showToast("Could not load residents for selection: " + err.message, "error");
    }
}

async function submitAddParent(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);

    const payload = {
        hosteler_id: parseInt(formData.get("hosteler_id")),
        name: formData.get("name"),
        relationship: formData.get("relationship"),
        phone: formData.get("phone"),
        email: formData.get("email"),
        whatsapp_number: formData.get("whatsapp_number") || null,
        notification_preference: formData.get("notification_preference")
    };

    try {
        await apiFetch("/api/parents", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        showToast("Parent details saved successfully!", "success");
        form.reset();
        bootstrap.Modal.getInstance(document.getElementById("addParentModal")).hide();
        loadParents();
    } catch (err) {
        showToast("Failed to add parent: " + err.message, "error");
    }
}

async function deleteParent(id) {
    if (!confirm("Are you sure you want to delete this parent record?")) return;
    try {
        await apiFetch(`/api/parents/${id}`, { method: "DELETE" });
        showToast("Parent record removed.", "info");
        loadParents();
    } catch (err) {
        showToast("Delete failed: " + err.message, "error");
    }
}

document.addEventListener("DOMContentLoaded", loadParents);
