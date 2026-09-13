// src/api/clockinApi.js

import apiClient from "./client";

/**
 * Upload a clock-in video.
 *
 * Backend flow:
 *
 * React
 *   ↓
 * FastAPI
 *   ↓
 * Phase 4 attendance processing
 *   ↓
 * Attendance result
 *
 * @param {File} videoFile
 * @param {(progress: number) => void} onUploadProgress
 * @returns {Promise<any>}
 */
export async function uploadClockInVideo(
  videoFile,
  onUploadProgress
) {
  if (!(videoFile instanceof File)) {
    throw new Error("A valid video file is required.");
  }

  const formData = new FormData();
  formData.append("video", videoFile);

  const response = await apiClient.post(
    "/clock-in/video",
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },

      onUploadProgress: (progressEvent) => {
        if (!onUploadProgress || !progressEvent.total) {
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
 * Send one temporary camera frame to the backend.
 *
 * Backend:
 *
 * Browser camera
 *   ↓
 * frame Blob
 *   ↓
 * FastAPI
 *   ↓
 * Phase 3 recognition / Phase 4 clock-in decision
 *   ↓
 * result
 *
 * @param {Blob} frameBlob
 * @returns {Promise<any>}
 */
export async function recognizeCameraFrame(frameBlob) {
  if (!(frameBlob instanceof Blob)) {
    throw new Error(
      "A valid camera frame is required."
    );
  }

  const formData = new FormData();

  formData.append(
    "frame",
    frameBlob,
    "camera-frame.jpg"
  );

  const response = await apiClient.post(
    "/clock-in/camera/frame",
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );

  return response.data;
}