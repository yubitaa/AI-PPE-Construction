// src/api/ppeApi.js

import apiClient from "./client";

/**
 * Upload a PPE monitoring video.
 *
 * POST /ppe/upload
 *
 * multipart/form-data:
 * - video_file: File
 * - frame_skip: optional integer
 *
 * @param {File} videoFile
 * @param {number} frameSkip
 * @param {(progress: number) => void} onUploadProgress
 * @returns {Promise<Object>}
 */
export async function uploadPPEVideo(
    videoFile,
    frameSkip,
    onUploadProgress
) {
    if (!(videoFile instanceof File)) {
        throw new Error("A valid video file is required.");
    }

    const formData = new FormData();

    formData.append("video_file", videoFile);

    if (
        frameSkip !== undefined &&
        frameSkip !== null &&
        frameSkip !== ""
    ) {
        formData.append(
            "frame_skip",
            String(frameSkip)
        );
    }

    const response = await apiClient.post(
        "/ppe/upload",
        formData,
        {
            headers: {
                "Content-Type": "multipart/form-data",
            },

            onUploadProgress: (progressEvent) => {
                if (
                    !onUploadProgress ||
                    !progressEvent.total
                ) {
                    return;
                }

                const progress = Math.round(
                    (progressEvent.loaded * 100) /
                    progressEvent.total
                );

                onUploadProgress(progress);
            },
        }
    );

    return response.data;
}

/**
 * Get PPE compliance results.
 *
 * GET /ppe/results
 *
 * Optional query parameters:
 * - date=YYYY-MM-DD
 * - worker_id=UUID
 *
 * @param {Object} params
 * @param {string} params.date
 * @param {string} params.worker_id
 * @returns {Promise<Array>}
 */
export async function getPPEResults({
    date,
    worker_id,
} = {}) {
    const params = {};

    if (date) {
        params.date = date;
    }

    if (worker_id) {
        params.worker_id = worker_id;
    }

    const response = await apiClient.get(
        "/ppe/results",
        {
            params,
        }
    );

    return response.data;
}

/**
 * Get PPE results for one worker.
 *
 * Convenience wrapper around the same endpoint.
 *
 * @param {string} workerId
 * @param {string} date
 * @returns {Promise<Array>}
 */
export async function getWorkerPPE(
    workerId,
    date
) {
    return getPPEResults({
        worker_id: workerId,
        date,
    });
}