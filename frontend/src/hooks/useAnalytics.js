// src/hooks/useAnalytics.js

import {
    useCallback,
    useEffect,
    useState,
} from "react";

import { getDailyAnalytics } from "../api/analyticsApi";

export function useAnalytics(targetDate) {
    const [analytics, setAnalytics] =
        useState(null);

    const [loading, setLoading] =
        useState(true);

    const [error, setError] =
        useState(null);

    const loadAnalytics = useCallback(
        async (requestedDate = targetDate) => {
            if (!requestedDate) {
                return;
            }

            setLoading(true);
            setError(null);

            try {
                const data =
                    await getDailyAnalytics(
                        requestedDate
                    );

                setAnalytics(data);
            } catch (err) {
                setAnalytics(null);
                setError(err);
            } finally {
                setLoading(false);
            }
        },
        [targetDate]
    );

    useEffect(() => {
        loadAnalytics();
    }, [loadAnalytics]);

    return {
        analytics,
        loading,
        error,
        loadAnalytics,
    };
}