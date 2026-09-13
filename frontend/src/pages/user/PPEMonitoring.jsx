// // src/pages/user/PPEMonitoring.jsx

// import { useState, useRef, useCallback } from 'react';
// import { uploadPPEVideo } from '../../api/ppeApi';
// import {
//     UploadCloud,
//     ShieldCheck,
//     ShieldAlert,
//     HardHat,
//     Shirt,
//     FileVideo,
//     X,
//     Loader2,
//     RefreshCw,
//     CheckCircle2,
// } from 'lucide-react';

// // ── Mock response (remove when backend is ready) ──────────────────────────────
// async function mockUploadPPEVideo(videoFile, onProgress) {
//     // TODO: replace with → return await uploadPPEVideo(videoFile, onProgress);
//     for (let p = 0; p <= 100; p += 20) {
//         await new Promise(r => setTimeout(r, 250));
//         onProgress?.(p);
//     }
//     // Simulate AI processing delay
//     await new Promise(r => setTimeout(r, 1500));

//     const compliant = Math.random() > 0.4;
//     return {
//         overall: compliant ? 'compliant' : 'violation',
//         complianceScore: compliant ? Math.floor(Math.random() * 10 + 90) : Math.floor(Math.random() * 30 + 50),
//         items: {
//             hardhat: compliant || Math.random() > 0.4,
//             vest: true,
//         },
//         message: compliant
//             ? 'All required PPE was detected throughout the session.'
//             : 'Some required PPE items were not consistently detected.',
//     };
// }
// // ─────────────────────────────────────────────────────────────────────────────

// const PPE_ITEMS = [
//     { key: 'hardhat', label: 'Safety Hardhat', Icon: HardHat },
//     { key: 'vest', label: 'High-Vis Vest', Icon: Shirt },
// ];

// // ── Sub-components ────────────────────────────────────────────────────────────

// function PPEItemRow({ icon: Icon, label, checked }) {
//     return (
//         <li className={`flex items-center justify-between p-3 rounded-xl border transition-all ${
//             checked ? 'bg-green-50 border-green-100' : 'bg-red-50 border-red-100'
//         }`}>
//             <div className="flex items-center gap-3">
//                 <div className={`p-2 rounded-lg ${checked ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-500'}`}>
//                     <Icon className="h-5 w-5" />
//                 </div>
//                 <span className={`font-medium text-sm ${checked ? 'text-slate-800' : 'text-red-700'}`}>{label}</span>
//             </div>
//             <span className={`font-bold text-sm ${checked ? 'text-green-500' : 'text-red-400'}`}>
//                 {checked ? '✓ Detected' : '✗ Missing'}
//             </span>
//         </li>
//     );
// }

// function UploadZone({ onFileSelected, isDragging, onDragOver, onDragLeave, onDrop }) {
//     const inputRef = useRef(null);

//     return (
//         <div
//             className={`relative border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all duration-200 ${
//                 isDragging
//                     ? 'border-blue-500 bg-blue-50 scale-[1.02]'
//                     : 'border-slate-300 bg-slate-50 hover:border-blue-400 hover:bg-blue-50/50'
//             }`}
//             onClick={() => inputRef.current?.click()}
//             onDragOver={onDragOver}
//             onDragLeave={onDragLeave}
//             onDrop={onDrop}
//         >
//             <input
//                 ref={inputRef}
//                 type="file"
//                 accept="video/*"
//                 className="hidden"
//                 onChange={e => onFileSelected(e.target.files[0])}
//             />
//             <div className="flex flex-col items-center gap-3">
//                 <div className="p-4 bg-blue-100 rounded-full">
//                     <UploadCloud className="h-8 w-8 text-blue-500" />
//                 </div>
//                 <div>
//                     <p className="font-semibold text-slate-700">Tap to upload your video</p>
//                     <p className="text-xs text-slate-400 mt-1">or drag and drop here</p>
//                 </div>
//                 <p className="text-xs text-slate-400 bg-white border border-slate-200 px-3 py-1 rounded-full">
//                     MP4, MOV, AVI, WEBM
//                 </p>
//             </div>
//         </div>
//     );
// }

// function VideoPreview({ file, onRemove }) {
//     const url = URL.createObjectURL(file);
//     return (
//         <div className="relative bg-slate-900 rounded-2xl overflow-hidden shadow-lg border border-slate-800">
//             <video
//                 src={url}
//                 controls
//                 className="w-full max-h-56 object-contain"
//                 onLoad={() => URL.revokeObjectURL(url)}
//             />
//             <div className="absolute top-2 left-2 flex items-center gap-2 bg-black/60 rounded-full px-2.5 py-1 backdrop-blur-sm">
//                 <FileVideo className="h-3.5 w-3.5 text-white" />
//                 <span className="text-[11px] text-white font-medium truncate max-w-[140px]">{file.name}</span>
//             </div>
//             <button
//                 onClick={onRemove}
//                 className="absolute top-2 right-2 p-1 bg-black/60 hover:bg-black/80 rounded-full text-white transition-colors"
//             >
//                 <X className="h-4 w-4" />
//             </button>
//         </div>
//     );
// }

// function UploadProgress({ progress }) {
//     return (
//         <div className="space-y-2">
//             <div className="flex justify-between text-xs text-slate-500">
//                 <span className="font-medium animate-pulse">
//                     {progress < 100 ? 'Uploading video...' : 'Analyzing PPE...'}
//                 </span>
//                 <span>{progress}%</span>
//             </div>
//             <div className="w-full bg-slate-200 rounded-full h-2.5 overflow-hidden">
//                 <div
//                     className="h-2.5 rounded-full bg-gradient-to-r from-blue-500 to-indigo-500 transition-all duration-300"
//                     style={{ width: `${progress}%` }}
//                 />
//             </div>
//             {progress === 100 && (
//                 <p className="text-center text-xs text-indigo-600 font-medium flex items-center justify-center gap-1.5 animate-pulse">
//                     <Loader2 className="h-3 w-3 animate-spin" />
//                     AI is analyzing your PPE compliance...
//                 </p>
//             )}
//         </div>
//     );
// }

// function ResultCard({ result }) {
//     const isCompliant = result.overall === 'compliant';

//     return (
//         <div className={`rounded-2xl border p-5 space-y-4 ${
//             isCompliant ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'
//         }`}>
//             {/* Header */}
//             <div className="flex items-center gap-3">
//                 {isCompliant
//                     ? <CheckCircle2 className="h-8 w-8 text-green-500 flex-shrink-0" />
//                     : <ShieldAlert className="h-8 w-8 text-red-500 flex-shrink-0" />
//                 }
//                 <div>
//                     <h3 className={`font-bold text-lg ${isCompliant ? 'text-green-700' : 'text-red-700'}`}>
//                         {isCompliant ? 'PPE Compliant' : 'PPE Violation Detected'}
//                     </h3>
//                     <p className="text-xs text-slate-500">{result.message}</p>
//                 </div>
//             </div>

//             {/* Score */}
//             <div className="flex items-center gap-3">
//                 <span className="text-xs text-slate-500 font-medium w-20">Compliance</span>
//                 <div className="flex-1 bg-slate-200 rounded-full h-2">
//                     <div
//                         className={`h-2 rounded-full transition-all duration-700 ${
//                             result.complianceScore >= 90 ? 'bg-green-500' :
//                             result.complianceScore >= 70 ? 'bg-yellow-400' : 'bg-red-500'
//                         }`}
//                         style={{ width: `${result.complianceScore}%` }}
//                     />
//                 </div>
//                 <span className={`text-sm font-bold w-10 text-right ${
//                     result.complianceScore >= 90 ? 'text-green-600' :
//                     result.complianceScore >= 70 ? 'text-yellow-600' : 'text-red-600'
//                 }`}>{result.complianceScore}%</span>
//             </div>

//             {/* Per-item breakdown */}
//             <ul className="space-y-2">
//                 {PPE_ITEMS.map(({ key, label, Icon }) => (
//                     <PPEItemRow key={key} icon={Icon} label={label} checked={result.items[key]} />
//                 ))}
//             </ul>
//         </div>
//     );
// }

// // ── Main Component ────────────────────────────────────────────────────────────

// export default function PPEMonitoring() {
//     const [videoFile, setVideoFile] = useState(null);
//     const [uploadProgress, setUploadProgress] = useState(0);
//     const [status, setStatus] = useState('idle'); // 'idle' | 'uploading' | 'done' | 'error'
//     const [result, setResult] = useState(null);
//     const [errorMsg, setErrorMsg] = useState('');
//     const [isDragging, setIsDragging] = useState(false);

//     const handleFileSelected = useCallback((file) => {
//         if (!file || !file.type.startsWith('video/')) return;
//         setVideoFile(file);
//         setStatus('idle');
//         setResult(null);
//         setErrorMsg('');
//     }, []);

//     const handleDragOver = (e) => { e.preventDefault(); setIsDragging(true); };
//     const handleDragLeave = () => setIsDragging(false);
//     const handleDrop = (e) => {
//         e.preventDefault();
//         setIsDragging(false);
//         handleFileSelected(e.dataTransfer.files[0]);
//     };

//     const handleRemoveFile = () => {
//         setVideoFile(null);
//         setStatus('idle');
//         setResult(null);
//         setUploadProgress(0);
//     };

//     const handleAnalyze = async () => {
//         if (!videoFile) return;
//         setStatus('uploading');
//         setUploadProgress(0);
//         setResult(null);
//         setErrorMsg('');

//         try {
//             const res = await mockUploadPPEVideo(videoFile, setUploadProgress);
//             setResult(res);
//             setStatus('done');
//         } catch (err) {
//             setErrorMsg(err.message || 'Failed to analyze video. Please try again.');
//             setStatus('error');
//         }
//     };

//     return (
//         <div className="flex-1 flex flex-col py-4 space-y-5">

//             {/* Title */}
//             <div className="text-center space-y-1">
//                 <h1 className="text-2xl font-extrabold text-slate-900">PPE Check</h1>
//                 <p className="text-sm text-slate-500">Upload your session video to verify PPE compliance.</p>
//             </div>

//             {/* Upload zone or video preview */}
//             {!videoFile ? (
//                 <UploadZone
//                     onFileSelected={handleFileSelected}
//                     isDragging={isDragging}
//                     onDragOver={handleDragOver}
//                     onDragLeave={handleDragLeave}
//                     onDrop={handleDrop}
//                 />
//             ) : (
//                 <VideoPreview file={videoFile} onRemove={handleRemoveFile} />
//             )}

//             {/* Upload progress */}
//             {status === 'uploading' && (
//                 <UploadProgress progress={uploadProgress} />
//             )}

//             {/* Result */}
//             {status === 'done' && result && (
//                 <ResultCard result={result} />
//             )}

//             {/* Error */}
//             {status === 'error' && (
//                 <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-700 flex items-start gap-2">
//                     <ShieldAlert className="h-5 w-5 flex-shrink-0 mt-0.5" />
//                     <div>
//                         <p className="font-semibold">Upload failed</p>
//                         <p className="text-red-500">{errorMsg}</p>
//                     </div>
//                 </div>
//             )}

//             {/* Action buttons */}
//             {videoFile && status !== 'uploading' && (
//                 <div className="flex gap-3 pt-1">
//                     {status !== 'done' ? (
//                         <button
//                             onClick={handleAnalyze}
//                             className="flex-1 py-3.5 bg-blue-600 hover:bg-blue-500 active:scale-95 text-white font-bold rounded-xl transition-all flex items-center justify-center gap-2"
//                         >
//                             <ShieldCheck className="h-5 w-5" />
//                             Analyze PPE
//                         </button>
//                     ) : (
//                         <button
//                             onClick={handleRemoveFile}
//                             className="flex-1 py-3.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold rounded-xl transition-all flex items-center justify-center gap-2"
//                         >
//                             <RefreshCw className="h-4 w-4" />
//                             Upload Another Video
//                         </button>
//                     )}
//                 </div>
//             )}

//         </div>
//     );
// }
// src/pages/user/PPEMonitoring.jsx

import { useCallback, useEffect, useRef, useState } from "react";
import { uploadPPEVideo } from "../../api/ppeApi";
import {
    UploadCloud,
    ShieldCheck,
    ShieldAlert,
    HardHat,
    Shirt,
    FileVideo,
    X,
    Loader2,
    RefreshCw,
    CheckCircle2,
    AlertCircle,
} from "lucide-react";

const PPE_ITEMS = [
    {
        key: "hardhat",
        label: "Safety Hardhat",
        Icon: HardHat,
    },
    {
        key: "vest",
        label: "High-Vis Vest",
        Icon: Shirt,
    },
];

/**
 * Convert the backend's PPE status into frontend display data.
 *
 * Supported Phase 7 statuses:
 * FULL_PPE
 * HELMET_MISSING
 * VEST_MISSING
 * NO_PPE
 */
function normalizeBackendResult(data) {
    const status =
        data?.compliance_status ||
        data?.status ||
        data?.overall_status ||
        null;

    const normalizedStatus = String(status || "").toUpperCase();

    let items = {
        hardhat: false,
        vest: false,
    };

    switch (normalizedStatus) {
        case "FULL_PPE":
            items = {
                hardhat: true,
                vest: true,
            };
            break;

        case "HELMET_MISSING":
            items = {
                hardhat: false,
                vest: true,
            };
            break;

        case "VEST_MISSING":
            items = {
                hardhat: true,
                vest: false,
            };
            break;

        case "NO_PPE":
            items = {
                hardhat: false,
                vest: false,
            };
            break;

        default:
            /*
             * Prefer explicit booleans when the backend response
             * provides them.
             */
            items = {
                hardhat: Boolean(
                    data?.helmet_detected ??
                    data?.helmetDetected ??
                    data?.items?.hardhat
                ),
                vest: Boolean(
                    data?.vest_detected ??
                    data?.vestDetected ??
                    data?.items?.vest
                ),
            };
            break;
    }

    const complianceScore =
        typeof data?.compliance_score === "number"
            ? data.compliance_score
            : typeof data?.complianceScore === "number"
                ? data.complianceScore
                : null;

    let overall = "unknown";

    if (normalizedStatus === "FULL_PPE") {
        overall = "compliant";
    } else if (
        normalizedStatus === "HELMET_MISSING" ||
        normalizedStatus === "VEST_MISSING" ||
        normalizedStatus === "NO_PPE"
    ) {
        overall = "violation";
    }

    return {
        ...data,
        status: normalizedStatus || data?.status || null,
        overall,
        complianceScore,
        items,
    };
}

// -----------------------------------------------------------------------------
// Sub-components
// -----------------------------------------------------------------------------

function PPEItemRow({ icon: Icon, label, checked }) {
    return (
        <li
            className={`flex items-center justify-between p-3 rounded-xl border transition-all ${checked
                ? "bg-green-50 border-green-100"
                : "bg-red-50 border-red-100"
                }`}
        >
            <div className="flex items-center gap-3">
                <div
                    className={`p-2 rounded-lg ${checked
                        ? "bg-green-100 text-green-600"
                        : "bg-red-100 text-red-500"
                        }`}
                >
                    <Icon className="h-5 w-5" />
                </div>

                <span
                    className={`font-medium text-sm ${checked ? "text-slate-800" : "text-red-700"
                        }`}
                >
                    {label}
                </span>
            </div>

            <span
                className={`font-bold text-sm ${checked ? "text-green-500" : "text-red-400"
                    }`}
            >
                {checked ? "✓ Detected" : "✗ Missing"}
            </span>
        </li>
    );
}

function UploadZone({
    onFileSelected,
    isDragging,
    onDragOver,
    onDragLeave,
    onDrop,
}) {
    const inputRef = useRef(null);

    const handleInputChange = (event) => {
        const file = event.target.files?.[0];

        if (file) {
            onFileSelected(file);
        }

        // Allow selecting the same file again after removal.
        event.target.value = "";
    };

    return (
        <div
            className={`relative border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all duration-200 ${isDragging
                ? "border-blue-500 bg-blue-50 scale-[1.02]"
                : "border-slate-300 bg-slate-50 hover:border-blue-400 hover:bg-blue-50/50"
                }`}
            onClick={() => inputRef.current?.click()}
            onDragOver={onDragOver}
            onDragLeave={onDragLeave}
            onDrop={onDrop}
        >
            <input
                ref={inputRef}
                type="file"
                accept="video/*"
                className="hidden"
                onChange={handleInputChange}
            />

            <div className="flex flex-col items-center gap-3">
                <div className="p-4 bg-blue-100 rounded-full">
                    <UploadCloud className="h-8 w-8 text-blue-500" />
                </div>

                <div>
                    <p className="font-semibold text-slate-700">
                        Tap to upload your video
                    </p>
                    <p className="text-xs text-slate-400 mt-1">
                        or drag and drop here
                    </p>
                </div>

                <p className="text-xs text-slate-400 bg-white border border-slate-200 px-3 py-1 rounded-full">
                    MP4, MOV, AVI, WEBM
                </p>
            </div>
        </div>
    );
}

function VideoPreview({ file, onRemove }) {
    const [videoUrl, setVideoUrl] = useState("");

    useEffect(() => {
        if (!file) {
            setVideoUrl("");
            return undefined;
        }

        const url = URL.createObjectURL(file);
        setVideoUrl(url);

        return () => {
            URL.revokeObjectURL(url);
        };
    }, [file]);

    return (
        <div className="relative bg-slate-900 rounded-2xl overflow-hidden shadow-lg border border-slate-800">
            <video
                src={videoUrl}
                controls
                className="w-full max-h-56 object-contain"
            />

            <div className="absolute top-2 left-2 flex items-center gap-2 bg-black/60 rounded-full px-2.5 py-1 backdrop-blur-sm">
                <FileVideo className="h-3.5 w-3.5 text-white" />

                <span className="text-[11px] text-white font-medium truncate max-w-[140px]">
                    {file.name}
                </span>
            </div>

            <button
                type="button"
                onClick={onRemove}
                className="absolute top-2 right-2 p-1 bg-black/60 hover:bg-black/80 rounded-full text-white transition-colors"
                aria-label="Remove video"
            >
                <X className="h-4 w-4" />
            </button>
        </div>
    );
}

function ProcessingStatus({ progress }) {
    const uploading = progress < 100;

    return (
        <div className="space-y-2">
            <div className="flex justify-between text-xs text-slate-500">
                <span className="font-medium animate-pulse">
                    {uploading ? "Uploading video..." : "Processing PPE..."}
                </span>

                <span>{progress}%</span>
            </div>

            <div className="w-full bg-slate-200 rounded-full h-2.5 overflow-hidden">
                <div
                    className="h-2.5 rounded-full bg-gradient-to-r from-blue-500 to-indigo-500 transition-all duration-300"
                    style={{ width: `${progress}%` }}
                />
            </div>

            {!uploading && (
                <p className="text-center text-xs text-indigo-600 font-medium flex items-center justify-center gap-1.5 animate-pulse">
                    <Loader2 className="h-3 w-3 animate-spin" />
                    Backend is analyzing your PPE video...
                </p>
            )}
        </div>
    );
}

function ResultCard({ result }) {
    const isCompliant = result.overall === "compliant";
    const score = result.complianceScore;

    return (
        <div
            className={`rounded-2xl border p-5 space-y-4 ${isCompliant
                ? "bg-green-50 border-green-200"
                : "bg-red-50 border-red-200"
                }`}
        >
            <div className="flex items-center gap-3">
                {isCompliant ? (
                    <CheckCircle2 className="h-8 w-8 text-green-500 flex-shrink-0" />
                ) : (
                    <ShieldAlert className="h-8 w-8 text-red-500 flex-shrink-0" />
                )}

                <div>
                    <h3
                        className={`font-bold text-lg ${isCompliant ? "text-green-700" : "text-red-700"
                            }`}
                    >
                        {isCompliant
                            ? "PPE Compliant"
                            : result.status || "PPE Compliance Result"}
                    </h3>

                    <p className="text-xs text-slate-500">
                        {result.message ||
                            "The backend returned a PPE compliance result."}
                    </p>
                </div>
            </div>

            {typeof score === "number" && (
                <div className="flex items-center gap-3">
                    <span className="text-xs text-slate-500 font-medium w-20">
                        Compliance
                    </span>

                    <div className="flex-1 bg-slate-200 rounded-full h-2">
                        <div
                            className={`h-2 rounded-full transition-all duration-700 ${score >= 90
                                ? "bg-green-500"
                                : score >= 70
                                    ? "bg-yellow-400"
                                    : "bg-red-500"
                                }`}
                            style={{
                                width: `${Math.min(100, Math.max(0, score))}%`,
                            }}
                        />
                    </div>

                    <span
                        className={`text-sm font-bold w-10 text-right ${score >= 90
                            ? "text-green-600"
                            : score >= 70
                                ? "text-yellow-600"
                                : "text-red-600"
                            }`}
                    >
                        {score}%
                    </span>
                </div>
            )}

            <ul className="space-y-2">
                {PPE_ITEMS.map(({ key, label, Icon }) => (
                    <PPEItemRow
                        key={key}
                        icon={Icon}
                        label={label}
                        checked={result.items[key]}
                    />
                ))}
            </ul>
        </div>
    );
}

function ErrorCard({ message }) {
    return (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-700 flex items-start gap-2">
            <ShieldAlert className="h-5 w-5 flex-shrink-0 mt-0.5" />

            <div>
                <p className="font-semibold">PPE analysis failed</p>

                <p className="text-red-500 mt-1">
                    {message || "The backend could not process the video."}
                </p>
            </div>
        </div>
    );
}

// -----------------------------------------------------------------------------
// Main component
// -----------------------------------------------------------------------------

export default function PPEMonitoring() {
    const [videoFile, setVideoFile] = useState(null);
    const [uploadProgress, setUploadProgress] = useState(0);

    const [status, setStatus] = useState("idle");
    // idle | processing | done | error

    const [result, setResult] = useState(null);
    const [errorMsg, setErrorMsg] = useState("");
    const [isDragging, setIsDragging] = useState(false);

    const handleFileSelected = useCallback((file) => {
        if (!file) {
            return;
        }

        if (!file.type.startsWith("video/")) {
            setVideoFile(null);
            setStatus("error");
            setResult(null);
            setErrorMsg("Please select a valid video file.");
            return;
        }

        setVideoFile(file);
        setStatus("idle");
        setResult(null);
        setErrorMsg("");
        setUploadProgress(0);
    }, []);

    const handleDragOver = (event) => {
        event.preventDefault();
        event.stopPropagation();
        setIsDragging(true);
    };

    const handleDragLeave = (event) => {
        event.preventDefault();
        event.stopPropagation();
        setIsDragging(false);
    };

    const handleDrop = (event) => {
        event.preventDefault();
        event.stopPropagation();

        setIsDragging(false);

        const file = event.dataTransfer.files?.[0];

        if (file) {
            handleFileSelected(file);
        }
    };

    const handleRemoveFile = () => {
        setVideoFile(null);
        setStatus("idle");
        setResult(null);
        setErrorMsg("");
        setUploadProgress(0);
    };

    const handleAnalyze = async () => {
        if (!videoFile) {
            return;
        }

        setStatus("processing");
        setUploadProgress(0);
        setResult(null);
        setErrorMsg("");

        try {
            /*
             * REAL BACKEND REQUEST
             *
             * React
             *   ↓
             * uploadPPEVideo()
             *   ↓
             * Axios
             *   ↓
             * FastAPI /ppe/analyze-video
             *   ↓
             * Phase 7 PPEMonitor
             *   ↓
             * PostgreSQL
             *   ↓
             * FastAPI response
             *   ↓
             * React
             */
            const backendResponse = await uploadPPEVideo(
                videoFile,
                setUploadProgress
            );

            const normalizedResult =
                normalizeBackendResult(backendResponse);

            setResult(normalizedResult);
            setStatus("done");
        } catch (error) {
            setStatus("error");

            setErrorMsg(
                error?.message ||
                "Failed to analyze the PPE video. Please try again."
            );
        }
    };

    const handleRetry = () => {
        setStatus("idle");
        setResult(null);
        setErrorMsg("");
        setUploadProgress(0);
    };

    return (
        <div className="flex-1 flex flex-col py-4 space-y-5">
            {/* Title */}
            <div className="text-center space-y-1">
                <h1 className="text-2xl font-extrabold text-slate-900">
                    PPE Check
                </h1>

                <p className="text-sm text-slate-500">
                    Upload your session video to verify PPE compliance.
                </p>
            </div>

            {/* Upload zone / preview */}
            {!videoFile ? (
                <UploadZone
                    onFileSelected={handleFileSelected}
                    isDragging={isDragging}
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                />
            ) : (
                <VideoPreview
                    file={videoFile}
                    onRemove={handleRemoveFile}
                />
            )}

            {/* Processing */}
            {status === "processing" && (
                <ProcessingStatus progress={uploadProgress} />
            )}

            {/* Backend result */}
            {status === "done" && result && (
                <ResultCard result={result} />
            )}

            {/* Backend error */}
            {status === "error" && (
                <ErrorCard message={errorMsg} />
            )}

            {/* Actions */}
            {videoFile && status !== "processing" && (
                <div className="flex gap-3 pt-1">
                    {status === "done" ? (
                        <button
                            type="button"
                            onClick={handleRemoveFile}
                            className="flex-1 py-3.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold rounded-xl transition-all flex items-center justify-center gap-2"
                        >
                            <RefreshCw className="h-4 w-4" />
                            Upload Another Video
                        </button>
                    ) : (
                        <>
                            <button
                                type="button"
                                onClick={handleAnalyze}
                                className="flex-1 py-3.5 bg-blue-600 hover:bg-blue-500 active:scale-95 text-white font-bold rounded-xl transition-all flex items-center justify-center gap-2"
                            >
                                <ShieldCheck className="h-5 w-5" />
                                Analyze PPE
                            </button>

                            {status === "error" && (
                                <button
                                    type="button"
                                    onClick={handleRetry}
                                    className="px-5 py-3.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold rounded-xl transition-all flex items-center justify-center gap-2"
                                >
                                    <RefreshCw className="h-4 w-4" />
                                    Retry
                                </button>
                            )}
                        </>
                    )}
                </div>
            )}
        </div>
    );
}