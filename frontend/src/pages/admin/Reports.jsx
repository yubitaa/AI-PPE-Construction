// src/pages/admin/Reports.jsx

import { useEffect, useState } from "react";

import {
  AlertCircle,
  Calendar,
  CheckCircle2,
  FileDown,
  FileText,
  Loader2,
  RefreshCw,
} from "lucide-react";

import {
  generateDailyReport,
  getDailyReport,
} from "../../api/reportsApi";

function getToday() {
  return new Date()
    .toISOString()
    .split("T")[0];
}

export default function Reports() {
  const [targetDate, setTargetDate] =
    useState(getToday());

  const [report, setReport] =
    useState(null);

  const [loading, setLoading] =
    useState(false);

  const [loadingExisting, setLoadingExisting] =
    useState(true);

  const [error, setError] =
    useState("");

  const [successMessage, setSuccessMessage] =
    useState("");

  const loadExistingReport =
    async (date) => {
      setLoadingExisting(true);
      setError("");
      setSuccessMessage("");

      try {
        const response =
          await getDailyReport(date);

        setReport(response);
      } catch (err) {
        /*
         * A missing report is not treated as a
         * catastrophic page error. The user can
         * generate one.
         */
        setReport(null);

        if (
          err?.status &&
          err.status !== 404
        ) {
          setError(
            err.message ||
            "Failed to load the existing report."
          );
        }
      } finally {
        setLoadingExisting(false);
      }
    };

  useEffect(() => {
    loadExistingReport(targetDate);
  }, [targetDate]);

  const handleGenerate = async () => {
    setLoading(true);
    setError("");
    setSuccessMessage("");

    try {
      const response =
        await generateDailyReport(
          targetDate
        );

      setReport(response);

      setSuccessMessage(
        "Daily safety report generated successfully."
      );
    } catch (err) {
      setError(
        err?.message ||
        "Failed to generate the safety report."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh =
    async () => {
      await loadExistingReport(
        targetDate
      );
    };

  const reportContent =
    report?.report_content ??
    report?.reportContent ??
    "";

  return (
    <div className="space-y-6 max-w-5xl">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">
          Daily Safety Report
        </h1>

        <p className="text-sm text-gray-500 mt-1">
          Generate and review the AI-generated
          safety report for a selected day.
        </p>
      </div>

      {/* Controls */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="p-6 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Target date */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Report Date
              </label>

              <div className="relative">
                <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400 pointer-events-none" />

                <input
                  type="date"
                  value={targetDate}
                  onChange={(event) =>
                    setTargetDate(
                      event.target.value
                    )
                  }
                  className="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white outline-none"
                />
              </div>
            </div>

            {/* Report type - informational */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Report Type
              </label>

              <div className="relative">
                <FileText className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />

                <div className="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-lg text-sm text-gray-600 bg-gray-50">
                  Daily AI Safety Report
                </div>
              </div>
            </div>
          </div>

          {/* Messages */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-700 flex items-center gap-2">
              <AlertCircle className="h-5 w-5 flex-shrink-0" />

              <span>{error}</span>
            </div>
          )}

          {successMessage && (
            <p className="text-sm text-green-600 flex items-center font-medium bg-green-50 px-3 py-2 rounded-lg border border-green-100">
              <CheckCircle2 className="h-4 w-4 mr-2" />
              {successMessage}
            </p>
          )}

          {/* Actions */}
          <div className="pt-4 flex items-center justify-between border-t border-gray-100">
            <button
              type="button"
              onClick={handleRefresh}
              disabled={loadingExisting}
              className="inline-flex items-center px-4 py-2.5 bg-white border border-gray-200 hover:bg-gray-50 disabled:opacity-50 text-gray-700 text-sm font-medium rounded-lg"
            >
              <RefreshCw
                className={`h-4 w-4 mr-2 ${loadingExisting
                    ? "animate-spin"
                    : ""
                  }`}
              />

              Refresh
            </button>

            <button
              type="button"
              onClick={handleGenerate}
              disabled={loading}
              className="inline-flex items-center px-6 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white text-sm font-medium rounded-lg shadow-sm transition-all"
            >
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <FileDown className="h-4 w-4 mr-2" />
                  Generate Report
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Existing/generated report */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">
              Safety Report
            </h2>

            <p className="text-xs text-gray-400 mt-1">
              {targetDate}
            </p>
          </div>

          {reportContent && (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-green-100 text-green-700 text-xs font-medium">
              <CheckCircle2 className="h-3.5 w-3.5" />
              Available
            </span>
          )}
        </div>

        <div className="p-6">
          {loadingExisting && !report ? (
            <div className="py-16 flex items-center justify-center text-gray-500">
              <Loader2 className="h-5 w-5 mr-2 animate-spin" />
              Loading report...
            </div>
          ) : reportContent ? (
            <div className="whitespace-pre-wrap text-sm leading-7 text-gray-700">
              {reportContent}
            </div>
          ) : (
            <div className="py-16 text-center">
              <FileText className="h-10 w-10 text-gray-300 mx-auto mb-3" />

              <p className="font-medium text-gray-700">
                No report available
              </p>

              <p className="text-sm text-gray-400 mt-1">
                Generate the daily safety report
                for {targetDate}.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}