// src/api/attendanceApi.js

import apiClient from "./client";

/**
 * Get attendance records.
 *
 * GET /attendance
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
export async function getAttendance({
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
    "/attendance",
    { params }
  );

  return response.data;
}

/**
 * Get attendance for one specific worker and date.
 *
 * Convenience wrapper around the same endpoint.
 *
 * @param {string} workerId
 * @param {string} date
 * @returns {Promise<Array>}
 */
export async function getWorkerAttendance(
  workerId,
  date
) {
  return getAttendance({
    date,
    worker_id: workerId,
  });
}