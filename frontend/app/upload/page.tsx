export default function UploadPage() {
  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* Header */}
      <div className="border-b border-[#1e293b] pb-6">
        <h1 className="text-3xl font-extrabold text-slate-100 tracking-tight">
          Upload & Analyze Imagery
        </h1>
        <p className="text-slate-400 mt-2 text-sm">
          Submit high-resolution satellite imagery (optical, infrared, thermal, or SAR) for immediate AI disaster classification and damage evaluation.
        </p>
      </div>

      {/* Upload Placeholder Container */}
      <div className="p-8 rounded-2xl bg-[#131b2e] border-2 border-dashed border-[#1e293b] flex flex-col items-center justify-center text-center space-y-4 min-h-[280px]">
        <div className="w-16 h-16 rounded-full bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
          <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
        </div>

        <div>
          <h2 className="text-lg font-bold text-slate-200">Drag & drop satellite raster file</h2>
          <p className="text-xs text-slate-400 mt-1">Supports GeoTIFF, PNG, JPG, and HDF5 up to 100MB</p>
        </div>

        <button
          type="button"
          className="px-5 py-2.5 rounded-lg bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 text-sm font-semibold hover:bg-cyan-500/30 transition cursor-pointer"
        >
          Select File (Placeholder)
        </button>
      </div>

      {/* Form Parameters Placeholder */}
      <div className="p-6 rounded-xl bg-[#131b2e] border border-[#1e293b] space-y-4">
        <h3 className="text-md font-bold text-slate-200">Analysis Options</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs text-slate-400 mb-1 font-medium">Imagery Band Type</label>
            <select disabled className="w-full bg-[#0e1424] border border-[#1e293b] rounded-lg px-3 py-2 text-sm text-slate-300 opacity-70">
              <option>Thermal Infrared (TIR)</option>
              <option>Multispectral (RGB + NIR)</option>
              <option>Synthetic Aperture Radar (SAR)</option>
            </select>
          </div>
          <div>
            <label className="block text-xs text-slate-400 mb-1 font-medium">Target Disaster Model</label>
            <select disabled className="w-full bg-[#0e1424] border border-[#1e293b] rounded-lg px-3 py-2 text-sm text-slate-300 opacity-70">
              <option>Auto-Detect (Recommended)</option>
              <option>Wildfire & Thermal Anomaly</option>
              <option>Flood Inundation & Water Boundaries</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  );
}
