// src/api/reportsApi.js

import apiClient from "./client";

/**
 * Generate an AI daily safety report.
 *
 * POST /reports/generate
 *
 * Body:
 * {
 *   target_date: "YYYY-MM-DD"
 * }
 *
 * @param {string} targetDate
 * @returns {Promise<Object>}
 */
export async function generateDailyReport(targetDate) {
    if (!targetDate) {
        throw new Error("targetDate is required.");
    }

    const response = await apiClient.post(
        "/reports/generate",
        {
            target_date: targetDate,
        }
    );

    return response.data;
}

/**
 * Get an existing daily safety report.
 *
 * GET /reports/{target_date}
 *
 * @param {string} targetDate
 * @returns {Promise<Object>}
 */
export async function getDailyReport(targetDate) {
    if (!targetDate) {
        throw new Error("targetDate is required.");
    }

    const response = await apiClient.get(
        `/reports/${targetDate}`
    );

    return response.data;
}

/**
 * Get daily analytics metrics (Phase 8).
 *
 * GET /analytics/{target_date}
 *
 * @param {string} targetDate
 * @returns {Promise<Object>}
 */
export async function getDailyAnalytics(targetDate) {
    if (!targetDate) {
        throw new Error("targetDate is required.");
    }

    const response = await apiClient.get(
        `/analytics/${targetDate}`
    );

    return response.data;
}