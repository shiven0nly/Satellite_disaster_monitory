"use client";

import React, { useState, useRef, ChangeEvent, DragEvent } from "react";
import { ImageType } from "@/types";

const ALLOWED_EXTENSIONS = [".jpg", ".jpeg", ".png", ".tiff", ".tif"];
const MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024; // 20MB

interface UploadDropzoneProps {
  onFileSubmit: (file: File, imageType: ImageType) => void;
  isUploading: boolean;
}

export default function UploadDropzone({ onFileSubmit, isUploading }: UploadDropzoneProps) {
  const [dragActive, setDragActive] = useState<boolean>(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [imageType, setImageType] = useState<ImageType>(ImageType.OTHER);
  const [validationError, setValidationError] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateFile = (file: File): boolean => {
    setValidationError(null);

    const ext = "." + file.name.split(".").pop()?.toLowerCase();
    if (!ALLOWED_EXTENSIONS.includes(ext)) {
      setValidationError(
        `Unsupported file type '${ext}'. Allowed types: ${ALLOWED_EXTENSIONS.join(", ")}`
      );
      return false;
    }

    if (file.size > MAX_FILE_SIZE_BYTES) {
      const fileSizeMB = (file.size / (1024 * 1024)).toFixed(2);
      setValidationError(
        `File size (${fileSizeMB}MB) exceeds the maximum allowed limit of 20MB.`
      );
      return false;
    }

    return true;
  };

  const handleFile = (file: File) => {
    if (validateFile(file)) {
      setSelectedFile(file);
      // Create object URL for web image preview (.jpg, .png)
      if (file.type.startsWith("image/") && !file.name.toLowerCase().endsWith(".tiff") && !file.name.toLowerCase().endsWith(".tif")) {
        setPreviewUrl(URL.createObjectURL(file));
      } else {
        setPreviewUrl(null); // TIFF files cannot be directly rendered in native <img> without canvas decoder
      }
    }
  };

  const handleDrag = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
      setPreviewUrl(null);
    }
    setValidationError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedFile) {
      onFileSubmit(selectedFile, imageType);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Validation Error Alert */}
      {validationError && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-sm flex items-center justify-between">
          <div className="flex items-center gap-3">
            <svg className="w-5 h-5 shrink-0 text-rose-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <span>{validationError}</span>
          </div>
          <button
            type="button"
            onClick={() => setValidationError(null)}
            className="text-rose-400 hover:text-rose-200 text-xs font-semibold"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Dropzone Container */}
      {!selectedFile ? (
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`p-10 rounded-2xl border-2 border-dashed transition-all duration-200 flex flex-col items-center justify-center text-center cursor-pointer min-h-[300px] ${
            dragActive
              ? "border-cyan-400 bg-cyan-500/10 shadow-[0_0_30px_rgba(6,182,212,0.25)] scale-[1.01]"
              : "border-[#1e293b] bg-[#131b2e] hover:border-cyan-500/50 hover:bg-[#172036]"
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".jpg,.jpeg,.png,.tiff,.tif"
            onChange={handleFileInputChange}
            className="hidden"
          />

          <div className={`w-16 h-16 rounded-full flex items-center justify-center mb-4 transition-transform duration-200 ${
            dragActive ? "bg-cyan-500/20 text-cyan-300 scale-110" : "bg-cyan-500/10 border border-cyan-500/30 text-cyan-400"
          }`}>
            <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
            </svg>
          </div>

          <h3 className="text-lg font-bold text-slate-100">
            {dragActive ? "Drop satellite image file here" : "Drag & drop satellite raster image here"}
          </h3>
          <p className="text-xs text-slate-400 mt-2 max-w-sm">
            Supported formats: <code className="text-cyan-400 font-mono">.JPG, .PNG, .TIFF</code> up to 20MB.
          </p>

          <button
            type="button"
            className="mt-5 px-5 py-2.5 rounded-lg bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/40 text-sm font-semibold transition"
          >
            Browse Computer
          </button>
        </div>
      ) : (
        /* Selected File Preview Box */
        <div className="p-6 rounded-2xl bg-[#131b2e] border border-[#1e293b] space-y-6">
          <div className="flex items-center justify-between border-b border-[#1e293b] pb-4">
            <div className="flex items-center gap-3">
              <span className="w-3 h-3 rounded-full bg-cyan-400"></span>
              <h3 className="text-sm font-bold text-slate-100">Selected Image Preview</h3>
            </div>
            <button
              type="button"
              onClick={handleRemoveFile}
              disabled={isUploading}
              className="text-xs font-medium text-rose-400 hover:text-rose-300 disabled:opacity-50 flex items-center gap-1"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
              Remove
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
            {/* Thumbnail Preview Column */}
            <div className="md:col-span-1 flex flex-col items-center">
              {previewUrl ? (
                // Standard browser image preview (.png, .jpg)
                <div className="w-full h-44 rounded-xl border border-[#1e293b] overflow-hidden bg-[#080c14] relative group">
                  {/* eslint-disable-next-html-element-suppression */}
                  <img
                    src={previewUrl}
                    alt="Satellite Image Preview"
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-slate-950/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-end p-3">
                    <span className="text-[10px] font-mono text-cyan-300">Ready for AI segmentation</span>
                  </div>
                </div>
              ) : (
                // TIFF / Non-standard image preview placeholder
                <div className="w-full h-44 rounded-xl border border-[#1e293b] bg-[#080c14] flex flex-col items-center justify-center p-4 text-center">
                  <svg className="w-10 h-10 text-cyan-400 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <span className="text-xs font-semibold text-slate-300">GeoTIFF Data Layer</span>
                  <span className="text-[10px] text-slate-400 mt-1">Multi-band spatial raster file</span>
                </div>
              )}
            </div>

            {/* File Info & Options Column */}
            <div className="md:col-span-2 space-y-4">
              <div>
                <div className="text-xs text-slate-400 font-medium">Filename</div>
                <div className="text-sm font-semibold text-slate-100 truncate">{selectedFile.name}</div>
                <div className="text-xs text-cyan-400 font-mono mt-0.5">
                  Size: {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                </div>
              </div>

              <div>
                <label htmlFor="image-type-select" className="block text-xs font-semibold text-slate-300 mb-1.5">
                  Satellite Band / Sensor Type
                </label>
                <select
                  id="image-type-select"
                  value={imageType}
                  onChange={(e) => setImageType(e.target.value as ImageType)}
                  disabled={isUploading}
                  className="w-full bg-[#080c14] border border-[#1e293b] rounded-lg px-3.5 py-2 text-sm text-slate-200 focus:outline-none focus:border-cyan-500 transition"
                >
                  <option value={ImageType.OTHER}>Auto-detect / Standard Optical (RGB)</option>
                  <option value={ImageType.THERMAL}>Thermal Infrared (TIR) - Fire & Hotspots</option>
                  <option value={ImageType.IR}>Short-wave Infrared (SWIR/NIR)</option>
                </select>
              </div>
            </div>
          </div>

          <div className="pt-4 border-t border-[#1e293b] flex justify-end">
            <button
              type="submit"
              disabled={isUploading}
              className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-violet-600 hover:from-cyan-400 hover:to-violet-500 text-white font-semibold text-sm transition shadow-lg shadow-cyan-500/25 flex items-center gap-2 cursor-pointer disabled:opacity-50"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {isUploading ? "Uploading..." : "Start AI Analysis"}
            </button>
          </div>
        </div>
      )}
    </form>
  );
}
