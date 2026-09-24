// src/pages/admin/Attendance.jsx

import { useMemo, useState } from "react";

import {
  AlertCircle,
  Calendar,
  Download,
  Filter,
  RefreshCw,
  Search,
  X,
} from "lucide-react";

import { useAttendance } from "../../hooks/useAttendance";
import { useWorkers } from "../../hooks/useWorkers";

function formatDateForDisplay(dateString) {
  if (!dateString) {
    return "";
  }

  const date = new Date(
    `${dateString}T00:00:00`
  );

  return date.toLocaleDateString(
    undefined,
    {
      year: "numeric",
      month: "long",
      day: "numeric",
    }
  );
}

function formatTimestamp(timestamp) {
  if (!timestamp) {
    return "—";
  }

  const date = new Date(timestamp);

  if (Number.isNaN(date.getTime())) {
    return String(timestamp);
  }

  return date.toLocaleTimeString(
    undefined,
    {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    }
  );
}

function getStatusBadge(status) {
  const normalized = String(
    status || ""
  ).toUpperCase();

  switch (normalized) {
    case "CLOCKED_IN":
      return (
        <span className="bg-green-100 text-green-800 px-2.5 py-0.5 rounded-full text-xs font-medium">
          Present
        </span>
      );

    case "ALREADY_CLOCKED_IN":
      return (
        <span className="bg-blue-100 text-blue-800 px-2.5 py-0.5 rounded-full text-xs font-medium">
          Already Clocked In
        </span>
      );

    default:
      return (
        <span className="bg-gray-100 text-gray-700 px-2.5 py-0.5 rounded-full text-xs font-medium">
          {status || "Unknown"}
        </span>
      );
  }
}

function normalizeAttendanceRecord(record) {
  return {
    ...record,

    id:
      record?.id ??
      record?.worker_id,

    workerId:
      record?.worker_id ??
      record?.workerId ??
      null,

    workerName:
      record?.worker_name ??
      record?.workerName ??
      "Unknown Worker",

    status:
      record?.status ??
      "UNKNOWN",

    timestamp:
      record?.timestamp ??
      null,

    clockOut:
      record?.clock_out ??
      record?.clockOut ??
      null,

    confidenceScore:
      record?.confidence_score ??
      record?.confidenceScore ??
      null,
  };
}

function exportToCsv(records, date) {
  if (!records.length) {
    return;
  }

  const rows = [
    [
      "Worker Name",
      "Worker ID",
      "Timestamp",
      "Status",
      "Confidence",
    ],
    ...records.map((record) => {
      const item =
        normalizeAttendanceRecord(
          record
        );

      return [
        item.workerName,
        item.workerId,
        item.timestamp ?? "",
        item.status,
        item.confidenceScore ?? "",
      ];
    }),
  ];

  const csv = rows
    .map((row) =>
      row
        .map((value) =>
          `"${String(value).replaceAll(
            '"',
            '""'
          )}"`
        )
        .join(",")
    )
    .join("\n");

  const blob = new Blob([csv], {
    type: "text/csv;charset=utf-8;",
  });

  const url =
    URL.createObjectURL(blob);

  const link =
    document.createElement("a");

  link.href = url;
  link.download = `attendance-${date}.csv`;
  document.body.appendChild(link);
  link.click();
  link.remove();

  URL.revokeObjectURL(url);
}

export default function Attendance() {
  const today =
    new Date()
      .toISOString()
      .split("T")[0];

  const [selectedDate, setSelectedDate] =
    useState(today);

  const [workerId, setWorkerId] =
    useState("");

  const [filterOpen, setFilterOpen] =
    useState(false);

  const {
    records,
    loading,
    error,
    loadAttendance,
  } = useAttendance({
    date: selectedDate,
    workerId,
  });

  const { workers } =
    useWorkers();

  const normalizedRecords =
    useMemo(
      () =>
        records.map(
          normalizeAttendanceRecord
        ),
      [records]
    );

  const handleDateChange = async (
    event
  ) => {
    const value =
      event.target.value;

    setSelectedDate(value);

    await loadAttendance({
      requestedDate: value,
      requestedWorkerId: workerId,
    });
  };

  const handleWorkerChange = async (
    event
  ) => {
    const value =
      event.target.value;

    setWorkerId(value);

    await loadAttendance({
      requestedDate: selectedDate,
      requestedWorkerId: value,
    });
  };

  const handleClearFilter = async () => {
    setWorkerId("");

    await loadAttendance({
      requestedDate: selectedDate,
      requestedWorkerId: "",
    });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex sm:items-center justify-between flex-col sm:flex-row gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Daily Attendance
          </h1>

          <p className="text-sm text-gray-500 mt-1">
            Review clock-in records for workers.
          </p>
        </div>

        <div className="flex space-x-3">
          <button
            type="button"
            onClick={() =>
              setFilterOpen(
                !filterOpen
              )
            }
            className="inline-flex items-center px-4 py-2 bg-white border border-gray-200 hover:bg-gray-50 text-gray-700 text-sm font-medium rounded-lg shadow-sm transition-colors"
          >
            <Filter className="h-4 w-4 mr-2" />
            Filter
          </button>

          <button
            type="button"
            onClick={() =>
              exportToCsv(
                normalizedRecords,
                selectedDate
              )
            }
            disabled={
              loading ||
              normalizedRecords.length === 0
            }
            className="inline-flex items-center px-4 py-2 bg-white border border-gray-200 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed text-gray-700 text-sm font-medium rounded-lg shadow-sm transition-colors"
          >
            <Download className="h-4 w-4 mr-2" />
            Export
          </button>
        </div>
      </div>

      {/* Filter panel */}
      {filterOpen && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <div className="flex flex-col md:flex-row md:items-end gap-4">
            <div className="w-full md:max-w-sm">
              <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
                Worker
              </label>

              <select
                value={workerId}
                onChange={handleWorkerChange}
                className="w-full px-3 py-2.5 border border-gray-200 rounded-lg text-sm bg-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              >
                <option value="">
                  All workers
                </option>

                {workers.map((worker) => (
                  <option
                    key={
                      worker.worker_id ??
                      worker.id
                    }
                    value={
                      worker.worker_id ??
                      worker.id
                    }
                  >
                    {worker.name ??
                      worker.worker_name ??
                      worker.employee_id ??
                      "Worker"}
                  </option>
                ))}
              </select>
            </div>

            {workerId && (
              <button
                type="button"
                onClick={handleClearFilter}
                className="inline-flex items-center px-3 py-2.5 bg-gray-100 hover:bg-gray-200 text-gray-700 text-sm font-medium rounded-lg"
              >
                <X className="h-4 w-4 mr-1.5" />
                Clear
              </button>
            )}
          </div>
        </div>
      )}

      {/* Main card */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="p-4 border-b border-gray-100 bg-gray-50/50 flex items-center justify-between">
          <div className="flex items-center text-gray-600 text-sm font-medium">
            <Calendar className="h-4 w-4 mr-2" />

            {formatDateForDisplay(
              selectedDate
            )}
          </div>

          <input
            type="date"
            value={selectedDate}
            onChange={handleDateChange}
            className="px-3 py-1.5 border border-gray-200 rounded-lg bg-white text-sm text-gray-700 outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Error */}
        {error && (
          <div className="m-4 bg-red-50 border border-red-200 rounded-xl p-4 flex items-center justify-between gap-3 text-sm text-red-700">
            <div className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5 flex-shrink-0" />

              <span>
                {error.message ||
                  "Failed to load attendance records."}
              </span>
            </div>

            <button
              type="button"
              onClick={() =>
                loadAttendance({
                  requestedDate:
                    selectedDate,
                  requestedWorkerId:
                    workerId,
                })
              }
              className="inline-flex items-center gap-1.5 font-semibold underline"
            >
              <RefreshCw className="h-4 w-4" />
              Retry
            </button>
          </div>
        )}

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-gray-100 text-gray-500 text-xs uppercase tracking-wider">
                <th className="px-6 py-4 font-semibold">
                  Worker Name
                </th>

                <th className="px-6 py-4 font-semibold">
                  Clock In
                </th>

                <th className="px-6 py-4 font-semibold">
                  Clock Out
                </th>

                <th className="px-6 py-4 font-semibold">
                  Status
                </th>
              </tr>
            </thead>

            <tbody className="divide-y divide-gray-100 text-sm">
              {loading ? (
                <tr>
                  <td
                    colSpan="4"
                    className="px-6 py-10 text-center text-gray-500"
                  >
                    <div className="inline-flex items-center gap-2">
                      <RefreshCw className="h-4 w-4 animate-spin" />
                      Loading attendance...
                    </div>
                  </td>
                </tr>
              ) : normalizedRecords.length ===
                0 ? (
                <tr>
                  <td
                    colSpan="4"
                    className="px-6 py-12 text-center"
                  >
                    <Search className="h-10 w-10 text-gray-300 mx-auto mb-3" />

                    <p className="font-medium text-gray-700">
                      No attendance records
                    </p>

                    <p className="text-sm text-gray-400 mt-1">
                      There are no records for the
                      selected date/filter.
                    </p>
                  </td>
                </tr>
              ) : (
                normalizedRecords.map(
                  (log) => (
                    <tr
                      key={`${log.workerId}-${log.timestamp}`}
                      className="hover:bg-gray-50 transition-colors"
                    >
                      <td className="px-6 py-4 font-medium text-gray-900">
                        {log.workerName}
                      </td>

                      <td className="px-6 py-4 text-gray-500 font-mono">
                        {formatTimestamp(
                          log.timestamp
                        )}
                      </td>

                      <td className="px-6 py-4 text-gray-500 font-mono">
                        {formatTimestamp(log.clockOut)}
                      </td>

                      <td className="px-6 py-4">
                        {getStatusBadge(
                          log.status
                        )}
                      </td>
                    </tr>
                  )
                )
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}