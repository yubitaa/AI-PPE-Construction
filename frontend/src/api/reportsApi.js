// src/api/reportsApi.js

import apiClient from "./client";

/**
 * Generate an AI daily safety report.
 *
 * POST /admin/reports/generate
 *
 * Body:
 * {
 *   target_date: "YYYY-MM-DD"
 * }
 *
 * @param {string} targetDate
 * @returns {Promise<Object>}
 */
export async function generateDailyReport(
    targetDate
) {
    if (!targetDate) {
        throw new Error(
            "targetDate is required."
        );
    }

    const response =
        await apiClient.post(
            "/admin/reports/generate",
            {
                target_date: targetDate,
            }
        );

    return response.data;
}

/**
 * Get an existing daily safety report.
 *
 * GET /admin/reports/{target_date}
 *
 * @param {string} targetDate
 * @returns {Promise<Object>}
 */
export async function getDailyReport(
    targetDate
) {
    if (!targetDate) {
        throw new Error(
            "targetDate is required."
        );
    }

    const response =
        await apiClient.get(
            `/admin/reports/${targetDate}`
        );

    return response.data;
}