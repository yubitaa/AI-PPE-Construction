// // src/pages/user/ClockIn.jsx

// import { useState, useEffect } from 'react';
// import { useCamera } from '../../hooks/useCamera';
// import { recognizeCameraFrame } from '../../api/clockinApi';
// import {
//     Camera,
//     CheckCircle,
//     XCircle,
//     Loader2,
//     AlertTriangle,
//     VideoOff,
//     RefreshCw,
// } from 'lucide-react';

// // ── Status overlay components ─────────────────────────────────────────────────

// function SuccessOverlay({ result, onReset }) {
//     return (
//         <div className="absolute inset-0 bg-green-500/95 backdrop-blur-sm flex flex-col items-center justify-center text-white p-6 text-center">
//             <CheckCircle className="h-20 w-20 mb-4 drop-shadow-lg" />
//             <h2 className="text-2xl font-bold mb-1">Welcome, {result.workerName}!</h2>
//             <p className="text-white/80 text-sm mb-6">Clocked in at {result.timestamp}</p>


//             <button
//                 onClick={onReset}
//                 className="px-6 py-2.5 bg-white text-green-600 rounded-full font-bold shadow-lg hover:scale-105 transition-transform"
//             >
//                 Done
//             </button>
//         </div>
//     );
// }

// function ErrorOverlay({ message, onRetry }) {
//     return (
//         <div className="absolute inset-0 bg-red-500/95 backdrop-blur-sm flex flex-col items-center justify-center text-white p-6 text-center">
//             <XCircle className="h-20 w-20 mb-4 drop-shadow-lg" />
//             <h2 className="text-2xl font-bold mb-2">Scan Failed</h2>
//             <p className="text-white/80 text-sm mb-6">{message}</p>
//             <button
//                 onClick={onRetry}
//                 className="px-6 py-2.5 bg-white text-red-600 rounded-full font-bold shadow-lg hover:scale-105 transition-transform flex items-center gap-2"
//             >
//                 <RefreshCw className="h-4 w-4" />
//                 Try Again
//             </button>
//         </div>
//     );
// }

// function CameraPermissionScreen({ status, errorMessage, onStart }) {
//     return (
//         <div className="flex-1 flex flex-col items-center justify-center py-12 px-4 text-center space-y-4">
//             {status === 'denied' || status === 'unavailable' || status === 'error' ? (
//                 <>
//                     <div className="p-4 bg-red-100 rounded-full">
//                         <VideoOff className="h-10 w-10 text-red-500" />
//                     </div>
//                     <h2 className="text-lg font-bold text-slate-800">Camera Unavailable</h2>
//                     <p className="text-sm text-slate-500 max-w-xs">{errorMessage}</p>
//                     <button
//                         onClick={onStart}
//                         className="px-5 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors"
//                     >
//                         Try Again
//                     </button>
//                 </>
//             ) : (
//                 <>
//                     <div className="p-5 bg-blue-100 rounded-full">
//                         <Camera className="h-12 w-12 text-blue-500" />
//                     </div>
//                     <h2 className="text-xl font-bold text-slate-900">Ready to Clock In</h2>
//                     <p className="text-sm text-slate-500 max-w-xs">
//                         Tap below to activate your camera. Make sure your face is clearly visible.
//                     </p>
//                     <button
//                         onClick={onStart}
//                         className="w-full max-w-xs py-4 bg-blue-600 hover:bg-blue-500 active:scale-95 text-white font-bold text-lg rounded-2xl shadow-xl transition-all"
//                     >
//                         Activate Camera
//                     </button>
//                 </>
//             )}
//         </div>
//     );
// }

// // ── Main Component ────────────────────────────────────────────────────────────

// export default function ClockIn() {
//     const { videoRef, status, errorMessage, startCamera, stopCamera, captureFrame, isActive } = useCamera({ facingMode: 'user' });
//     const [processing, setProcessing] = useState(false);
//     const [result, setResult] = useState(null); // { type: 'success' | 'error', ... }

//     // Auto-start camera when component mounts
//     useEffect(() => {
//         startCamera();
//         return () => stopCamera();
//     }, []);

//     const handleScan = async () => {
//         setProcessing(true);
//         setResult(null);
//         try {
//             const frameBlob = await captureFrame();
//             const response = await recognizeCameraFrame(frameBlob);
//             setResult({ type: 'success', ...response });
//         } catch (err) {
//             setResult({ type: 'error', message: err.message || 'Recognition failed. Please try again.' });
//         } finally {
//             setProcessing(false);
//         }
//     };

//     const handleReset = () => {
//         setResult(null);
//     };

//     // Show permission/error screen if camera isn't active and we haven't got a result
//     if (!isActive && status !== 'requesting' && !result) {
//         return (
//             <div className="flex-1 flex flex-col">
//                 <div className="text-center pt-6 space-y-1">
//                     <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Clock In</h1>
//                     <p className="text-slate-500 text-sm">Verify your identity and PPE with your camera.</p>
//                 </div>
//                 <CameraPermissionScreen status={status} errorMessage={errorMessage} onStart={startCamera} />
//             </div>
//         );
//     }

//     return (
//         <div className="flex-1 flex flex-col items-center justify-start pt-6 space-y-6">

//             {/* Title */}
//             <div className="text-center space-y-1 w-full">
//                 <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Clock In</h1>
//                 <p className="text-slate-500 text-sm">Look at the camera. Make sure your face is clearly visible.</p>
//             </div>

//             {/* Camera Viewport */}
//             <div className="w-full max-w-sm aspect-[3/4] bg-slate-900 rounded-3xl overflow-hidden shadow-2xl relative border-4 border-slate-800">

//                 {/* Live video feed */}
//                 <video
//                     ref={videoRef}
//                     autoPlay
//                     playsInline
//                     muted
//                     className="w-full h-full object-cover"
//                 />

//                 {/* Requesting indicator */}
//                 {status === 'requesting' && (
//                     <div className="absolute inset-0 bg-slate-900/80 flex flex-col items-center justify-center text-white space-y-3">
//                         <Loader2 className="h-10 w-10 animate-spin text-blue-400" />
//                         <p className="text-sm font-medium">Requesting camera access...</p>
//                     </div>
//                 )}

//                 {/* Scanning overlay */}
//                 {processing && (
//                     <div className="absolute inset-0 bg-black/60 backdrop-blur-[2px] flex flex-col items-center justify-center text-white space-y-3">
//                         {/* Animated scan line */}
//                         <div className="relative w-40 h-40 border-2 border-blue-400 rounded-lg">
//                             <div className="absolute top-0 left-0 right-0 h-0.5 bg-blue-400 animate-[scanline_1.5s_ease-in-out_infinite]" />
//                         </div>
//                         <p className="font-medium animate-pulse text-blue-300 text-sm">Recognizing face...</p>
//                     </div>
//                 )}

//                 {/* LIVE badge */}
//                 {isActive && !processing && !result && (
//                     <div className="absolute top-3 left-3 flex items-center space-x-1.5 bg-black/50 rounded-full px-2.5 py-1 backdrop-blur-md">
//                         <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
//                         <span className="text-[10px] text-white font-bold tracking-wider uppercase">Live</span>
//                     </div>
//                 )}

//                 {/* Face guide overlay */}
//                 {isActive && !processing && !result && (
//                     <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
//                         <div className="w-40 h-52 border-2 border-white/30 rounded-[40%] shadow-inner" />
//                     </div>
//                 )}

//                 {/* Result overlays */}
//                 {result?.type === 'success' && (
//                     <SuccessOverlay result={result} onReset={handleReset} />
//                 )}
//                 {result?.type === 'error' && (
//                     <ErrorOverlay message={result.message} onRetry={handleReset} />
//                 )}
//             </div>

//             {/* Capture button */}
//             {isActive && !result && (
//                 <button
//                     onClick={handleScan}
//                     disabled={processing}
//                     className={`w-full max-w-sm py-4 rounded-2xl font-bold text-lg text-white shadow-xl transition-all duration-200 ${
//                         processing
//                             ? 'bg-blue-400 cursor-not-allowed scale-95'
//                             : 'bg-blue-600 hover:bg-blue-500 active:scale-95'
//                     }`}
//                 >
//                     {processing ? 'Processing...' : 'Capture & Clock In'}
//                 </button>
//             )}

//             {/* Warning hint */}
//             {isActive && !result && !processing && (
//                 <p className="text-xs text-slate-400 flex items-center gap-1.5 text-center">
//                     <AlertTriangle className="h-3.5 w-3.5 flex-shrink-0" />
//                     Look straight at the camera for face recognition
//                 </p>
//             )}

//         </div>
//     );
// }
// src/pages/user/ClockIn.jsx
// src/pages/user/ClockIn.jsx

import { useEffect, useState } from "react";
import { useCamera } from "../../hooks/useCamera";
import { recognizeCameraFrame, uploadClockInVideo } from "../../api/clockinApi";

import {
    Camera,
    CheckCircle,
    XCircle,
    Loader2,
    AlertTriangle,
    VideoOff,
    RefreshCw,
    UploadCloud,
    FileVideo,
    X,
} from "lucide-react";

// -----------------------------------------------------------------------------
// Helpers
// -----------------------------------------------------------------------------

function normalizeClockInResult(response) {
    const status = String(
        response?.status ||
        response?.result ||
        response?.attendance_status ||
        ""
    ).toUpperCase();

    return {
        ...response,
        status,
        workerName:
            response?.workerName ??
            response?.worker_name ??
            response?.name ??
            null,
        workerId:
            response?.workerId ??
            response?.worker_id ??
            null,
        timestamp:
            response?.timestamp ??
            response?.clock_in_time ??
            response?.clocked_in_at ??
            null,
        message:
            response?.message ??
            response?.detail ??
            null,
    };
}

function getResultType(result) {
    if (!result) {
        return null;
    }

    if (result.status === "CLOCKED_IN") {
        return "success";
    }

    return "error";
}

// -----------------------------------------------------------------------------
// Camera result overlays
// -----------------------------------------------------------------------------

function SuccessOverlay({ result, onReset }) {
    const isAlreadyClockedIn =
        result.status === "ALREADY_CLOCKED_IN";

    return (
        <div
            className={`absolute inset-0 backdrop-blur-sm flex flex-col items-center justify-center text-white p-6 text-center ${isAlreadyClockedIn
                    ? "bg-blue-500/95"
                    : "bg-green-500/95"
                }`}
        >
            <CheckCircle className="h-20 w-20 mb-4 drop-shadow-lg" />

            <h2 className="text-2xl font-bold mb-1">
                {isAlreadyClockedIn
                    ? `Welcome back${result.workerName ? `, ${result.workerName}` : ""}!`
                    : `Welcome${result.workerName ? `, ${result.workerName}` : ""}!`}
            </h2>

            <p className="text-white/80 text-sm mb-2">
                {isAlreadyClockedIn
                    ? "You are already clocked in."
                    : "Clock-in successful."}
            </p>

            {result.timestamp && (
                <p className="text-white/70 text-sm mb-6">
                    {isAlreadyClockedIn
                        ? `Recorded at ${result.timestamp}`
                        : `Clocked in at ${result.timestamp}`}
                </p>
            )}

            {!result.timestamp && <div className="mb-6" />}

            <button
                type="button"
                onClick={onReset}
                className={`px-6 py-2.5 bg-white rounded-full font-bold shadow-lg hover:scale-105 transition-transform ${isAlreadyClockedIn
                        ? "text-blue-600"
                        : "text-green-600"
                    }`}
            >
                Done
            </button>
        </div>
    );
}

function ErrorOverlay({ result, onRetry }) {
    const title =
        result.status === "UNKNOWN"
            ? "Worker Not Recognized"
            : "Clock-in Failed";

    const message =
        result.message ||
        (result.status === "UNKNOWN"
            ? "The system could not identify the worker. Please try again."
            : "Recognition failed. Please try again.");

    return (
        <div className="absolute inset-0 bg-red-500/95 backdrop-blur-sm flex flex-col items-center justify-center text-white p-6 text-center">
            <XCircle className="h-20 w-20 mb-4 drop-shadow-lg" />

            <h2 className="text-2xl font-bold mb-2">
                {title}
            </h2>

            <p className="text-white/80 text-sm mb-6 max-w-xs">
                {message}
            </p>

            <button
                type="button"
                onClick={onRetry}
                className="px-6 py-2.5 bg-white text-red-600 rounded-full font-bold shadow-lg hover:scale-105 transition-transform flex items-center gap-2"
            >
                <RefreshCw className="h-4 w-4" />
                Try Again
            </button>
        </div>
    );
}

// -----------------------------------------------------------------------------
// Camera permission screen
// -----------------------------------------------------------------------------

function CameraPermissionScreen({
    status,
    errorMessage,
    onStart,
}) {
    const hasError =
        status === "denied" ||
        status === "unavailable" ||
        status === "error";

    return (
        <div className="flex-1 flex flex-col items-center justify-center py-12 px-4 text-center space-y-4">
            {hasError ? (
                <>
                    <div className="p-4 bg-red-100 rounded-full">
                        <VideoOff className="h-10 w-10 text-red-500" />
                    </div>

                    <h2 className="text-lg font-bold text-slate-800">
                        Camera Unavailable
                    </h2>

                    <p className="text-sm text-slate-500 max-w-xs">
                        {errorMessage ||
                            "Camera access could not be started."}
                    </p>

                    <button
                        type="button"
                        onClick={onStart}
                        className="px-5 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors"
                    >
                        Try Again
                    </button>
                </>
            ) : (
                <>
                    <div className="p-5 bg-blue-100 rounded-full">
                        <Camera className="h-12 w-12 text-blue-500" />
                    </div>

                    <h2 className="text-xl font-bold text-slate-900">
                        Ready to Clock In
                    </h2>

                    <p className="text-sm text-slate-500 max-w-xs">
                        Activate the camera and make sure your face is
                        clearly visible.
                    </p>

                    <button
                        type="button"
                        onClick={onStart}
                        className="w-full max-w-xs py-4 bg-blue-600 hover:bg-blue-500 active:scale-95 text-white font-bold text-lg rounded-2xl shadow-xl transition-all"
                    >
                        Activate Camera
                    </button>
                </>
            )}
        </div>
    );
}

// -----------------------------------------------------------------------------
// Upload video
// -----------------------------------------------------------------------------

function UploadVideoSection({
    videoFile,
    onSelect,
    onRemove,
    onProcess,
    progress,
    processing,
    result,
}) {
    const [videoUrl, setVideoUrl] = useState("");

    useEffect(() => {
        if (!videoFile) {
            setVideoUrl("");
            return undefined;
        }

        const url = URL.createObjectURL(videoFile);
        setVideoUrl(url);

        return () => {
            URL.revokeObjectURL(url);
        };
    }, [videoFile]);

    const handleInputChange = (event) => {
        const file = event.target.files?.[0];

        if (file) {
            onSelect(file);
        }

        event.target.value = "";
    };

    return (
        <div className="w-full max-w-sm space-y-5">
            {!videoFile ? (
                <label className="block cursor-pointer">
                    <input
                        type="file"
                        accept="video/*"
                        className="hidden"
                        onChange={handleInputChange}
                    />

                    <div className="border-2 border-dashed border-slate-300 rounded-3xl p-8 text-center hover:border-blue-400 hover:bg-blue-50/40 transition-all">
                        <div className="flex flex-col items-center gap-3">
                            <div className="p-5 bg-blue-100 rounded-full">
                                <UploadCloud className="h-10 w-10 text-blue-500" />
                            </div>

                            <div>
                                <h2 className="text-lg font-bold text-slate-800">
                                    Upload Clock-in Video
                                </h2>

                                <p className="text-sm text-slate-500 mt-1">
                                    Select a video containing the worker's face.
                                </p>
                            </div>

                            <span className="text-xs text-slate-400 bg-white border border-slate-200 px-3 py-1 rounded-full">
                                MP4, MOV, AVI, WEBM
                            </span>
                        </div>
                    </div>
                </label>
            ) : (
                <>
                    {/* Video preview */}
                    <div className="relative bg-slate-900 rounded-3xl overflow-hidden shadow-2xl border-4 border-slate-800">
                        <video
                            src={videoUrl}
                            controls
                            className="w-full aspect-[3/4] object-contain"
                        />

                        {/* File badge */}
                        <div className="absolute top-3 left-3 flex items-center gap-1.5 bg-black/60 rounded-full px-2.5 py-1 backdrop-blur-md max-w-[75%]">
                            <FileVideo className="h-3.5 w-3.5 text-white flex-shrink-0" />

                            <span className="text-[10px] text-white font-bold truncate">
                                {videoFile.name}
                            </span>
                        </div>

                        {!processing && (
                            <button
                                type="button"
                                onClick={onRemove}
                                className="absolute top-3 right-3 p-1.5 bg-black/60 hover:bg-black/80 rounded-full text-white transition-colors"
                                aria-label="Remove video"
                            >
                                <X className="h-4 w-4" />
                            </button>
                        )}

                        {processing && (
                            <div className="absolute inset-0 bg-black/60 backdrop-blur-[2px] flex flex-col items-center justify-center text-white space-y-3">
                                <Loader2 className="h-10 w-10 animate-spin text-blue-400" />

                                <p className="font-medium text-blue-300 text-sm">
                                    Processing clock-in...
                                </p>
                            </div>
                        )}
                    </div>

                    {/* Upload progress */}
                    {processing && (
                        <div className="space-y-2">
                            <div className="flex items-center justify-between text-xs text-slate-500">
                                <span>
                                    {progress < 100
                                        ? "Uploading video..."
                                        : "Processing video..."}
                                </span>

                                <span>{progress}%</span>
                            </div>

                            <div className="w-full h-2 bg-slate-200 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-blue-600 rounded-full transition-all duration-300"
                                    style={{
                                        width: `${progress}%`,
                                    }}
                                />
                            </div>
                        </div>
                    )}

                    {!processing && !result && (
                        <button
                            type="button"
                            onClick={onProcess}
                            className="w-full py-4 bg-blue-600 hover:bg-blue-500 active:scale-95 text-white font-bold text-lg rounded-2xl shadow-xl transition-all"
                        >
                            Upload & Clock In
                        </button>
                    )}
                </>
            )}
        </div>
    );
}

// -----------------------------------------------------------------------------
// Main component
// -----------------------------------------------------------------------------

export default function ClockIn() {
    const {
        videoRef,
        status,
        errorMessage,
        startCamera,
        stopCamera,
        captureFrame,
        isActive,
    } = useCamera({
        facingMode: "user",
    });

    const [mode, setMode] = useState("camera");

    const [processing, setProcessing] = useState(false);
    const [result, setResult] = useState(null);

    const [videoFile, setVideoFile] = useState(null);
    const [uploadProgress, setUploadProgress] = useState(0);

    // ---------------------------------------------------------------------------
    // Camera lifecycle
    // ---------------------------------------------------------------------------

    useEffect(() => {
        if (mode !== "camera") {
            return undefined;
        }

        startCamera();

        return () => {
            stopCamera();
        };
    }, [mode]);

    // ---------------------------------------------------------------------------
    // Camera scan
    // ---------------------------------------------------------------------------

    const handleScan = async () => {
        setProcessing(true);
        setResult(null);

        try {
            const frameBlob = await captureFrame();

            const response =
                await recognizeCameraFrame(frameBlob);

            const normalized =
                normalizeClockInResult(response);

            setResult(normalized);

            /*
             * Stop the camera once the backend has returned
             * an actual final attendance state.
             */
            if (
                [
                    "CLOCKED_IN",
                    "ALREADY_CLOCKED_IN",
                    "UNKNOWN",
                ].includes(normalized.status)
            ) {
                stopCamera();
            }
        } catch (error) {
            setResult({
                status: "ERROR",
                message:
                    error?.message ||
                    "Recognition failed. Please try again.",
            });

            stopCamera();
        } finally {
            setProcessing(false);
        }
    };

    // ---------------------------------------------------------------------------
    // Camera reset
    // ---------------------------------------------------------------------------

    const handleCameraReset = () => {
        setResult(null);

        if (!isActive) {
            startCamera();
        }
    };

    // ---------------------------------------------------------------------------
    // Upload video
    // ---------------------------------------------------------------------------

    const handleVideoSelected = (file) => {
        if (!file.type.startsWith("video/")) {
            setResult({
                status: "ERROR",
                message: "Please select a valid video file.",
            });

            setVideoFile(null);
            return;
        }

        setVideoFile(file);
        setUploadProgress(0);
        setResult(null);
    };

    const handleVideoRemove = () => {
        setVideoFile(null);
        setUploadProgress(0);
        setResult(null);
    };

    const handleVideoProcess = async () => {
        if (!videoFile) {
            return;
        }

        setProcessing(true);
        setUploadProgress(0);
        setResult(null);

        try {
            const response = await uploadClockInVideo(
                videoFile,
                setUploadProgress
            );

            const normalized =
                normalizeClockInResult(response);

            setResult(normalized);
        } catch (error) {
            setResult({
                status: "ERROR",
                message:
                    error?.message ||
                    "Video processing failed. Please try again.",
            });
        } finally {
            setProcessing(false);
        }
    };

    // ---------------------------------------------------------------------------
    // Mode change
    // ---------------------------------------------------------------------------

    const handleModeChange = (nextMode) => {
        if (nextMode === mode) {
            return;
        }

        stopCamera();

        setResult(null);
        setProcessing(false);

        if (nextMode === "camera") {
            setVideoFile(null);
            setUploadProgress(0);
        }

        setMode(nextMode);
    };

    // ---------------------------------------------------------------------------
    // Camera permission screen
    // ---------------------------------------------------------------------------

    if (
        mode === "camera" &&
        !isActive &&
        status !== "requesting" &&
        !result
    ) {
        return (
            <div className="flex-1 flex flex-col">
                <div className="text-center pt-6 space-y-1">
                    <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
                        Clock In
                    </h1>

                    <p className="text-slate-500 text-sm">
                        Verify your identity using the camera.
                    </p>
                </div>

                <div className="flex justify-center px-4 mt-5">
                    <div className="w-full max-w-sm grid grid-cols-2 gap-2 p-1 bg-slate-100 rounded-xl">
                        <button
                            type="button"
                            onClick={() => handleModeChange("camera")}
                            className="py-2.5 rounded-lg text-sm font-semibold bg-white text-blue-600 shadow-sm"
                        >
                            Camera
                        </button>

                        <button
                            type="button"
                            onClick={() => handleModeChange("video")}
                            className="py-2.5 rounded-lg text-sm font-semibold text-slate-500"
                        >
                            Upload Video
                        </button>
                    </div>
                </div>

                <CameraPermissionScreen
                    status={status}
                    errorMessage={errorMessage}
                    onStart={startCamera}
                />
            </div>
        );
    }

    // ---------------------------------------------------------------------------
    // Main UI
    // ---------------------------------------------------------------------------

    return (
        <div className="flex-1 flex flex-col items-center justify-start pt-6 space-y-6">
            {/* Title */}
            <div className="text-center space-y-1 w-full">
                <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
                    Clock In
                </h1>

                <p className="text-slate-500 text-sm">
                    {mode === "camera"
                        ? "Look at the camera. Make sure your face is clearly visible."
                        : "Upload a clock-in video containing the worker's face."}
                </p>
            </div>

            {/* Mode selector */}
            <div className="w-full max-w-sm grid grid-cols-2 gap-2 p-1 bg-slate-100 rounded-xl">
                <button
                    type="button"
                    onClick={() => handleModeChange("camera")}
                    className={`py-2.5 rounded-lg text-sm font-semibold transition-all ${mode === "camera"
                            ? "bg-white text-blue-600 shadow-sm"
                            : "text-slate-500"
                        }`}
                >
                    Camera
                </button>

                <button
                    type="button"
                    onClick={() => handleModeChange("video")}
                    className={`py-2.5 rounded-lg text-sm font-semibold transition-all ${mode === "video"
                            ? "bg-white text-blue-600 shadow-sm"
                            : "text-slate-500"
                        }`}
                >
                    Upload Video
                </button>
            </div>

            {/* ------------------------------------------------------------------ */}
            {/* CAMERA MODE                                                       */}
            {/* ------------------------------------------------------------------ */}

            {mode === "camera" && (
                <>
                    {/* Camera viewport */}
                    <div className="w-full max-w-sm aspect-[3/4] bg-slate-900 rounded-3xl overflow-hidden shadow-2xl relative border-4 border-slate-800">
                        {/* Live video */}
                        <video
                            ref={videoRef}
                            autoPlay
                            playsInline
                            muted
                            className="w-full h-full object-cover"
                        />

                        {/* Requesting */}
                        {status === "requesting" && (
                            <div className="absolute inset-0 bg-slate-900/80 flex flex-col items-center justify-center text-white space-y-3">
                                <Loader2 className="h-10 w-10 animate-spin text-blue-400" />

                                <p className="text-sm font-medium">
                                    Requesting camera access...
                                </p>
                            </div>
                        )}

                        {/* Processing */}
                        {processing && (
                            <div className="absolute inset-0 bg-black/60 backdrop-blur-[2px] flex flex-col items-center justify-center text-white space-y-3">
                                <div className="relative w-40 h-40 border-2 border-blue-400 rounded-lg">
                                    <div className="absolute top-0 left-0 right-0 h-0.5 bg-blue-400 animate-[scanline_1.5s_ease-in-out_infinite]" />
                                </div>

                                <p className="font-medium animate-pulse text-blue-300 text-sm">
                                    Recognizing face...
                                </p>
                            </div>
                        )}

                        {/* LIVE badge */}
                        {isActive && !processing && !result && (
                            <div className="absolute top-3 left-3 flex items-center space-x-1.5 bg-black/50 rounded-full px-2.5 py-1 backdrop-blur-md">
                                <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />

                                <span className="text-[10px] text-white font-bold tracking-wider uppercase">
                                    Live
                                </span>
                            </div>
                        )}

                        {/* Face guide */}
                        {isActive && !processing && !result && (
                            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                                <div className="w-40 h-52 border-2 border-white/30 rounded-[40%] shadow-inner" />
                            </div>
                        )}

                        {/* Results */}
                        {getResultType(result) === "success" && (
                            <SuccessOverlay
                                result={result}
                                onReset={handleCameraReset}
                            />
                        )}

                        {getResultType(result) === "error" && (
                            <ErrorOverlay
                                result={result}
                                onRetry={handleCameraReset}
                            />
                        )}
                    </div>

                    {/* Capture button */}
                    {isActive && !result && (
                        <button
                            type="button"
                            onClick={handleScan}
                            disabled={processing}
                            className={`w-full max-w-sm py-4 rounded-2xl font-bold text-lg text-white shadow-xl transition-all duration-200 ${processing
                                    ? "bg-blue-400 cursor-not-allowed scale-95"
                                    : "bg-blue-600 hover:bg-blue-500 active:scale-95"
                                }`}
                        >
                            {processing
                                ? "Processing..."
                                : "Capture & Clock In"}
                        </button>
                    )}

                    {/* Warning */}
                    {isActive && !result && !processing && (
                        <p className="text-xs text-slate-400 flex items-center gap-1.5 text-center">
                            <AlertTriangle className="h-3.5 w-3.5 flex-shrink-0" />
                            Look straight at the camera for face recognition
                        </p>
                    )}
                </>
            )}

            {/* ------------------------------------------------------------------ */}
            {/* UPLOAD VIDEO MODE                                                 */}
            {/* ------------------------------------------------------------------ */}

            {mode === "video" && (
                <UploadVideoSection
                    videoFile={videoFile}
                    onSelect={handleVideoSelected}
                    onRemove={handleVideoRemove}
                    onProcess={handleVideoProcess}
                    progress={uploadProgress}
                    processing={processing}
                    result={result}
                />
            )}

            {/* Upload result */}
            {mode === "video" &&
                result &&
                result.status !== "ERROR" && (
                    <div className="w-full max-w-sm">
                        {result.status === "CLOCKED_IN" ||
                            result.status === "ALREADY_CLOCKED_IN" ? (
                            <SuccessOverlay
                                result={result}
                                onReset={() => setResult(null)}
                            />
                        ) : (
                            <ErrorOverlay
                                result={result}
                                onRetry={() => setResult(null)}
                            />
                        )}
                    </div>
                )}
        </div>
    );
}