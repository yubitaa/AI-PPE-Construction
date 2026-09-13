// src/api/workersApi.js

import apiClient from "./client";

/**
 * Get all workers.
 *
 * GET /admin/workers
 *
 * @returns {Promise<Array>}
 */
export async function getWorkers() {
    const response = await apiClient.get("/admin/workers");

    return response.data;
}

/**
 * Get one worker.
 *
 * GET /admin/workers/{worker_id}
 *
 * @param {string} workerId
 * @returns {Promise<Object>}
 */
export async function getWorker(workerId) {
    if (!workerId) {
        throw new Error("workerId is required.");
    }

    const response = await apiClient.get(
        `/admin/workers/${workerId}`
    );

    return response.data;
}

/**
 * Create a worker.
 *
 * POST /admin/workers
 *
 * multipart/form-data:
 * - name
 * - employee_id
 * - role
 * - department
 * - tag_id (optional)
 * - face_images[] (required)
 *
 * @param {Object} workerData
 * @returns {Promise<Object>}
 */
export async function createWorker({
    name,
    employee_id,
    role,
    department,
    tag_id,
    face_images,
}) {
    if (!name?.trim()) {
        throw new Error("Worker name is required.");
    }

    if (!employee_id?.trim()) {
        throw new Error("Employee ID is required.");
    }

    if (!role?.trim()) {
        throw new Error("Worker role is required.");
    }

    if (!department?.trim()) {
        throw new Error("Department is required.");
    }

    if (!Array.isArray(face_images) || face_images.length === 0) {
        throw new Error(
            "At least one face image is required."
        );
    }

    const formData = new FormData();

    formData.append("name", name.trim());
    formData.append(
        "employee_id",
        employee_id.trim()
    );
    formData.append("role", role.trim());
    formData.append(
        "department",
        department.trim()
    );

    if (tag_id?.trim()) {
        formData.append("tag_id", tag_id.trim());
    }

    face_images.forEach((file) => {
        formData.append("face_images", file);
    });

    const response = await apiClient.post(
        "/admin/workers",
        formData,
        {
            headers: {
                "Content-Type": "multipart/form-data",
            },
        }
    );

    return response.data;
}

/**
 * Update a worker.
 *
 * PUT /admin/workers/{worker_id}
 *
 * JSON:
 * {
 *   name?,
 *   employee_id?,
 *   role?,
 *   department?,
 *   tag_id?
 * }
 *
 * @param {string} workerId
 * @param {Object} workerData
 * @returns {Promise<Object>}
 */
export async function updateWorker(
    workerId,
    workerData
) {
    if (!workerId) {
        throw new Error("workerId is required.");
    }

    if (!workerData || typeof workerData !== "object") {
        throw new Error("workerData must be an object.");
    }

    const response = await apiClient.put(
        `/admin/workers/${workerId}`,
        workerData
    );

    return response.data;
}

/**
 * Delete a worker.
 *
 * DELETE /admin/workers/{worker_id}
 *
 * @param {string} workerId
 * @returns {Promise<Object>}
 */
export async function deleteWorker(workerId) {
    if (!workerId) {
        throw new Error("workerId is required.");
    }

    const response = await apiClient.delete(
        `/admin/workers/${workerId}`
    );

    return response.data;
}

/**
 * Identify a worker from a face image.
 *
 * POST /admin/workers/identify
 *
 * multipart/form-data:
 * face_image: File
 *
 * @param {File} faceImage
 * @returns {Promise<Object>}
 */
export async function identifyWorker(faceImage) {
    if (!(faceImage instanceof File)) {
        throw new Error(
            "A valid face image is required."
        );
    }

    const formData = new FormData();

    formData.append("face_image", faceImage);

    const response = await apiClient.post(
        "/admin/workers/identify",
        formData,
        {
            headers: {
                "Content-Type": "multipart/form-data",
            },
        }
    );

    return response.data;
}