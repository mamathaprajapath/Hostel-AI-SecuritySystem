/* Residents Management JS Controller */

async function loadResidents() {
    try {
        const search = document.getElementById("search-input").value;
        const state = document.getElementById("state-filter").value;

        let query = "/api/residents?";
        if (search) query += `search=${encodeURIComponent(search)}&`;
        if (state) query += `state_filter=${encodeURIComponent(state)}&`;

        const residents = await apiFetch(query);
        const tbody = document.getElementById("residents-tbody");

        if (residents.length === 0) {
            tbody.innerHTML = `<tr><td colspan="9" class="text-center text-muted py-4">No resident hostelers found.</td></tr>`;
            return;
        }

        let html = "";
        residents.forEach(res => {
            const photoSrc = res.photo_path || "https://via.placeholder.com/150?text=No+Photo";
            const stateBadge = res.current_state === "INSIDE" ? "badge bg-success" : "badge bg-danger";
            const faceBadge = res.face_enrolled ? '<span class="badge bg-success"><i class="fa-solid fa-circle-check me-1"></i> Enrolled</span>' : '<span class="badge bg-warning text-dark"><i class="fa-solid fa-clock me-1"></i> Pending</span>';

            html += `
                <tr>
                    <td><img src="${photoSrc}" class="avatar-img" alt="${res.name}"></td>
                    <td><code>${res.student_id}</code></td>
                    <td class="fw-bold">${res.name}</td>
                    <td>${res.room_no}</td>
                    <td>${res.department}</td>
                    <td>${res.phone}</td>
                    <td><span class="${stateBadge}">${res.current_state}</span></td>
                    <td>${faceBadge}</td>
                    <td class="text-end">
                        <button class="btn btn-sm btn-outline-success me-1" onclick="openEnrollModal(${res.id}, '${res.name}')">
                            <i class="fa-solid fa-camera"></i> Enroll Face
                        </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="deleteResident(${res.id})">
                            <i class="fa-solid fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `;
        });
        tbody.innerHTML = html;
    } catch (err) {
        showToast("Error loading residents: " + err.message, "error");
    }
}

async function submitAddResident(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);

    const payload = {
        student_id: formData.get("student_id"),
        name: formData.get("name"),
        room_no: formData.get("room_no"),
        department: formData.get("department"),
        phone: formData.get("phone"),
        email: formData.get("email") || null
    };

    try {
        await apiFetch("/api/residents", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        showToast("Hosteler registered successfully!", "success");
        form.reset();
        bootstrap.Modal.getInstance(document.getElementById("addResidentModal")).hide();
        loadResidents();
    } catch (err) {
        showToast(err.message, "error");
    }
}

function openEnrollModal(id, name) {
    document.getElementById("enroll-resident-id").value = id;
    document.getElementById("enroll-resident-name").value = name;
    document.getElementById("enroll-error-alert").classList.add("d-none");
    document.getElementById("face-file-input").value = "";
    new bootstrap.Modal(document.getElementById("enrollFaceModal")).show();
}

async function submitFaceEnrollment(event) {
    event.preventDefault();
    const residentId = document.getElementById("enroll-resident-id").value;
    const fileInput = document.getElementById("face-file-input");
    const errorAlert = document.getElementById("enroll-error-alert");
    const btnSubmit = document.getElementById("btn-submit-enroll");

    if (!fileInput.files || fileInput.files.length === 0) {
        errorAlert.innerText = "Please select an image file to upload.";
        errorAlert.classList.remove("d-none");
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    try {
        btnSubmit.disabled = true;
        btnSubmit.innerHTML = `<span class="spinner-border spinner-border-sm me-1"></span> Validating & Training...`;

        const response = await fetch(`/api/faces/enroll/${residentId}`, {
            method: "POST",
            body: formData
        });

        const result = await response.json();
        if (!response.ok) {
            throw new Error(result.detail || "Enrollment failed.");
        }

        showToast("Face enrolled and AI engine retrained successfully!", "success");
        bootstrap.Modal.getInstance(document.getElementById("enrollFaceModal")).hide();
        loadResidents();
    } catch (err) {
        errorAlert.innerText = err.message;
        errorAlert.classList.remove("d-none");
    } finally {
        btnSubmit.disabled = false;
        btnSubmit.innerHTML = `<i class="fa-solid fa-upload me-1"></i> Enroll & Train AI`;
    }
}

async function deleteResident(id) {
    if (!confirm("Are you sure you want to delete this resident record?")) return;
    try {
        await apiFetch(`/api/residents/${id}`, { method: "DELETE" });
        showToast("Resident record deleted.", "info");
        loadResidents();
    } catch (err) {
        showToast("Delete failed: " + err.message, "error");
    }
}

document.addEventListener("DOMContentLoaded", loadResidents);
