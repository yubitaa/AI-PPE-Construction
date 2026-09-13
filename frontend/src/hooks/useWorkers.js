// src/hooks/useWorkers.js

import { useCallback, useEffect, useState } from "react";

import {
    createWorker,
    deleteWorker,
    getWorker,
    getWorkers,
    updateWorker,
} from "../api/workersApi";

export function useWorkers() {
    const [workers, setWorkers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [deleting, setDeleting] = useState(false);
    const [error, setError] = useState(null);

    const loadWorkers = useCallback(async () => {
        setLoading(true);
        setError(null);

        try {
            const data = await getWorkers();

            setWorkers(
                Array.isArray(data) ? data : []
            );
        } catch (err) {
            setError(err);
            setWorkers([]);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        loadWorkers();
    }, [loadWorkers]);

    const create = useCallback(
        async (workerData) => {
            setSaving(true);
            setError(null);

            try {
                const result =
                    await createWorker(workerData);

                /*
                 * Reload from backend so the UI always reflects
                 * the actual server state.
                 */
                await loadWorkers();

                return result;
            } catch (err) {
                setError(err);
                throw err;
            } finally {
                setSaving(false);
            }
        },
        [loadWorkers]
    );

    const update = useCallback(
        async (workerId, workerData) => {
            setSaving(true);
            setError(null);

            try {
                const result = await updateWorker(
                    workerId,
                    workerData
                );

                await loadWorkers();

                return result;
            } catch (err) {
                setError(err);
                throw err;
            } finally {
                setSaving(false);
            }
        },
        [loadWorkers]
    );

    const remove = useCallback(
        async (workerId) => {
            setDeleting(true);
            setError(null);

            try {
                const result =
                    await deleteWorker(workerId);

                await loadWorkers();

                return result;
            } catch (err) {
                setError(err);
                throw err;
            } finally {
                setDeleting(false);
            }
        },
        [loadWorkers]
    );

    const getDetails = useCallback(
        async (workerId) => {
            try {
                return await getWorker(workerId);
            } catch (err) {
                setError(err);
                throw err;
            }
        },
        []
    );

    return {
        workers,
        loading,
        saving,
        deleting,
        error,

        loadWorkers,
        create,
        update,
        remove,
        getDetails,
    };
}