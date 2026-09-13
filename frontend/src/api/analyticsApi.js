// src/api/analyticsApi.js

import apiClient from "./client";

/**
 * Get daily analytics.
 *
 * GET /admin/analytics/{target_date}
 *
 * @param {string} targetDate
 * @returns {Promise<Object>}
 */
export async function getDailyAnalytics(targetDate) {
  if (!targetDate) {
    throw new Error("targetDate is required.");
  }

  const response = await apiClient.get(
    `/admin/analytics/${targetDate}`
  );

  return response.data;
}