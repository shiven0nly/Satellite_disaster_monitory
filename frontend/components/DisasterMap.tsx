"use client";

import React, { useEffect } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { JobRead } from "@/types";
import { getSeverityTheme } from "@/lib/severity";
import MapLegend from "@/components/MapLegend";
import MarkerPopup from "@/components/MarkerPopup";

interface DisasterMapProps {
  jobs: JobRead[];
}

function createSeverityIcon(severity?: string) {
  const theme = getSeverityTheme(severity);

  const svgHtml = `
    <div style="
      position: relative;
      width: 32px;
      height: 32px;
      display: flex;
      align-items: center;
      justify-content: center;
    ">
      <div style="
        position: absolute;
        width: 100%;
        height: 100%;
        border-radius: 50%;
        background-color: ${theme.hex};
        opacity: 0.35;
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
      "></div>
      <div style="
        width: 20px;
        height: 20px;
        border-radius: 50%;
        background: radial-gradient(circle at 35% 35%, #ffffff, ${theme.hex});
        border: 2px solid #ffffff;
        box-shadow: 0 0 10px ${theme.shadow}, 0 2px 4px rgba(0,0,0,0.6);
      "></div>
    </div>
  `;

  return L.divIcon({
    html: svgHtml,
    className: "custom-disaster-marker-icon",
    iconSize: [32, 32],
    iconAnchor: [16, 16],
    popupAnchor: [0, -16],
  });
}

function MapBoundsAdjuster({ jobs }: { jobs: JobRead[] }) {
  const map = useMap();

  useEffect(() => {
    if (jobs.length > 0) {
      const validCoords = jobs
        .map((job) => {
          const lat = job.result?.latitude;
          const lng = job.result?.longitude;
          if (
            lat !== undefined &&
            lat !== null &&
            lng !== undefined &&
            lng !== null &&
            !isNaN(lat) &&
            !isNaN(lng)
          ) {
            return [lat, lng] as [number, number];
          }
          return null;
        })
        .filter((coord): coord is [number, number] => coord !== null);

      if (validCoords.length > 0) {
        if (validCoords.length === 1) {
          map.setView(validCoords[0], 10);
        } else {
          const bounds = L.latLngBounds(validCoords);
          map.fitBounds(bounds, { padding: [50, 50], maxZoom: 12 });
        }
      }
    }
  }, [jobs, map]);

  return null;
}

export default function DisasterMap({ jobs }: DisasterMapProps) {
  const validJobs = jobs.filter(
    (j) =>
      j.result &&
      j.result.latitude !== undefined &&
      j.result.latitude !== null &&
      j.result.longitude !== undefined &&
      j.result.longitude !== null &&
      !isNaN(j.result.latitude) &&
      !isNaN(j.result.longitude)
  );

  return (
    <div className="relative w-full h-[550px] rounded-2xl overflow-hidden border border-[#1e293b] shadow-2xl bg-[#080c14]">
      <MapContainer
        center={[20, 0]}
        zoom={2}
        scrollWheelZoom={true}
        className="w-full h-full z-0"
        style={{ background: "#0b0f19" }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          maxZoom={19}
        />

        <MapBoundsAdjuster jobs={validJobs} />

        {validJobs.map((job) => (
          <Marker
            key={job.id}
            position={[job.result!.latitude!, job.result!.longitude!]}
            icon={createSeverityIcon(job.result?.severity)}
          >
            <Popup>
              <MarkerPopup job={job} />
            </Popup>
          </Marker>
        ))}
      </MapContainer>

      {/* Fixed Map Legend Overlay */}
      <MapLegend />

      {/* Empty State Banner Overlay if no valid markers exist */}
      {validJobs.length === 0 && (
        <div className="absolute inset-0 bg-[#080c14]/75 backdrop-blur-xs flex items-center justify-center z-[1000] p-6 text-center">
          <div className="max-w-md p-6 rounded-2xl bg-[#131b2e] border border-[#1e293b] space-y-3 shadow-2xl">
            <div className="w-12 h-12 rounded-full bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center mx-auto text-cyan-400">
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
            <h3 className="text-base font-bold text-slate-100">No Plotted Markers Available</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              No disaster analysis jobs with valid latitude and longitude coordinates were found. Defaulting to world view.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
