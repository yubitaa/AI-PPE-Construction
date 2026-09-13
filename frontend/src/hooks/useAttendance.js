// src/hooks/useAttendance.js

import {
    useCallback,
    useEffect,
    useState,
} from "react";

import { getAttendance } from "../api/attendanceApi";

export function useAttendance({
    date,
    workerId = "",
} = {}) {
    const [records, setRecords] = useState([]);
    const [loading, setLoading] =
        useState(true);
    const [error, setError] =
        useState(null);

    const loadAttendance = useCallback(
        async ({
            requestedDate = date,
            requestedWorkerId = workerId,
        } = {}) => {
            setLoading(true);
            setError(null);

            try {
                const data = await getAttendance({
                    date: requestedDate,
                    worker_id: requestedWorkerId || undefined,
                });

                setRecords(
                    Array.isArray(data)
                        ? data
                        : []
                );
            } catch (err) {
                setRecords([]);
                setError(err);
            } finally {
                setLoading(false);
            }
        },
        [date, workerId]
    );

    useEffect(() => {
        loadAttendance();
    }, [loadAttendance]);

    return {
        records,
        loading,
        error,
        loadAttendance,
    };
}