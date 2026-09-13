// src/hooks/useCamera.js

import { useRef, useState, useCallback, useEffect } from "react";

/**
 * useCamera
 *
 * Manages access to the device camera via navigator.mediaDevices.getUserMedia.
 *
 * Usage:
 *   const { videoRef, status, startCamera, stopCamera, captureFrame } = useCamera();
 *
 * Then attach `videoRef` to a <video> element:
 *   <video ref={videoRef} autoPlay playsInline muted />
 *
 * Status values:
 *   'idle'        - Camera not started yet
 *   'requesting'  - Waiting for user to grant permission
 *   'active'      - Camera is streaming
 *   'denied'      - User denied camera permission
 *   'unavailable' - Device has no camera or browser doesn't support it
 *   'error'       - Unexpected error
 */
export function useCamera({ facingMode = "user" } = {}) {
    const videoRef = useRef(null);
    const streamRef = useRef(null);

    const [status, setStatus] = useState("idle");
    const [errorMessage, setErrorMessage] = useState(null);

    // ── Start Camera ─────────────────────────────────────────────────────────
    const startCamera = useCallback(async () => {
        if (!navigator.mediaDevices?.getUserMedia) {
            setStatus("unavailable");
            setErrorMessage("Your browser or device does not support camera access.");
            return;
        }

        setStatus("requesting");
        setErrorMessage(null);

        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode },
                audio: false,
            });

            streamRef.current = stream;

            if (videoRef.current) {
                videoRef.current.srcObject = stream;
            }

            setStatus("active");
        } catch (err) {
            if (err.name === "NotAllowedError" || err.name === "PermissionDeniedError") {
                setStatus("denied");
                setErrorMessage("Camera permission was denied. Please allow camera access in your browser settings.");
            } else if (err.name === "NotFoundError" || err.name === "DevicesNotFoundError") {
                setStatus("unavailable");
                setErrorMessage("No camera found on this device.");
            } else {
                setStatus("error");
                setErrorMessage("An unexpected error occurred while accessing the camera.");
            }
        }
    }, [facingMode]);

    // ── Stop Camera ──────────────────────────────────────────────────────────
    const stopCamera = useCallback(() => {
        if (streamRef.current) {
            streamRef.current.getTracks().forEach(track => track.stop());
            streamRef.current = null;
        }
        if (videoRef.current) {
            videoRef.current.srcObject = null;
        }
        setStatus("idle");
    }, []);

    // ── Capture Frame (returns a Blob) ────────────────────────────────────────
    const captureFrame = useCallback(() => {
        return new Promise((resolve, reject) => {
            const video = videoRef.current;

            if (!video || status !== "active") {
                reject(new Error("Camera is not active."));
                return;
            }

            const canvas = document.createElement("canvas");
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;

            const ctx = canvas.getContext("2d");
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

            canvas.toBlob(
                (blob) => {
                    if (blob) {
                        resolve(blob);
                    } else {
                        reject(new Error("Failed to capture frame from camera."));
                    }
                },
                "image/jpeg",
                0.92
            );
        });
    }, [status]);

    // ── Cleanup on unmount ───────────────────────────────────────────────────
    useEffect(() => {
        return () => {
            if (streamRef.current) {
                streamRef.current.getTracks().forEach(track => track.stop());
            }
        };
    }, []);

    return {
        videoRef,
        status,
        errorMessage,
        startCamera,
        stopCamera,
        captureFrame,
        isActive: status === "active",
    };
}
