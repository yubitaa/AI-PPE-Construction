// src/pages/admin/PPE.jsx

import { useMemo, useState } from "react";

import {
  AlertCircle,
  Calendar,
  CheckCircle2,
  Filter,
  HardHat,
  RefreshCw,
  Search,
  ShieldAlert,
  Shirt,
  X,
} from "lucide-react";

import { usePPE } from "../../hooks/usePPE";
import { useWorkers } from "../../hooks/useWorkers";

const PPE_STATUS = {
  FULL_PPE: "FULL_PPE",
  HELMET_MISSING: "HELMET_MISSING",
  VEST_MISSING: "VEST_MISSING",
  NO_PPE: "NO_PPE",
};

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

function formatVideoTimestamp(value) {
  if (
    value === null ||
    value === undefined ||
    value === ""
  ) {
    return "—";
  }

  const seconds = Number(value);

  if (!Number.isFinite(seconds)) {
    return String(value);
  }

  const hours = Math.floor(
    seconds / 3600
  );

  const minutes = Math.floor(
    (seconds % 3600) / 60
  );

  const remainingSeconds = Math.floor(
    seconds % 60
  );

  const milliseconds = Math.floor(
    (seconds - Math.floor(seconds)) *
    1000
  );

  if (hours > 0) {
    return `${String(hours).padStart(
      2,
      "0"
    )}:${String(minutes).padStart(
      2,
      "0"
    )}:${String(remainingSeconds).padStart(
      2,
      "0"
    )}`;
  }

  if (milliseconds > 0) {
    return `${String(minutes).padStart(
      2,
      "0"
    )}:${String(remainingSeconds).padStart(
      2,
      "0"
    )}.${String(milliseconds).padStart(
      3,
      "0"
    )}`;
  }

  return `${String(minutes).padStart(
    2,
    "0"
  )}:${String(remainingSeconds).padStart(
    2,
    "0"
  )}`;
}

function normalizePPERecord(record, workerName) {
  const status = String(
    record?.compliance_status ??
    record?.complianceStatus ??
    record?.status ??
    ""
  ).toUpperCase();

  return {
    ...record,

    id:
      record?.log_id ??
      `${record?.worker_id}-${record?.start_timestamp}`,

    workerId:
      record?.worker_id ??
      null,

    workerName:
      record?.name ??
      workerName ??
      "Unknown Worker",

    videoId:
      record?.video_id ??
      null,

    startTimestamp:
      record?.start_timestamp ??
      null,

    endTimestamp:
      record?.end_timestamp ??
      null,

    helmetDetected:
      Boolean(
        record?.helmet_detected ??
        record?.helmetDetected
      ),

    vestDetected:
      Boolean(
        record?.vest_detected ??
        record?.vestDetected
      ),

    status,
  };
}

function StatusBadge({ status }) {
  switch (status) {
    case PPE_STATUS.FULL_PPE:
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-green-100 text-green-800">
          <CheckCircle2 className="h-3.5 w-3.5" />
          FULL PPE
        </span>
      );

    case PPE_STATUS.HELMET_MISSING:
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-orange-100 text-orange-800">
          <HardHat className="h-3.5 w-3.5" />
          Helmet Missing
        </span>
      );

    case PPE_STATUS.VEST_MISSING:
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-yellow-100 text-yellow-800">
          <Shirt className="h-3.5 w-3.5" />
          Vest Missing
        </span>
      );

    case PPE_STATUS.NO_PPE:
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-red-100 text-red-800">
          <ShieldAlert className="h-3.5 w-3.5" />
          No PPE
        </span>
      );

    default:
      return (
        <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-gray-100 text-gray-700">
          Unknown
        </span>
      );
  }
}

function PPEIndicator({
  detected,
  icon: Icon,
  label,
}) {
  return (
    <div className="flex items-center gap-2">
      <div
        className={`p-1.5 rounded-lg ${detected
            ? "bg-green-100 text-green-600"
            : "bg-red-100 text-red-500"
          }`}
      >
        <Icon className="h-4 w-4" />
      </div>

      <span
        className={`text-xs font-medium ${detected
            ? "text-green-700"
            : "text-red-600"
          }`}
      >
        {label}:{" "}
        {detected
          ? "Detected"
          : "Missing"}
      </span>
    </div>
  );
}

export default function PPE() {
  const today =
    new Date()
      .toISOString()
      .split("T")[0];

  const [selectedDate, setSelectedDate] =
    useState(today);

  const [workerId, setWorkerId] =
    useState("");

  const [statusFilter, setStatusFilter] =
    useState("");

  const [filterOpen, setFilterOpen] =
    useState(false);

  const {
    records,
    loading,
    error,
    loadPPEResults,
  } = usePPE({
    date: selectedDate,
    workerId,
  });

  const { workers } =
    useWorkers();

  const normalizedRecords =
    useMemo(
      () =>
        records.map(
          (record) => {
            const workerId = record?.worker_id;
            const worker = workers.find(
              (item) =>
                (item.worker_id ?? item.id) ===
                workerId
            );

            return normalizePPERecord(
              record,
              worker?.name ??
                worker?.worker_name
            );
          }
        ),
      [records, workers]
    );

  /*
   * Status filtering is only UI filtering.
   *
   * We are NOT calculating a new compliance
   * status. The backend already gives us the
   * official Phase 7 status.
   */
  const displayedRecords =
    useMemo(() => {
      if (!statusFilter) {
        return normalizedRecords;
      }

      return normalizedRecords.filter(
        (record) =>
          record.status === statusFilter
      );
    }, [
      normalizedRecords,
      statusFilter,
    ]);

  const handleDateChange = async (
    event
  ) => {
    const value =
      event.target.value;

    setSelectedDate(value);

    await loadPPEResults({
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

    await loadPPEResults({
      requestedDate: selectedDate,
      requestedWorkerId: value,
    });
  };

  const handleClearFilters =
    async () => {
      setWorkerId("");
      setStatusFilter("");

      await loadPPEResults({
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
            PPE Compliance
          </h1>

          <p className="text-sm text-gray-500 mt-1">
            Review PPE compliance intervals recorded
            by the monitoring system.
          </p>
        </div>

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
          Filters
        </button>
      </div>

      {/* Filter panel */}
      {filterOpen && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Worker */}
            <div>
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

            {/* Status */}
            <div>
              <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
                Compliance Status
              </label>

              <select
                value={statusFilter}
                onChange={(event) =>
                  setStatusFilter(
                    event.target.value
                  )
                }
                className="w-full px-3 py-2.5 border border-gray-200 rounded-lg text-sm bg-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              >
                <option value="">
                  All statuses
                </option>

                <option
                  value={
                    PPE_STATUS.FULL_PPE
                  }
                >
                  FULL PPE
                </option>

                <option
                  value={
                    PPE_STATUS.HELMET_MISSING
                  }
                >
                  Helmet Missing
                </option>

                <option
                  value={
                    PPE_STATUS.VEST_MISSING
                  }
                >
                  Vest Missing
                </option>

                <option
                  value={
                    PPE_STATUS.NO_PPE
                  }
                >
                  No PPE
                </option>
              </select>
            </div>

            {/* Clear */}
            <div className="flex items-end">
              <button
                type="button"
                onClick={
                  handleClearFilters
                }
                className="w-full md:w-auto inline-flex items-center justify-center px-4 py-2.5 bg-gray-100 hover:bg-gray-200 text-gray-700 text-sm font-medium rounded-lg"
              >
                <X className="h-4 w-4 mr-1.5" />
                Clear Filters
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Main results card */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        {/* Date toolbar */}
        <div className="p-4 border-b border-gray-100 bg-gray-50/50 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
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

        {/* API error */}
        {error && (
          <div className="m-4 bg-red-50 border border-red-200 rounded-xl p-4 flex items-center justify-between gap-3 text-sm text-red-700">
            <div className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5 flex-shrink-0" />

              <span>
                {error.message ||
                  "Failed to load PPE results."}
              </span>
            </div>

            <button
              type="button"
              onClick={() =>
                loadPPEResults({
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
                  Worker
                </th>

                <th className="px-6 py-4 font-semibold">
                  PPE
                </th>

                <th className="px-6 py-4 font-semibold">
                  Status
                </th>

                <th className="px-6 py-4 font-semibold">
                  Start
                </th>

                <th className="px-6 py-4 font-semibold">
                  End
                </th>

                <th className="px-6 py-4 font-semibold">
                  Video
                </th>
              </tr>
            </thead>

            <tbody className="divide-y divide-gray-100 text-sm">
              {loading ? (
                <tr>
                  <td
                    colSpan="6"
                    className="px-6 py-10 text-center text-gray-500"
                  >
                    <div className="inline-flex items-center gap-2">
                      <RefreshCw className="h-4 w-4 animate-spin" />
                      Loading PPE results...
                    </div>
                  </td>
                </tr>
              ) : displayedRecords.length ===
                0 ? (
                <tr>
                  <td
                    colSpan="6"
                    className="px-6 py-12 text-center"
                  >
                    <ShieldAlert className="h-10 w-10 text-gray-300 mx-auto mb-3" />

                    <p className="font-medium text-gray-700">
                      No PPE records found
                    </p>

                    <p className="text-sm text-gray-400 mt-1">
                      There are no compliance
                      intervals matching the
                      selected filters.
                    </p>
                  </td>
                </tr>
              ) : (
                displayedRecords.map(
                  (record) => (
                    <tr
                      key={record.id}
                      className="hover:bg-gray-50 transition-colors"
                    >
                      {/* Worker */}
                      <td className="px-6 py-4">
                        <div>
                          <p className="font-medium text-gray-900">
                            {
                              record.workerName
                            }
                          </p>

                          <p className="text-xs text-gray-400 mt-0.5">
                            {record.workerId ||
                              "—"}
                          </p>
                        </div>
                      </td>

                      {/* PPE */}
                      <td className="px-6 py-4">
                        <div className="space-y-2">
                          <PPEIndicator
                            detected={
                              record.helmetDetected
                            }
                            icon={HardHat}
                            label="Helmet"
                          />

                          <PPEIndicator
                            detected={
                              record.vestDetected
                            }
                            icon={Shirt}
                            label="Vest"
                          />
                        </div>
                      </td>

                      {/* Status */}
                      <td className="px-6 py-4">
                        <StatusBadge
                          status={
                            record.status
                          }
                        />
                      </td>

                      {/* Start */}
                      <td className="px-6 py-4 text-gray-600 font-mono">
                        {formatVideoTimestamp(
                          record.startTimestamp
                        )}
                      </td>

                      {/* End */}
                      <td className="px-6 py-4 text-gray-600 font-mono">
                        {formatVideoTimestamp(
                          record.endTimestamp
                        )}
                      </td>

                      {/* Video */}
                      <td className="px-6 py-4">
                        <span className="text-xs text-gray-400 font-mono">
                          {record.videoId ||
                            "—"}
                        </span>
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