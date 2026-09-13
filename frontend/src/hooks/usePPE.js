// src/hooks/usePPE.js

import {
    useCallback,
    useEffect,
    useState,
} from "react";

import {
    getPPEResults,
} from "../api/ppeApi";

export const PPE_STATUSES = {
    FULL_PPE: "FULL_PPE",
    HELMET_MISSING: "HELMET_MISSING",
    VEST_MISSING: "VEST_MISSING",
    NO_PPE: "NO_PPE",
};

export function usePPE({
    date,
    workerId = "",
} = {}) {
    const [records, setRecords] = useState([]);
    const [loading, setLoading] =
        useState(true);
    const [error, setError] =
        useState(null);

    const loadPPEResults = useCallback(
        async ({
            requestedDate = date,
            requestedWorkerId = workerId,
        } = {}) => {
            setLoading(true);
            setError(null);

            try {
                const data = await getPPEResults({
                    date: requestedDate,
                    worker_id:
                        requestedWorkerId || undefined,
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
        loadPPEResults();
    }, [loadPPEResults]);

    return {
        records,
        loading,
        error,
        loadPPEResults,
    };
}