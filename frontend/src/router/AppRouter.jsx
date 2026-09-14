// src/router/AppRouter.jsx

import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

// Layouts
import AdminLayout from "../layouts/AdminLayout";
import UserLayout from "../layouts/UserLayout";

// Admin pages
import Dashboard from "../pages/admin/Dashboard";
import Workers from "../pages/admin/Workers";
import Attendance from "../pages/admin/Attendance";
import PPE from "../pages/admin/PPE";
import Reports from "../pages/admin/Reports";

// User pages
import ClockIn from "../pages/user/ClockIn";
import PPEMonitoring from "../pages/user/PPEMonitoring";

export default function AppRouter() {
    return (
        <BrowserRouter>
            <Routes>
                {/* =========================
            ADMIN ROUTES
           ========================= */}
                <Route path="/" element={<AdminLayout />}>
                    <Route index element={<Navigate to="/dashboard" replace />} />

                    <Route path="dashboard" element={<Dashboard />} />
                    <Route path="workers" element={<Workers />} />
                    <Route path="attendance" element={<Attendance />} />
                    <Route path="ppe" element={<PPE />} />
                    <Route path="reports" element={<Reports />} />
                </Route>

                {/* =========================
            USER ROUTES
           ========================= */}
                <Route path="/user" element={<UserLayout />}>
                    <Route index element={<Navigate to="/user/clock-in" replace />} />

                    <Route path="clock-in" element={<ClockIn />} />
                    <Route path="ppe-monitoring" element={<PPEMonitoring />} />
                </Route>

                {/* =========================
            404
           ========================= */}
                <Route
                    path="*"
                    element={<Navigate to="/dashboard" replace />}
                />
            </Routes>
        </BrowserRouter>
    );
}