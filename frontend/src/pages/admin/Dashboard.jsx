// src/pages/admin/Dashboard.jsx

import { useMemo, useState } from "react";

import {
  Users,
  ShieldCheck,
  ShieldAlert,
  AlertTriangle,
  Calendar,
  RefreshCw,
  AlertCircle,
} from "lucide-react";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

import { useAnalytics } from "../../hooks/useAnalytics";

function getToday() {
  return new Date()
    .toISOString()
    .split("T")[0];
}

function normalizeAnalytics(data) {
  const attendance =
    data?.attendance_summary ??
    data?.attendanceSummary ??
    {};

  const ppe =
    data?.ppe_summary ??
    data?.ppeSummary ??
    {};

  const breakdown =
    ppe.violations_breakdown ??
    ppe.violationsBreakdown ??
    {};

  return {
    totalPresent:
      attendance.total_present ??
      attendance.totalPresent ??
      data?.total_present ??
      data?.totalPresent ??
      0,

    totalWorkers:
      attendance.total_workers ??
      attendance.totalWorkers ??
      data?.total_workers ??
      data?.totalWorkers ??
      null,

    totalPPEEvents:
      ppe.total_ppe_events ??
      ppe.totalPpeEvents ??
      ppe.total_events ??
      data?.total_ppe_events ??
      data?.totalPpeEvents ??
      0,

    fullPPE:
      breakdown.full_ppe ??
      breakdown.fullPpe ??
      breakdown.FULL_PPE ??
      ppe.full_ppe ??
      ppe.fullPpe ??
      ppe.FULL_PPE ??
      0,

    helmetMissing:
      breakdown.helmet_missing ??
      breakdown.helmetMissing ??
      breakdown.HELMET_MISSING ??
      ppe.helmet_missing ??
      ppe.helmetMissing ??
      ppe.HELMET_MISSING ??
      0,

    vestMissing:
      breakdown.vest_missing ??
      breakdown.vestMissing ??
      breakdown.VEST_MISSING ??
      ppe.vest_missing ??
      ppe.vestMissing ??
      ppe.VEST_MISSING ??
      0,

    noPPE:
      breakdown.no_ppe ??
      breakdown.noPpe ??
      breakdown.NO_PPE ??
      ppe.no_ppe ??
      ppe.noPpe ??
      ppe.NO_PPE ??
      0,

    complianceRate:
      data?.compliance_rate ??
      data?.complianceRate ??
      ppe.compliance_rate ??
      ppe.complianceRate ??
      0,

    workerRates:
      data?.worker_compliance_rates ??
      data?.workerComplianceRates ??
      data?.worker_rates ??
      data?.workerRates ??
      [],
  };
}

function StatCard({
  title,
  value,
  icon,
  suffix = "",
}) {
  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 transition-transform hover:-translate-y-1 hover:shadow-md">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-gray-500">
          {title}
        </h3>

        <div className="p-2 bg-gray-50 rounded-lg">
          {icon}
        </div>
      </div>

      <div className="text-3xl font-bold text-gray-900">
        {value}
        {suffix}
      </div>
    </div>
  );
}

export default function Dashboard() {
  const [selectedDate, setSelectedDate] =
    useState(getToday());

  const {
    analytics,
    loading,
    error,
    loadAnalytics,
  } = useAnalytics(selectedDate);

  const normalized =
    useMemo(
      () =>
        normalizeAnalytics(
          analytics
        ),
      [analytics]
    );

  const chartData = useMemo(
    () => [
      {
        status: "Full PPE",
        count: normalized.fullPPE,
      },
      {
        status: "Helmet Missing",
        count:
          normalized.helmetMissing,
      },
      {
        status: "Vest Missing",
        count:
          normalized.vestMissing,
      },
      {
        status: "No PPE",
        count: normalized.noPPE,
      },
    ],
    [normalized]
  );

  const totalViolations =
    normalized.helmetMissing +
    normalized.vestMissing +
    normalized.noPPE;

  const handleDateChange = async (
    event
  ) => {
    const value =
      event.target.value;

    setSelectedDate(value);

    await loadAnalytics(value);
  };

  const handleRefresh = async () => {
    await loadAnalytics(selectedDate);
  };

  if (loading && !analytics) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="flex items-center gap-2 text-gray-500">
          <RefreshCw className="h-5 w-5 animate-spin" />
          Loading daily analytics...
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Dashboard Overview
          </h1>

          <p className="text-sm text-gray-500 mt-1">
            Daily attendance and PPE analytics.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Calendar className="h-4 w-4 text-gray-400" />

          <input
            type="date"
            value={selectedDate}
            onChange={handleDateChange}
            className="px-3 py-2 border border-gray-200 rounded-lg text-sm text-gray-700 bg-white outline-none focus:ring-2 focus:ring-blue-500"
          />

          <button
            type="button"
            onClick={handleRefresh}
            disabled={loading}
            className="p-2 border border-gray-200 rounded-lg bg-white hover:bg-gray-50 disabled:opacity-50"
            title="Refresh analytics"
          >
            <RefreshCw
              className={`h-4 w-4 text-gray-500 ${loading
                  ? "animate-spin"
                  : ""
                }`}
            />
          </button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex items-center justify-between gap-3 text-sm text-red-700">
          <div className="flex items-center gap-2">
            <AlertCircle className="h-5 w-5 flex-shrink-0" />

            <span>
              {error.message ||
                "Failed to load daily analytics."}
            </span>
          </div>

          <button
            type="button"
            onClick={handleRefresh}
            className="font-semibold underline"
          >
            Retry
          </button>
        </div>
      )}

      {/* Top Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Present Today"
          value={normalized.totalPresent}
          icon={
            <Users className="h-6 w-6 text-blue-500" />
          }
        />

        <StatCard
          title="Total PPE Events"
          value={
            normalized.totalPPEEvents
          }
          icon={
            <ShieldCheck className="h-6 w-6 text-green-500" />
          }
        />

        <StatCard
          title="PPE Compliance"
          value={
            Number(normalized.complianceRate).toFixed(2)
          }
          suffix="%"
          icon={
            <ShieldAlert className="h-6 w-6 text-indigo-500" />
          }
        />

        <StatCard
          title="PPE Violations"
          value={totalViolations}
          icon={
            <AlertTriangle className="h-6 w-6 text-red-500" />
          }
        />
      </div>

      {/* PPE Breakdown */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-lg font-semibold text-gray-800">
              PPE Compliance Breakdown
            </h2>

            <p className="text-xs text-gray-400 mt-1">
              {selectedDate}
            </p>
          </div>
        </div>

        <div className="h-80 w-full">
          <ResponsiveContainer
            width="100%"
            height="100%"
          >
            <BarChart
              data={chartData}
              margin={{
                top: 10,
                right: 20,
                left: 0,
                bottom: 0,
              }}
            >
              <CartesianGrid
                strokeDasharray="3 3"
                vertical={false}
                stroke="#f3f4f6"
              />

              <XAxis
                dataKey="status"
                axisLine={false}
                tickLine={false}
                tick={{
                  fill: "#9ca3af",
                  fontSize: 12,
                }}
              />

              <YAxis
                axisLine={false}
                tickLine={false}
                tick={{
                  fill: "#9ca3af",
                  fontSize: 12,
                }}
                allowDecimals={false}
              />

              <Tooltip />

              <Bar
                dataKey="count"
                fill="#4f46e5"
                radius={[
                  6,
                  6,
                  0,
                  0,
                ]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Worker compliance */}
      {normalized.workerRates.length >
        0 && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
            <div className="p-6 border-b border-gray-100">
              <h2 className="text-lg font-semibold text-gray-800">
                Worker Compliance Rates
              </h2>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="bg-gray-50 text-gray-500 text-xs uppercase tracking-wider">
                    <th className="px-6 py-4">
                      Worker
                    </th>

                    <th className="px-6 py-4">
                      Compliance
                    </th>
                  </tr>
                </thead>

                <tbody className="divide-y divide-gray-100">
                  {normalized.workerRates.map(
                    (worker, index) => {
                      const name =
                        worker?.worker_name ??
                        worker?.workerName ??
                        worker?.name ??
                        `Worker ${index + 1}`;

                      const rate =
                        worker?.compliance_rate ??
                        worker?.complianceRate ??
                        0;

                      return (
                        <tr
                          key={
                            worker?.worker_id ??
                            worker?.workerId ??
                            index
                          }
                          className="hover:bg-gray-50"
                        >
                          <td className="px-6 py-4 text-sm font-medium text-gray-900">
                            {name}
                          </td>

                          <td className="px-6 py-4">
                            <div className="flex items-center gap-3">
                              <div className="w-32 bg-gray-200 rounded-full h-2">
                                <div
                                  className="h-2 rounded-full bg-indigo-500"
                                  style={{
                                    width: `${Math.max(
                                      0,
                                      Math.min(
                                        100,
                                        Number(rate)
                                      )
                                    )}%`,
                                  }}
                                />
                              </div>

                              <span className="text-sm text-gray-600">
                                {rate}%
                              </span>
                            </div>
                          </td>
                        </tr>
                      );
                    }
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}
    </div>
  );
}